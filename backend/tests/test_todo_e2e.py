"""todo 생성·수정·삭제 e2e 테스트.

실제 DB: SQLite in-memory (conftest.py)
AI 서버: unittest.mock으로 대체
"""
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

MOCK_INTERFERENCE = {
    "global_rate": 60.0,
    "personal_rate": 50.0,
    "similar_count": 3,
    "feedback": "지난번에도 비슷한 목표를 세웠는데, 이번엔 꼭 해내세요!",
    "similar_failures": ["운동하기", "공부하기"],
}

_AI_PATHS = {
    "get_interference": "app.services.todo.get_interference",
    "update_embedding": "app.services.todo.update_embedding",
    "patch_embedding":  "app.services.todo.patch_embedding",
    "delete_embedding": "app.services.todo.delete_embedding",
}


@pytest.fixture(autouse=True)
def mock_ai_calls():
    """모든 테스트에서 AI 서버 호출을 mock으로 대체."""
    with (
        patch(_AI_PATHS["get_interference"], new_callable=AsyncMock, return_value=MOCK_INTERFERENCE),
        patch(_AI_PATHS["update_embedding"], new_callable=AsyncMock),
        patch(_AI_PATHS["patch_embedding"],  new_callable=AsyncMock),
        patch(_AI_PATHS["delete_embedding"], new_callable=AsyncMock),
    ):
        yield


# ─── 헬퍼 ────────────────────────────────────────────────────────────────────

