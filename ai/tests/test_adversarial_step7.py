"""
Step 7 FastAPI 라우터 Adversarial Test Suite
테스트 범위:
- DELETE/PUT 엔드포인트의 비존재 항목 처리
- 벡터 정규화 검증
- 입력 검증
"""

import pytest
import numpy as np
from unittest.mock import patch
from fastapi.testclient import TestClient

from ai.main import app
from ai.embeddings.store import EmbeddingStore
from ai.embeddings.model import EmbeddingModel
from ai.core.dependencies import get_embedding_model, get_embedding_store


class MockEmbeddingStore(EmbeddingStore):
    def __init__(self):
        super().__init__()
        self.save_called = False
    
    def save(self) -> None:
        self.save_called = True


class MockEmbeddingModel(EmbeddingModel):
    def __init__(self):
        self._model = None
    
    def encode(self, text: str) -> np.ndarray:
        return np.ones(384, dtype=np.float32)
    
    def encode_passage(self, text: str) -> np.ndarray:
        vec = np.ones(384, dtype=np.float32)
        return vec / np.linalg.norm(vec)


@pytest.fixture
def mock_store():
    return MockEmbeddingStore()


@pytest.fixture
def mock_model():
    return MockEmbeddingModel()


@pytest.fixture
def client(mock_store, mock_model):
    app.dependency_overrides[get_embedding_store] = lambda: mock_store
    app.dependency_overrides[get_embedding_model] = lambda: mock_model
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


class TestDeleteNonexistent:
    """CRITICAL #1: DELETE 존재하지 않는 todo_id"""
    
    def test_delete_nonexistent_returns_200_silent_failure(self, client, mock_store):
        """존재하지 않는 todo 삭제 시 200 반환 (사일런트 팰리어)"""
        assert len(mock_store._metadata) == 0
        
        response = client.delete("/ai/embeddings/todo/nonexistent-id")
        
        assert response.status_code == 200
        assert response.json()["deleted"] is True
        assert len(mock_store._metadata) == 0  # 실제로 아무것도 안 함


class TestPutNonexistent:
    """HIGH #5: PUT 존재하지 않는 todo_id"""
    
    def test_put_nonexistent_creates_instead_of_update(self, client, mock_store):
        """PUT이 없는 항목도 create (REST 의미론 위반)"""
        response = client.put(
            "/ai/embeddings/todo/nonexistent-id",
            json={
                "user_id": "user-1",
                "category": "work",
                "text": "modified",
                "completed": True
            }
        )
        
        assert response.status_code == 200
        assert len(mock_store._metadata) == 1  # create됨!


class TestPostDuplicate:
    """CRITICAL #3: POST 중복 todo_id"""
    
    def test_duplicate_returns_409(self, client, mock_store):
        """중복 todo_id 시 409"""
        response1 = client.post(
            "/ai/embeddings/todo",
            json={
                "todo_id": "todo-dup",
                "user_id": "user-1",
                "category": "work",
                "text": "task",
                "completed": True
            }
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            "/ai/embeddings/todo",
            json={
                "todo_id": "todo-dup",
                "user_id": "user-1",
                "category": "work",
                "text": "task",
                "completed": True
            }
        )
        
        assert response2.status_code == 409


class TestVectorValidation:
    """벡터 검증 - 정규화, NaN, Inf"""
    
    def test_non_normalized_vector_rejected(self, client, mock_store, mock_model):
        """비정규화 벡터 거부"""
        mock_model.encode_passage = lambda x: np.ones(384, dtype=np.float32) * 2
        
        response = client.post(
            "/ai/embeddings/todo",
            json={
                "todo_id": "todo-1",
                "user_id": "user-1",
                "category": "work",
                "text": "task",
                "completed": True
            }
        )
        
        assert response.status_code == 422
    
    def test_nan_vector_rejected(self, client, mock_store, mock_model):
        """NaN 벡터 거부"""
        vec = np.ones(384, dtype=np.float32)
        vec[0] = np.nan
        mock_model.encode_passage = lambda x: vec
        
        response = client.post(
            "/ai/embeddings/todo",
            json={
                "todo_id": "todo-1",
                "user_id": "user-1",
                "category": "work",
                "text": "task",
                "completed": True
            }
        )
        
        assert response.status_code == 422


class TestInputValidation:
    """입력 검증"""
    
    def test_empty_todo_id(self, client):
        response = client.post(
            "/ai/embeddings/todo",
            json={
                "todo_id": "",
                "user_id": "user-1",
                "category": "work",
                "text": "task",
                "completed": True
            }
        )
        assert response.status_code == 422
    
    def test_empty_text(self, client):
        response = client.post(
            "/ai/embeddings/todo",
            json={
                "todo_id": "todo-1",
                "user_id": "user-1",
                "category": "work",
                "text": "",
                "completed": True
            }
        )
        assert response.status_code == 422


class TestHealthCheck:
    """GET /health"""
    
    def test_health_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
