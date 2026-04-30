import re
import uuid
import csv
from datetime import datetime

NAME = 'ljh'
USERID = 4

STATUS_MAP = {
    "성공": "완료",
    "실패": "시작전"
}


def parse_line(line: str, year=2026):
    pattern = r"(\d{1,2})/(\d{1,2})\([^)]+\)\s+(.*?)\s*/\s*(.*?)\s*/\s*(.*?)$"
    match = re.match(pattern, line)

    if not match:
        return None

    month, day, title, category, status = match.groups()

    try:
        date = datetime(year, int(month), int(day))
    except ValueError:
        return None

    return {
        "history_id": str(uuid.uuid4()),
        "user_id": USERID,
        "title": title.strip(),
        "todo_status": STATUS_MAP.get(status.strip(), "시작전"),
        "archived_at": date.strftime("%Y-%m-%d %H:%M:%S"),
        "category_name": category.strip()
    }


def parse_txt(input_path):
    results = []

    with open(input_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            parsed = parse_line(line)
            if parsed:
                results.append(parsed)
            else:
                print(f"파싱 실패: {line}")

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
    input_path = rf"C:\NagTODO\seed_data\todo_{NAME}.txt"
    output_path = rf"C:\NagTODO\seed_data\{NAME}({USERID})_clean.csv"

    data = parse_txt(input_path)
    save_to_csv(data, output_path)

    print(f"{len(data)}개 변환 완료")