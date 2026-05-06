import random
from datetime import date
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.attendance import Attendance
from app.db.models.reward import Reward
from app.db.models.cloth import Cloth
from app.db.scheme.attendance import AttendanceResponse

# 누적 출석일수 리스트 (고정)
REWARDS_THRESHOLDS = [1, 3, 7, 14, 30, 60, 100, 150, 200]

class AttendanceService:
    @staticmethod
    async def create_attendance_svc(db: AsyncSession, user_id: int) -> AttendanceResponse:
        # 오늘 날짜 가져와서
        today = date.today()
        # 오늘 출석했는지 확인
        existing = await db.execute(
            select(Attendance).where(
                Attendance.user_id == user_id,
                Attendance.attended_at == today
            )
        )
        # 이미 출석했다면 True, 아직이라면 False
        already_today = existing.scalar_one_or_none() is not None
        # 누적 출석 일수 count
        counter = await db.execute(
            select(func.count()).select_from(Attendance)
                .where(Attendance.user_id == user_id)
        )
        # 누적 출석 일수 저장
        total = counter.scalar() or 0
        # 1. 이미 출석 했다면? DB 반영X
        if already_today:
            return AttendanceResponse(
                is_first_today=False,
                total_days=total,
            )
        # 2. 이제 첫 출석이라면?
        db.add(Attendance(user_id=user_id, attended_at=today))
        # DB에 출석 즉시 반영
        await db.flush()
        total += 1
        # 회원의 누적 출석 일수가 누적 출석일수 리스트에 있으면 보상 주기
        chosen_cloth: Optional[Cloth] = None
        if total in REWARDS_THRESHOLDS:
            chosen_cloth = await AttendanceService.unlock_croissant_svc(db, user_id)
        # 얻은 보상이 어떤건지 속성 추출
        # commit 전에 cloth 속성을 미리 추출 (commit 후엔 expired되어 접근 불가)
        reward_cloth_id = chosen_cloth.cloth_id if chosen_cloth else None
        reward_cloth_title = chosen_cloth.title if chosen_cloth else None
        reward_cloth_file_url = chosen_cloth.file_url if chosen_cloth else None

        await db.commit()

        return AttendanceResponse(
            is_first_today=True,
            total_days=total,
            reward_cloth_id=reward_cloth_id,
            reward_cloth_title=reward_cloth_title,
            reward_cloth_file_url=reward_cloth_file_url,
        )

    @staticmethod
    async def unlock_croissant_svc(db: AsyncSession, user_id: int) -> Optional[Cloth]:
        owned_q = await db.execute(
            select(Reward.cloth_id).where(
                Reward.user_id == user_id,
                Reward.cloth_id.like("croissant_%")
            )
        )
        owned = set(owned_q.scalars().all())

        if owned:
            locked_q = await db.execute(
                select(Cloth).where(
                    Cloth.cloth_id.like("croissant_%"),
                    ~Cloth.cloth_id.in_(owned)
                )
            )
        else:
            locked_q = await db.execute(
                select(Cloth).where(Cloth.cloth_id.like("croissant_%"))
            )
        locked = locked_q.scalars().all()

        if not locked:
            return None

        chosen = random.choice(locked)
        db.add(Reward(user_id=user_id, cloth_id=chosen.cloth_id))
        return chosen