"""Step 2 완료 조건 검증 테스트.

완료 조건:
1. add → search → 결과 반환 정상 동작
2. delete 후 search 결과에서 제외 확인
3. save → load 후 동일 데이터 복원
4. rebuild 후 is_deleted 항목 완전 제거 확인
"""
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from ai.embeddings.store import EmbeddingStore, _VECTOR_DIM


# ── 픽스처 ──────────────────────────────────────────────────────────────────────

def _make_store(tmp_path: Path) -> EmbeddingStore:
    """임시 경로를 사용하는 EmbeddingStore 인스턴스 반환."""
    idx_path = str(tmp_path / "index.faiss")
    meta_path = str(tmp_path / "metadata.json")
    with (
        patch("ai.embeddings.store.settings") as mock_settings,
    ):
        mock_settings.FAISS_INDEX_PATH = "index.faiss"
        mock_settings.FAISS_METADATA_PATH = "metadata.json"
        # _AI_DIR 패치: 임시 디렉터리를 루트로 사용
        with patch("ai.embeddings.store._AI_DIR", tmp_path):
            return EmbeddingStore()


def _rand_vec() -> np.ndarray:
    """정규화된 무작위 384차원 벡터 생성."""
    v = np.random.randn(_VECTOR_DIM).astype(np.float32)
    return v / np.linalg.norm(v)


def _meta(text: str = "운동하기") -> dict:
    return {"user_id": "u1", "category": "health", "text": text, "completed": False}


# ── 1. add → search ──────────────────────────────────────────────────────────────

def test_add_and_search(tmp_path):
    """add 후 search 결과에 해당 항목이 포함되어야 한다."""
    with patch("ai.embeddings.store._AI_DIR", tmp_path):
        store = EmbeddingStore()
        vec = _rand_vec()
        store.add("todo-1", vec, _meta("운동하기"))

        results = store.search(vec, top_k=5)
        assert len(results) == 1
        assert results[0]["todo_id"] == "todo-1"
        assert results[0]["text"] == "운동하기"
        # cosine similarity: 동일 벡터이므로 score ≈ 1.0
        assert results[0]["score"] == pytest.approx(1.0, abs=1e-5)


def test_search_returns_top_k(tmp_path):
    """top_k 개수만큼만 반환해야 한다."""
    with patch("ai.embeddings.store._AI_DIR", tmp_path):
        store = EmbeddingStore()
        for i in range(5):
            store.add(f"todo-{i}", _rand_vec(), _meta(f"task {i}"))

        results = store.search(_rand_vec(), top_k=3)
        assert len(results) <= 3


def test_search_empty_store(tmp_path):
    """빈 스토어에서 search는 빈 리스트를 반환해야 한다."""
    with patch("ai.embeddings.store._AI_DIR", tmp_path):
        store = EmbeddingStore()
        assert store.search(_rand_vec(), top_k=5) == []


# ── 2. delete 후 search 제외 ──────────────────────────────────────────────────

def test_delete_excludes_from_search(tmp_path):
    """delete 후 search 결과에서 해당 항목이 제외되어야 한다."""
    with patch("ai.embeddings.store._AI_DIR", tmp_path):
        store = EmbeddingStore()
        vec = _rand_vec()
        store.add("todo-1", vec, _meta("운동하기"))
        store.add("todo-2", _rand_vec(), _meta("독서하기"))

        store.delete("todo-1")
        results = store.search(vec, top_k=5)
        ids = [r["todo_id"] for r in results]
        assert "todo-1" not in ids
        assert "todo-2" in ids


def test_delete_nonexistent_is_safe(tmp_path):
    """존재하지 않는 todo_id 삭제 시 오류 없이 처리되어야 한다."""
    with patch("ai.embeddings.store._AI_DIR", tmp_path):
        store = EmbeddingStore()
        store.delete("nonexistent")  # 예외 없이 통과


# ── 3. save → load 복원 ───────────────────────────────────────────────────────

def test_save_and_load(tmp_path):
    """save 후 load 시 동일 데이터가 복원되어야 한다."""
    with patch("ai.embeddings.store._AI_DIR", tmp_path):
        store1 = EmbeddingStore()
        vec = _rand_vec()
        store1.add("todo-1", vec, _meta("운동하기"))
        store1.save()

        store2 = EmbeddingStore()
        store2.load()

        # 메타데이터 복원 확인
        assert len(store2._metadata) == 1
        assert store2._metadata[0]["todo_id"] == "todo-1"
        assert store2._metadata[0]["text"] == "운동하기"

        # 검색 동작 확인
        results = store2.search(vec, top_k=1)
        assert len(results) == 1
        assert results[0]["todo_id"] == "todo-1"


def test_load_without_files(tmp_path):
    """파일 없이 load 호출 시 빈 상태로 시작되어야 한다."""
    with patch("ai.embeddings.store._AI_DIR", tmp_path):
        store = EmbeddingStore()
        store.load()  # 파일 없음
        assert store._index.ntotal == 0
        assert store._metadata == []


# ── 4. rebuild 후 is_deleted 완전 제거 ───────────────────────────────────────

def test_rebuild_removes_deleted(tmp_path):
    """rebuild 후 is_deleted 항목이 인덱스와 메타데이터에서 완전히 제거되어야 한다."""
    with patch("ai.embeddings.store._AI_DIR", tmp_path):
        store = EmbeddingStore()
        store.add("todo-1", _rand_vec(), _meta("운동하기"))
        store.add("todo-2", _rand_vec(), _meta("독서하기"))
        store.delete("todo-1")

        assert store._index.ntotal == 2  # soft delete: 벡터는 유지
        store.rebuild()

        # 물리적 제거 확인
        assert store._index.ntotal == 1
        assert len(store._metadata) == 1
        assert store._metadata[0]["todo_id"] == "todo-2"
        assert all(not m["is_deleted"] for m in store._metadata)


def test_rebuild_all_deleted(tmp_path):
    """모든 항목이 삭제된 후 rebuild 시 빈 인덱스가 되어야 한다."""
    with patch("ai.embeddings.store._AI_DIR", tmp_path):
        store = EmbeddingStore()
        store.add("todo-1", _rand_vec(), _meta("운동하기"))
        store.delete("todo-1")
        store.rebuild()

        assert store._index.ntotal == 0
        assert store._metadata == []


# ── update 통합 ───────────────────────────────────────────────────────────────

def test_update(tmp_path):
    """update 후 이전 텍스트는 검색되지 않고 새 텍스트 메타데이터가 반환되어야 한다."""
    with patch("ai.embeddings.store._AI_DIR", tmp_path):
        store = EmbeddingStore()
        old_vec = _rand_vec()
        new_vec = _rand_vec()
        store.add("todo-1", old_vec, _meta("운동하기"))
        store.update("todo-1", new_vec, _meta("수영하기"))

        results = store.search(new_vec, top_k=5)
        active = [r for r in results if r["todo_id"] == "todo-1"]
        assert len(active) == 1
        assert active[0]["text"] == "수영하기"
