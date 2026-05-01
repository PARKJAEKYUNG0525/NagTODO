"""Todo CRUD 적대적 e2e 테스트.

이 파일의 테스트는 현재 구현의 버그/취약점을 드러내기 위해 설계되었습니다.
xfail로 표시된 테스트는 "현재는 통과하지만 실제로는 버그"를 의미합니다.
"""
from unittest.mock import AsyncMock, patch, call

import pytest
from datetime import date
from httpx import AsyncClient

MOCK_INTERFERENCE = {
    "global_rate": 60.0,
    "personal_rate": 50.0,
    "similar_count": 3,
    "feedback": "피드백",
    "similar_failures": [],
}

_AI = {
    "get_interference": "app.services.todo.get_interference",
    "update_embedding": "app.services.todo.update_embedding",
    "patch_embedding":  "app.services.todo.patch_embedding",
    "delete_embedding": "app.services.todo.delete_embedding",
}


@pytest.fixture(autouse=True)
def mock_ai():
    with (
        patch(_AI["get_interference"], new_callable=AsyncMock, return_value=MOCK_INTERFERENCE),
        patch(_AI["update_embedding"], new_callable=AsyncMock),
        patch(_AI["patch_embedding"],  new_callable=AsyncMock),
        patch(_AI["delete_embedding"], new_callable=AsyncMock),
    ):
        yield


# ─── 헬퍼 ────────────────────────────────────────────────────────────────────

