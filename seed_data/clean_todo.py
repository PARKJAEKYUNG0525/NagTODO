"""
seed_data/todo_<user>.csv 를 정제하여 <user>_cleaned.csv 로 저장한다.

변환 규칙
- user     : 파일명 'todo_' 뒤의 문자열
- date     : "M월 D" → YYYY-MM-DD (12월은 2025년, 1월~ 는 2026년)
- todo     : 그대로
- progress : Not started → 0 / In progress → 1 / Completed → 2
- type     : 운동 → 운동, 공부 → 공부, 일상 → 일상, 일 → 업무,
             프로젝트 → 공부, 포트폴리오 → 공부, 빈값/기타 → 기타

약속, 운동, 일상, 공부, 업무, 기타
"""

import re
import csv
from pathlib import Path

HERE = Path(__file__).parent

PROGRESS_MAP = {
    "not started": 0,
    "in progress": 1,
    "completed": 2,
}

TYPE_MAP = {
    "운동": "운동",
    "공부": "공부",
    "일상": "일상",
    "일": "업무",
    "프로젝트": "공부",
    "포트폴리오":"공부"
}


def parse_date(raw: str) -> str:
    """'M월 D' → 'YYYY-MM-DD'. 12월은 2025년, 나머지는 2026년."""
    m = re.match(r"(\d+)월\s*(\d+)", raw.strip())
    if not m:
        raise ValueError(f"날짜 파싱 실패: {raw!r}")
    month, day = int(m.group(1)), int(m.group(2))
    year = 2025 if month == 12 else 2026
    return f"{year}-{month:02d}-{day:02d}"


def map_progress(raw: str) -> int:
    key = raw.strip().lower()
    if key not in PROGRESS_MAP:
        raise ValueError(f"알 수 없는 progress 값: {raw!r}")
    return PROGRESS_MAP[key]


def map_type(raw: str) -> str:
    return TYPE_MAP.get(raw.strip(), "기타")


def clean(src: Path, dst: Path, user: str) -> None:
    rows = []
    with src.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # 헤더 제외, 행 번호는 CSV 기준
            try:
                rows.append({
                    "user": user,
                    "date": parse_date(row["Date"]),
                    "todo": row["To-do"].strip(),
                    "progress": map_progress(row["Progress"]),
                    "type": map_type(row["Type"]),
                })
            except ValueError as e:
                print(f"[행 {i}] 건너뜀 — {e}")

    with dst.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["user", "date", "todo", "progress", "type"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"완료: {len(rows)}건 → {dst}")


if __name__ == "__main__":
    src = HERE / "todo_chj.csv"
    # 파일명에서 'todo_' 뒤 문자열 추출 (예: todo_chj.csv → chj)
    user = src.stem.split("todo_", 1)[-1]
    clean(src, HERE / f"{user}_cleaned.csv", user)