async def _create_todo(client: AsyncClient, user_id: int, **overrides) -> dict:
    payload = {
        "title":       "원래 제목",
        "detail":      "원래 상세",
        "category_id": "study",
        "user_id":     user_id,
        "todo_status": "시작전",
        "visibility":  "친구공개",
        **overrides,
    }
    resp = await client.post("/todos/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ─── 생성(C) ──────────────────────────────────────────────────────────────────

async def test_create_success(client: AsyncClient, test_user):
    resp = await client.post("/todos/", json={
        "title":       "오늘의 운동",
        "detail":      "30분 달리기",
        "category_id": "workout",
        "user_id":     test_user.user_id,
        "todo_status": "시작전",
        "visibility":  "친구공개",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "오늘의 운동"
    assert data["user_id"] == test_user.user_id
    assert "todo_id" in data
    assert data["interference"]["feedback"] == MOCK_INTERFERENCE["feedback"]


async def test_create_user_not_found(client: AsyncClient):
    resp = await client.post("/todos/", json={
        "title":       "할 일",
        "detail":      "",
        "category_id": "study",
        "user_id":     9999,
        "todo_status": "시작전",
        "visibility":  "친구공개",
    })
    assert resp.status_code == 404
    assert "9999" in resp.json()["detail"]


async def test_create_category_not_found(client: AsyncClient, test_user):
    resp = await client.post("/todos/", json={
        "title":       "할 일",
        "detail":      "",
        "category_id": "nonexistent_cat",
        "user_id":     test_user.user_id,
        "todo_status": "시작전",
        "visibility":  "친구공개",
    })
    assert resp.status_code == 404
    assert "nonexistent_cat" in resp.json()["detail"]


async def test_create_ai_failure_still_returns_201(client: AsyncClient, test_user):
    """AI 서버 실패 시에도 todo 생성은 성공하고 interference는 None."""
    with patch(_AI_PATHS["get_interference"], new_callable=AsyncMock, return_value=None):
        resp = await client.post("/todos/", json={
            "title":       "공부하기",
            "detail":      "",
            "category_id": "study",
            "user_id":     test_user.user_id,
            "todo_status": "시작전",
            "visibility":  "친구공개",
        })
        assert resp.status_code == 201
        assert resp.json()["interference"] is None


# ─── 조회(R) ──────────────────────────────────────────────────────────────────

async def test_get_single_todo(client: AsyncClient, test_user):
    todo = await _create_todo(client, test_user.user_id, title="독서")
    resp = await client.get(f"/todos/{todo['todo_id']}")
    assert resp.status_code == 200
    assert resp.json()["todo_id"] == todo["todo_id"]


async def test_get_todo_not_found(client: AsyncClient):
    resp = await client.get("/todos/does-not-exist")
    assert resp.status_code == 404


async def test_get_todos_by_user(client: AsyncClient, test_user):
    for i in range(3):
        await _create_todo(client, test_user.user_id, title=f"할 일 {i}", category_id="work")
    resp = await client.get(f"/todos/user/{test_user.user_id}")
    assert resp.status_code == 200
    assert len(resp.json()) >= 3


async def test_get_todos_user_not_found(client: AsyncClient):
    resp = await client.get("/todos/user/9999")
    assert resp.status_code == 404


# ─── 수정(U) ──────────────────────────────────────────────────────────────────

async def test_update_title_calls_update_embedding(client: AsyncClient, test_user):
    todo = await _create_todo(client, test_user.user_id)
    with patch(_AI_PATHS["update_embedding"], new_callable=AsyncMock) as mock_update:
        resp = await client.patch(f"/todos/{todo['todo_id']}", json={"title": "수정된 제목"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "수정된 제목"
        mock_update.assert_called_once()


async def test_update_same_title_no_update_embedding(client: AsyncClient, test_user):
    """제목이 변경되지 않으면 update_embedding 미호출."""
    todo = await _create_todo(client, test_user.user_id, title="같은 제목")
    with patch(_AI_PATHS["update_embedding"], new_callable=AsyncMock) as mock_update:
        resp = await client.patch(f"/todos/{todo['todo_id']}", json={"title": "같은 제목"})
        assert resp.status_code == 200
        mock_update.assert_not_called()


async def test_update_status_calls_patch_embedding(client: AsyncClient, test_user):
    todo = await _create_todo(client, test_user.user_id)
    with patch(_AI_PATHS["patch_embedding"], new_callable=AsyncMock) as mock_patch:
        resp = await client.patch(f"/todos/{todo['todo_id']}", json={"todo_status": "완료"})
        assert resp.status_code == 200
        assert resp.json()["todo_status"] == "완료"
        mock_patch.assert_called_once()


async def test_update_category_calls_patch_embedding(client: AsyncClient, test_user):
    todo = await _create_todo(client, test_user.user_id)
    with patch(_AI_PATHS["patch_embedding"], new_callable=AsyncMock) as mock_patch:
        resp = await client.patch(f"/todos/{todo['todo_id']}", json={"category_id": "workout"})
        assert resp.status_code == 200
        mock_patch.assert_called_once()


async def test_update_detail_only_no_ai_call(client: AsyncClient, test_user):
    """제목·상태·카테고리 변경 없이 detail만 수정하면 AI 호출 없음."""
    todo = await _create_todo(client, test_user.user_id)
    with (
        patch(_AI_PATHS["update_embedding"], new_callable=AsyncMock) as mu,
        patch(_AI_PATHS["patch_embedding"],  new_callable=AsyncMock) as mp,
    ):
        resp = await client.patch(f"/todos/{todo['todo_id']}", json={"detail": "수정된 상세 내용"})
        assert resp.status_code == 200
        mu.assert_not_called()
        mp.assert_not_called()


async def test_update_not_found(client: AsyncClient):
    resp = await client.patch("/todos/does-not-exist", json={"title": "새 제목"})
    assert resp.status_code == 404


async def test_update_invalid_category(client: AsyncClient, test_user):
    todo = await _create_todo(client, test_user.user_id)
    resp = await client.patch(f"/todos/{todo['todo_id']}", json={"category_id": "invalid_cat"})
    assert resp.status_code == 404


# ─── 삭제(D) ──────────────────────────────────────────────────────────────────

async def test_delete_success_and_calls_delete_embedding(client: AsyncClient, test_user):
    todo = await _create_todo(client, test_user.user_id, title="삭제할 todo")
    todo_id = todo["todo_id"]
    with patch(_AI_PATHS["delete_embedding"], new_callable=AsyncMock) as mock_del:
        resp = await client.delete(f"/todos/{todo_id}")
        assert resp.status_code == 200
        assert todo_id in resp.json()["message"]
        mock_del.assert_called_once_with(todo_id=todo_id)


async def test_delete_then_get_returns_404(client: AsyncClient, test_user):
    todo = await _create_todo(client, test_user.user_id, title="삭제 후 조회")
    todo_id = todo["todo_id"]
    await client.delete(f"/todos/{todo_id}")
    assert (await client.get(f"/todos/{todo_id}")).status_code == 404


async def test_delete_not_found(client: AsyncClient):
    resp = await client.delete("/todos/does-not-exist")
    assert resp.status_code == 404