async def _create(client, user_id: int, **kw) -> dict:
    resp = await client.post("/todos/", json={
        "title": "기본 제목", "detail": "상세", "category_id": "study",
        "user_id": user_id, "todo_status": "시작전", "visibility": "친구공개",
        **kw,
    })
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture
async def second_user(db_session):
    """두 번째 테스트 유저."""
    from app.db.models.user import User
    user = User(
        email="other@nagtodo.com",
        pw="hashed",
        username="다른유저",
        birthday=date(1990, 1, 1),
        state=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ─── CRITICAL-1: 소유권 변경 공격 ────────────────────────────────────────────

@pytest.mark.xfail(reason="CRITICAL-1: 소유권 검증 없음 — user_id 변경으로 todo 탈취 가능", strict=True)
async def test_cannot_change_todo_owner(client: AsyncClient, test_user, second_user):
    """유저 B의 todo를 유저 A의 소유로 변경 요청 → 403 이어야 하지만 현재 200 반환."""
    todo = await _create(client, test_user.user_id, title="유저A의 todo")
    resp = await client.patch(
        f"/todos/{todo['todo_id']}",
        json={"user_id": second_user.user_id},
    )
    assert resp.status_code == 403, f"소유권 탈취 가능: {resp.status_code}"


async def test_owner_change_currently_succeeds(client: AsyncClient, test_user, second_user):
    """현재 구현에서 user_id 변경이 실제로 200 반환됨을 증명 (버그 확인)."""
    todo = await _create(client, test_user.user_id)
    resp = await client.patch(
        f"/todos/{todo['todo_id']}",
        json={"user_id": second_user.user_id},
    )
    # 버그: 200이 반환됨 (owner 변경 성공)
    assert resp.status_code == 200
    assert resp.json()["user_id"] == second_user.user_id  # 소유자가 바뀌었음


# ─── CRITICAL-2: 빈 제목 허용 ─────────────────────────────────────────────────

@pytest.mark.xfail(reason="CRITICAL-2: title min_length 검증 없음 — 빈 제목 허용", strict=True)
async def test_create_empty_title_rejected(client: AsyncClient, test_user):
    """빈 제목으로 생성 → 422 이어야 하지만 현재 201 반환."""
    resp = await client.post("/todos/", json={
        "title": "", "detail": "상세", "category_id": "study",
        "user_id": test_user.user_id, "todo_status": "시작전", "visibility": "친구공개",
    })
    assert resp.status_code == 422, f"빈 제목으로 생성됨: {resp.status_code}"


async def test_empty_title_currently_creates(client: AsyncClient, test_user):
    """현재 빈 제목 생성이 성공함을 증명 (버그 확인)."""
    resp = await client.post("/todos/", json={
        "title": "", "detail": "상세", "category_id": "study",
        "user_id": test_user.user_id, "todo_status": "시작전", "visibility": "친구공개",
    })
    assert resp.status_code == 201  # 버그: 빈 제목이 DB에 저장됨
    assert resp.json()["title"] == ""


@pytest.mark.xfail(reason="CRITICAL-2: title min_length 검증 없음 — 빈 제목으로 수정 허용", strict=True)
async def test_update_empty_title_rejected(client: AsyncClient, test_user):
    """빈 제목으로 수정 → 422 이어야 하지만 현재 200 반환."""
    todo = await _create(client, test_user.user_id)
    resp = await client.patch(f"/todos/{todo['todo_id']}", json={"title": ""})
    assert resp.status_code == 422, f"빈 제목으로 수정됨: {resp.status_code}"


async def test_empty_title_update_currently_succeeds(client: AsyncClient, test_user):
    """현재 빈 제목 수정이 성공함을 증명 (버그 확인)."""
    todo = await _create(client, test_user.user_id)
    resp = await client.patch(f"/todos/{todo['todo_id']}", json={"title": ""})
    # 빈 제목은 update_embedding을 호출하지 않음 (old_title != "")
    assert resp.status_code == 200
    assert resp.json()["title"] == ""


# ─── CRITICAL-3: 유효하지 않은 ENUM 값 허용 (SQLite 환경) ────────────────────

@pytest.mark.xfail(
    reason="CRITICAL-3: Pydantic ENUM 검증 없음 — SQLite에서 잘못된 status 값 허용",
    strict=True,
)
async def test_invalid_todo_status_rejected(client: AsyncClient, test_user):
    """잘못된 todo_status → 422 이어야 하지만 SQLite에서는 201 반환."""
    resp = await client.post("/todos/", json={
        "title": "할 일", "detail": "", "category_id": "study",
        "user_id": test_user.user_id,
        "todo_status": "완전히_틀린_상태",  # ENUM 외 값
        "visibility": "친구공개",
    })
    assert resp.status_code == 422, f"잘못된 status가 허용됨: {resp.status_code}"


async def test_invalid_todo_status_returns_db_error_not_pydantic(client: AsyncClient, test_user):
    """잘못된 todo_status는 Pydantic 422가 아닌 DB 레벨 400을 반환함을 증명 (버그 확인).

    올바른 동작: Pydantic 422 (스키마 레벨 검증)
    현재 동작: SQLAlchemy CHECK 제약 위반 → 400 (서비스의 except Exception 포착)
    """
    resp = await client.post("/todos/", json={
        "title": "할 일", "detail": "", "category_id": "study",
        "user_id": test_user.user_id,
        "todo_status": "완전히_틀린_상태",
        "visibility": "친구공개",
    })
    # 버그: 400 반환 (Pydantic 검증이 아닌 DB 오류)
    # 올바른 동작이라면 422여야 함
    assert resp.status_code == 400
    assert resp.json()["detail"] == "todo 생성에 실패했습니다."


@pytest.mark.xfail(
    reason="CRITICAL-3: Pydantic ENUM 검증 없음 — 잘못된 visibility 허용",
    strict=True,
)
async def test_invalid_visibility_rejected(client: AsyncClient, test_user):
    resp = await client.post("/todos/", json={
        "title": "할 일", "detail": "", "category_id": "study",
        "user_id": test_user.user_id, "todo_status": "시작전",
        "visibility": "전체공개",  # "친구공개"/"비공개"만 유효
    })
    assert resp.status_code == 422


# ─── CRITICAL-4: TodoUpdate category_id max_length 검증 우회 ─────────────────

@pytest.mark.xfail(
    reason="CRITICAL-4: TodoUpdate.category_id에 max_length 없음 — 101자 카테고리 수정 허용",
    strict=True,
)
async def test_update_category_max_length_enforced(client: AsyncClient, test_user):
    """101자 category_id로 수정 → 422여야 하지만 현재 404 또는 200 반환."""
    todo = await _create(client, test_user.user_id)
    long_cat = "a" * 101
    resp = await client.patch(f"/todos/{todo['todo_id']}", json={"category_id": long_cat})
    assert resp.status_code == 422, f"101자 category_id 수정 허용: {resp.status_code}"


# ─── HIGH-1: title + status 동시 변경 시 update_embedding 파라미터 검증 ───────

async def test_title_and_status_change_uses_update_embedding(client: AsyncClient, test_user):
    """제목+상태 동시 변경 시 update_embedding이 최신 상태를 반영해야 함."""
    todo = await _create(client, test_user.user_id, title="기존 제목")
    with patch(_AI["update_embedding"], new_callable=AsyncMock) as mock_update:
        resp = await client.patch(
            f"/todos/{todo['todo_id']}",
            json={"title": "새 제목", "todo_status": "완료"},
        )
        assert resp.status_code == 200
        # update_embedding이 호출되고 completed=True (상태=완료)여야 함
        mock_update.assert_called_once()
        _, kwargs = mock_update.call_args
        assert kwargs["completed"] is True, (
            f"update_embedding에 completed=True 미전달: {mock_update.call_args}"
        )
        # patch_embedding은 호출되지 않아야 함 (elif 구조)
        # 이는 실제로 올바른 동작이지만, 테스트로 명시


async def test_update_embedding_receives_correct_params(client: AsyncClient, test_user):
    """update_embedding 호출 시 user_id(str), category, text, completed가 올바른지."""
    todo = await _create(client, test_user.user_id, title="원본", category_id="study")
    with patch(_AI["update_embedding"], new_callable=AsyncMock) as mock_update:
        resp = await client.patch(
            f"/todos/{todo['todo_id']}",
            json={"title": "변경된 제목"},
        )
        assert resp.status_code == 200
        mock_update.assert_called_once()
        _, kwargs = mock_update.call_args
        assert kwargs["user_id"] == str(test_user.user_id)
        assert kwargs["category"] == "study"
        assert kwargs["text"] == "변경된 제목"
        assert kwargs["completed"] is False  # 시작전이므로


async def test_patch_embedding_receives_correct_params_on_status_change(
    client: AsyncClient, test_user
):
    """상태 변경 시 patch_embedding에 completed 파라미터가 올바른지."""
    todo = await _create(client, test_user.user_id)
    with patch(_AI["patch_embedding"], new_callable=AsyncMock) as mock_patch:
        await client.patch(f"/todos/{todo['todo_id']}", json={"todo_status": "완료"})
        _, kwargs = mock_patch.call_args
        assert kwargs["completed"] is True
        assert "category" not in kwargs or kwargs.get("category") is None


async def test_patch_embedding_receives_correct_params_on_category_change(
    client: AsyncClient, test_user
):
    """카테고리 변경 시 patch_embedding에 category 파라미터가 올바른지."""
    todo = await _create(client, test_user.user_id, category_id="study")
    with patch(_AI["patch_embedding"], new_callable=AsyncMock) as mock_patch:
        await client.patch(f"/todos/{todo['todo_id']}", json={"category_id": "workout"})
        _, kwargs = mock_patch.call_args
        assert kwargs["category"] == "workout"
        assert "completed" not in kwargs or kwargs.get("completed") is None


# ─── 데이터 격리: 유저별 todo 분리 ──────────────────────────────────────────

async def test_user_todos_isolated_from_other_users(
    client: AsyncClient, test_user, second_user
):
    """유저 A의 todo 조회 시 유저 B의 todo가 포함되지 않아야 함."""
    await _create(client, test_user.user_id, title="유저A-todo")
    await _create(client, second_user.user_id, title="유저B-todo")

    resp = await client.get(f"/todos/user/{test_user.user_id}")
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]
    assert "유저A-todo" in titles
    assert "유저B-todo" not in titles


