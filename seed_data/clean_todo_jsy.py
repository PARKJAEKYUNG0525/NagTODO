import re
import uuid
import csv
from datetime import datetime

NAME = 'jsy'
USERID = 1

STATUS_MAP = {
    "완료": "완료",
    "진행중": "진행중",
    "시작전": "시작전",
    "실패": "시작전"
}

def parse_date(line: str, year=2026):
    match = re.search(r"(\d+)월(\d+)일", line)
    if match:
        month, day = map(int, match.groups())
        return datetime(year, month, day)
    return None


def clean_and_parse(file_path: str):
    results = []
    current_date = None

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for raw_line in lines:
        line = raw_line.strip()

        # 빈 줄 제거
        if not line:
            continue

        # 시간 라인 제거
        if line.startswith("오후") or line.startswith("오전"):
            continue

        # 날짜 라인
        parsed_date = parse_date(line)
        if parsed_date:
            current_date = parsed_date
            continue

        # 데이터 라인
        parts = [p.strip() for p in line.split(",")]

        if len(parts) != 3:
            continue

        title, category, status = parts

        if current_date is None:
            continue  # 날짜 없는 데이터는 스킵

        results.append({
            "history_id": str(uuid.uuid4()),
            "user_id": USERID,
            "title": title,
            "todo_status": STATUS_MAP.get(status, "시작전"),
            "archived_at": current_date.strftime("%Y-%m-%d %H:%M:%S"),
            "category_name": category
        })

    return results


def save_to_csv(data, output_path="history_seed.csv"):
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
    data = clean_and_parse(rf"C:\NagTODO\seed_data\todo_{NAME}.txt")
    save_to_csv(data, rf"C:\NagTODO\seed_data\{NAME}({USERID})_clean.csv")

    print(f"{len(data)}개 데이터 CSV 저장 완료")