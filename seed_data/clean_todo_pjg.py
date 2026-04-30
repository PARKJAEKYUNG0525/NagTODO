import re
import uuid
import csv
from datetime import datetime

NAME = 'pjg'
USERID = 105

# 제목 → 카테고리 매핑 (데이터에 카테고리 정보가 없으므로 여기서 직접 지정)
CATEGORY_MAP = {
    "학원가기": "일상",
    "공부":    "공부",
    "복습":    "공부",
    "정처기":  "공부",
    "팀플":    "공부",
    "운동하기": "운동",
    "알바":    "일상",
    "친구":    "일상",
    "농구":    "운동",
    "재활용":  "일상",
    "방청소": "일상"
}

STATUS_MAP = {
    "O": "완료",
    "X": "시작전",
}


def parse_txt(input_path: str, year: int = 2026) -> list[dict]:
    """
    입력 형식:
        4/10 금      ← 날짜 라인
        학원가기 O   ← todo 항목 (O=완료, X=시작전)
        공부         ← O/X 없는 항목 → 상태 미기록, "시작전"으로 처리
        복습 X
        ...
    """
    results = []
    current_date = None

    with open(input_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            # 날짜 라인: "4/10 금" 형태
            date_match = re.match(r"^(\d{1,2})/(\d{1,2})\s+[가-힣]+$", line)
            if date_match:
                month, day = int(date_match.group(1)), int(date_match.group(2))
                current_date = datetime(year, month, day)
                continue

            if current_date is None:
                print(f"날짜 없이 항목 발견, 건너뜀: {line}")
                continue

            # O/X 없는 항목은 무시
            todo_match = re.match(r"^(.+?)\s+(O|X)$", line)
            if not todo_match:
                continue

            title = todo_match.group(1).strip()
            status = STATUS_MAP[todo_match.group(2)]

            category = CATEGORY_MAP.get(title, "기타")
            if category == "기타":
                print(f"카테고리 미등록 항목: '{title}' → CATEGORY_MAP에 추가 필요")

            results.append({
                "history_id": str(uuid.uuid4()),
                "user_id": USERID,
                "title": title,
                "todo_status": status,
                "archived_at": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                "category_name": category,
            })

    return results


def save_to_csv(data: list[dict], output_path: str) -> None:
    fieldnames = [
        "history_id",
        "user_id",
        "title",
        "todo_status",
        "archived_at",
        "category_name",
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    input_path = rf"C:\NagTODO\seed_data\todo_{NAME}.txt"
    output_path = rf"C:\NagTODO\seed_data\{NAME}({USERID})_clean.csv"

    data = parse_txt(input_path)
    save_to_csv(data, output_path)

    print(f"{len(data)}개 변환 완료")
