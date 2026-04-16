import json
from pathlib import Path

import faiss
import numpy as np

from ai.core.config import settings

'''FAISS 기반 임베딩 벡터 저장소(EmbeddingStore) : 임베딩, 유사도 검색, soft delete, 디스크 영속화'''

# 임베딩 모델 고정 출력 차원
_VECTOR_DIM = settings.VECTOR_DIM

# ai/ 패키지 루트 (store.py 위치 기준 2단계 상위)
_AI_DIR = Path(__file__).resolve().parent.parent


class EmbeddingStore:
    '''
    faiss IndexFlatIP 인덱스와 메타데이터를 함께 관리하는 벡터 스토어.
    GPU 사용 가능하면 GpuIndexFlatIP로 실행 / 없으면 CPU 인덱스로 폴백.

    faiss 인덱스의 i번째 행과 _metadata[i]가 1:1 대응
    삭제는 soft delete(is_deleted 플래그)로 처리하고, rebuild() 호출 시에만 물리적으로 제거
    '''

    def __init__(self) -> None:
        # GPU 사용 가능 여부 확인
        self._gpu_available: bool = faiss.get_num_gpus() > 0
        self._res: faiss.StandardGpuResources | None = (
            faiss.StandardGpuResources() if self._gpu_available else None
        )
        self._index: faiss.Index = self._to_gpu(faiss.IndexFlatIP(_VECTOR_DIM))
        # 각 항목: todo_id, user_id, category, text, completed, is_deleted, _vec
        self._metadata: list[dict] = []   # 메타데이터 리스트 생성

    # CPU 인덱스 → GPU 인덱스 변환 (GPU 없으면 그대로 반환)
    def _to_gpu(self, cpu_index: faiss.Index) -> faiss.Index:
        if self._gpu_available and self._res is not None:
            return faiss.index_cpu_to_gpu(self._res, 0, cpu_index)
        return cpu_index

    # GPU 인덱스 → CPU 인덱스 변환 (디스크 저장 전 필수)
    def _to_cpu(self) -> faiss.Index:
        if self._gpu_available:
            return faiss.index_gpu_to_cpu(self._index)
        return self._index

    
    ########## 경로 헬퍼 ##########

    @staticmethod
    def _index_path() -> Path:
        return _AI_DIR / settings.FAISS_INDEX_PATH

    @staticmethod
    def _metadata_path() -> Path:
        return _AI_DIR / settings.FAISS_METADATA_PATH


    ########## 입력 검증 ##########

    def _validate_vec(self, vec: np.ndarray) -> None:
        '''벡터 차원, NaN/Inf, L2 정규화 검증'''
        if vec.shape != (_VECTOR_DIM,):
            raise ValueError(f"벡터 차원 불일치: 기대 ({_VECTOR_DIM},), 실제 {vec.shape}")
        if not np.isfinite(vec).all():
            raise ValueError("벡터에 NaN 또는 Inf 값 포함")
        # IndexFlatIP는 L2 정규화 벡터를 가정 — norm ≠ 1이면 내적 ≠ cosine similarity
        norm = float(np.linalg.norm(vec))
        if not np.isclose(norm, 1.0, atol=1e-5):   # float32 정밀도 오차 허용 범위 (~1e-7), 임베딩 연산 누적 오차 고려
            raise ValueError(f"벡터가 정규화되지 않음: norm={norm:.4f}")

    ########## CRUD ##########

    # todo 생성 : 벡터 + 메타데이터 추가
    def add(self, todo_id: str, vec: np.ndarray, meta: dict) -> None:
        # 중복 todo_id 방지 (active 항목 기준)
        if any(m["todo_id"] == todo_id and not m["is_deleted"] for m in self._metadata):
            raise ValueError(f"todo_id '{todo_id}' 이미 존재")
        self._validate_vec(vec)

        # 메타 정보 패킹
        row: dict = {
            "todo_id": todo_id,
            **meta,
            "is_deleted": False,
            "_vec": vec.tolist(),  # JSON 직렬화 및 rebuild 재구축용
        }

        # FAISS(2차원 벡터로 변환해서), metadata에 추가
        self._index.add(vec.reshape((1, -1)))  # type: ignore[call-arg]
        self._metadata.append(row)

    # todo 삭제 (soft delete) — 동일 todo_id의 모든 active 항목 처리
    def delete(self, todo_id: str) -> None:
        for row in self._metadata:
            if row["todo_id"] == todo_id and not row["is_deleted"]:
                row["is_deleted"] = True

    # todo 수정 : 기존 항목 삭제 후 새 벡터/메타데이터 추가
    def update(self, todo_id: str, new_vec: np.ndarray, new_meta: dict) -> None:
        self.delete(todo_id)
        self.add(todo_id, new_vec, new_meta)

    # 유사 todo top-k 검색 : cosine similarity 기준 top-k 검색. is_deleted=True 항목 제외
    def search(self, query_vec: np.ndarray, top_k: int) -> list[dict]:
        """
        정규화된 벡터 + IndexFlatIP → 내적 = cosine similarity.
        전체 인덱스를 검색한 뒤 삭제 항목을 필터링해 top_k 반환.
        """
        # 빈 벡터 저장소 제외
        if self._index.ntotal == 0:
            return []

        # 삭제된 항목을 제외하기 위해 전체 인덱스 검색 후 필터링
        scores, indices = self._index.search(  # type: ignore[call-arg]
            query_vec.reshape((1, -1)), self._index.ntotal
        )

        active_set: set[int] = {
            i for i, m in enumerate(self._metadata) if not m["is_deleted"]
        }

        # cosine similarity 기반 top_k 검색
        results: list[dict] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or idx not in active_set:
                continue
            entry = {k: v for k, v in self._metadata[idx].items() if k != "_vec"}
            entry["score"] = float(score)
            results.append(entry)
            if len(results) >= top_k:
                break

        return results


    ########## 인덱스 유지보수 ##########

    # soft delele 데이터 실제 제거 + faiss 인덱스 재구축
    def rebuild(self) -> None:
        active = [m for m in self._metadata if not m["is_deleted"]]
        cpu_index: faiss.Index = faiss.IndexFlatIP(_VECTOR_DIM)
        if active:
            vecs = np.array([m["_vec"] for m in active], dtype=np.float32)
            cpu_index.add(vecs)  # type: ignore[call-arg]
        self._index = self._to_gpu(cpu_index)
        self._metadata = active


    ########## 영구 저장 ##########

    # index.faiss + metadata.json 디스크 저장
    # faiss.write_index는 CPU 인덱스만 지원하므로 GPU → CPU 변환 후 저장
    def save(self) -> None:
        idx_path = self._index_path()
        meta_path = self._metadata_path()

        idx_path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self._to_cpu(), str(idx_path))
        meta_path.write_text(
            json.dumps(self._metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # 디스크에서 인덱스와 메타데이터 로드 (파일 없으면 빈 상태로 시작)
    # 로드 후 GPU로 이동 / 서버 시작 시 호출
    def load(self) -> None:
        idx_path = self._index_path()
        meta_path = self._metadata_path()
        
        if idx_path.exists() and meta_path.exists():
            cpu_index = faiss.read_index(str(idx_path))
            self._index = self._to_gpu(cpu_index)
            self._metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        else:
            self._index = self._to_gpu(faiss.IndexFlatIP(_VECTOR_DIM))
            self._metadata = []