# ─── 이중 삭제 ────────────────────────────────────────────────────────────────

async def test_double_delete_returns_404(client: AsyncClient, test_user):
    """같은 todo를 두 번 삭제하면 두 번째는 404여야 함."""
    todo = await _create(client, test_user.user_id)
    todo_id = todo["todo_id"]
    first = await client.delete(f"/todos/{todo_id}")
    assert first.status_code == 200
    second = await client.delete(f"/todos/{todo_id}")
    assert second.status_code == 404


# ─── 삭제 후 수정 시도 ────────────────────────────────────────────────────────

async def test_update_deleted_todo_returns_404(client: AsyncClient, test_user):
    """삭제된 todo 수정 시도 → 404."""
    todo = await _create(client, test_user.user_id)
    await client.delete(f"/todos/{todo['todo_id']}")
    resp = await client.patch(f"/todos/{todo['todo_id']}", json={"title": "수정 시도"})
    assert resp.status_code == 404


# ─── 공백만 있는 제목 ─────────────────────────────────────────────────────────

@pytest.mark.xfail(
    reason="CRITICAL-2 연장: 공백 제목도 허용됨 (strip 후 empty 검증 없음)",
    strict=True,
)
async def test_whitespace_only_title_rejected(client: AsyncClient, test_user):
    resp = await client.post("/todos/", json={
        "title": "   ", "detail": "", "category_id": "study",
        "user_id": test_user.user_id, "todo_status": "시작전", "visibility": "친구공개",
    })
    assert resp.status_code == 422


# ─── 응답 필드 완전성 ──────────────────────────────────────────────────────────

async def test_create_response_contains_all_required_fields(client: AsyncClient, test_user):
    """생성 응답에 created_at, updated_at 등 모든 필드가 포함되어야 함."""
    resp = await client.post("/todos/", json={
        "title": "필드 검증", "detail": "상세", "category_id": "daily",
        "user_id": test_user.user_id, "todo_status": "시작전", "visibility": "친구공개",
    })
    assert resp.status_code == 201
    data = resp.json()
    for field in ["todo_id", "title", "detail", "todo_status", "visibility",
                  "user_id", "created_at", "updated_at"]:
        assert field in data, f"응답에 '{field}' 필드 없음"


# ─── 긴 제목 경계값 ──────────────────────────────────────────────────────────

async def test_create_title_at_max_length(client: AsyncClient, test_user):
    """255자 제목으로 생성 → 성공해야 함."""
    resp = await client.post("/todos/", json={
        "title": "가" * 255, "detail": "", "category_id": "etc",
        "user_id": test_user.user_id, "todo_status": "시작전", "visibility": "친구공개",
    })
    assert resp.status_code == 201


@pytest.mark.xfail(reason="title max_length(255) 초과 시 SQLite는 저장함 (MySQL은 거부)", strict=True)
async def test_create_title_over_max_length_rejected(client: AsyncClient, test_user):
    """256자 제목 → 422여야 하지만 SQLite에서 통과."""
    resp = await client.post("/todos/", json={
        "title": "가" * 256, "detail": "", "category_id": "etc",
        "user_id": test_user.user_id, "todo_status": "시작전", "visibility": "친구공개",
    })
    assert resp.status_code == 422
