import csv
import uuid
from datetime import datetime

NAME = 'chj'
USERID = 103

TYPE_MAP = {
    "운동": "운동",
    "공부": "공부",
    "일상": "일상",
    "일": "업무",
    "프로젝트": "공부",
    "포트폴리오": "공부"
}

STATUS_MAP = {
    "Completed": "완료",
    "In progress": "진행중",
    "Not started": "시작전"
}


def parse_korean_date(date_str: str):
    """
    '12월 22' → datetime(2025, 12, 22)
    '3월 1'  → datetime(2026, 3, 1)
    10월 이후는 2025년, 그 외는 2026년으로 처리
    """
    try:
        month, day = date_str.replace("월", "").split()
        month = int(month)
        year = 2025 if month >= 10 else 2026
        return datetime(year, month, int(day))
    except Exception:
        return None


def parse_simple_csv(input_path):
    results = []

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        reader.fieldnames = [name.strip().replace("\ufeff", "") for name in reader.fieldnames]

        for row in reader:
            title = row["To-do"].strip()
            date_str = row["Date"].strip()
            progress = row["Progress"].strip()
            raw_type = row["Type"].strip()

            # 날짜 변환
            parsed_date = parse_korean_date(date_str)
            if not parsed_date:
                print(f"날짜 파싱 실패: {date_str}")
                continue

            # 2026-03-01 이전 데이터 제외
            if parsed_date < datetime(2026, 3, 1):
                continue

            # 상태 변환
            status = STATUS_MAP.get(progress, "시작전")

            # 카테고리 변환
            category = TYPE_MAP.get(raw_type, "기타")

            results.append({
                "history_id": str(uuid.uuid4()),
                "user_id": USERID,
                "title": title,
                "todo_status": status,
                "archived_at": parsed_date.strftime("%Y-%m-%d %H:%M:%S"),
                "category_name": category
            })

    return results


def save_to_csv(data, output_path):
    fieldnames = [
        "history_id",
        "user_id",
        "title",
        "todo_status",
        "archived_at",
        "category_name"
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


# 실행
if __name__ == "__main__":
    data = parse_simple_csv(rf"C:\NagTODO\seed_data\todo_{NAME}.csv")
    save_to_csv(data, rf"C:\NagTODO\seed_data\{NAME}({USERID})_clean.csv")

    print(f"{len(data)}개 데이터 변환 완료")