"""Adversarial tests for Step 2: EmbeddingStore"""

import pytest
import numpy as np
from unittest.mock import patch
from ai.embeddings.store import EmbeddingStore, _VECTOR_DIM


def _make_store():
    """테스트용 스토어 생성"""
    return EmbeddingStore()


def _rand_vec():
    """정규화된 384차원 벡터 생성"""
    v = np.random.randn(_VECTOR_DIM).astype(np.float32)
    return v / np.linalg.norm(v)


class TestEmbeddingStoreInputValidation:
    """EmbeddingStore 입력 검증"""

    def test_add_non_normalized_vector_rejected(self):
        """정규화되지 않은 벡터는 거부되어야 함"""
        store = _make_store()
        non_normalized = np.ones(_VECTOR_DIM, dtype=np.float32)  # norm ≈ 19.6

        meta = {"user_id": "u1", "category": "test", "text": "task", "completed": False}
        with pytest.raises(ValueError, match="정규화"):
            store.add("todo-1", non_normalized, meta)

    def test_add_nan_vector_rejected(self):
        """NaN이 포함된 벡터는 거부되어야 함"""
        store = _make_store()
        vec_with_nan = np.ones(_VECTOR_DIM, dtype=np.float32)
        vec_with_nan[0] = np.nan

        meta = {"user_id": "u1", "category": "test", "text": "task", "completed": False}
        with pytest.raises(ValueError, match="NaN"):
            store.add("todo-1", vec_with_nan, meta)

    def test_add_inf_vector_rejected(self):
        """Inf가 포함된 벡터는 거부되어야 함"""
        store = _make_store()
        vec_with_inf = np.ones(_VECTOR_DIM, dtype=np.float32)
        vec_with_inf[0] = np.inf

        meta = {"user_id": "u1", "category": "test", "text": "task", "completed": False}
        with pytest.raises(ValueError, match="NaN|Inf"):
            store.add("todo-1", vec_with_inf, meta)

    def test_add_wrong_dimension_vector_rejected(self):
        """잘못된 차원 벡터는 거부되어야 함"""
        store = _make_store()
        wrong_dim = np.ones(100, dtype=np.float32)
        wrong_dim = wrong_dim / np.linalg.norm(wrong_dim)

        meta = {"user_id": "u1", "category": "test", "text": "task", "completed": False}
        with pytest.raises(ValueError, match="차원"):
            store.add("todo-1", wrong_dim, meta)

    def test_add_duplicate_todo_id_rejected(self):
        """중복 todo_id는 거부되어야 함"""
        store = _make_store()
        vec = _rand_vec()
        meta = {"user_id": "u1", "category": "test", "text": "task", "completed": False}

        store.add("todo-1", vec, meta)
        with pytest.raises(ValueError, match="이미"):
            store.add("todo-1", vec, meta)

    def test_search_empty_store(self):
        """빈 스토어에서 search는 []를 반환해야 함"""
        store = _make_store()
        result = store.search(_rand_vec(), top_k=5)
        assert result == []

    def test_search_returns_top_k_limit(self):
        """search는 top_k 개수를 초과하지 않아야 함"""
        store = _make_store()
        for i in range(10):
            store.add(f"todo-{i}", _rand_vec(), 
                     {"user_id": "u1", "category": "test", "text": f"task{i}", "completed": False})

        result = store.search(_rand_vec(), top_k=3)
        assert len(result) <= 3


class TestEmbeddingStoreDataIntegrity:
    """EmbeddingStore 데이터 무결성"""

    def test_rebuild_preserves_normalization(self):
        """rebuild() 후 벡터 정규화가 유지되어야 함"""
        store = _make_store()
        vec = _rand_vec()
        meta = {"user_id": "u1", "category": "test", "text": "task", "completed": False}

        store.add("todo-1", vec, meta)
        store.rebuild()

        assert len(store._metadata) == 1
        restored_vec = np.array(store._metadata[0]["_vec"], dtype=np.float32)
        norm = np.linalg.norm(restored_vec)
        assert np.isclose(norm, 1.0, atol=1e-5), f"norm={norm} after rebuild"

    def test_delete_soft_then_rebuild_hard(self):
        """delete는 soft delete, rebuild는 hard delete"""
        store = _make_store()
        vec = _rand_vec()
        meta = {"user_id": "u1", "category": "test", "text": "task", "completed": False}

        store.add("todo-1", vec, meta)
        store.delete("todo-1")
        
        # soft delete 후 인덱스 크기 변화 없음
        assert store._index.ntotal == 1
        
        # rebuild 후 인덱스 크기 0
        store.rebuild()
        assert store._index.ntotal == 0
        assert len(store._metadata) == 0

    def test_update_cycles(self):
        """add/update 사이클이 일관성을 유지해야 함"""
        store = _make_store()
        vec = _rand_vec()
        meta1 = {"user_id": "u1", "category": "test", "text": "task1", "completed": False}
        meta2 = {"user_id": "u1", "category": "test", "text": "task2", "completed": True}

        store.add("todo-1", vec, meta1)
        store.update("todo-1", vec, meta2)

        # soft delete 후 새 항목 추가 → 2개 항목
        assert store._index.ntotal == 2

        store.rebuild()
        # rebuild 후 active 항목만 남음
        assert store._index.ntotal == 1
        assert store._metadata[0]["text"] == "task2"
