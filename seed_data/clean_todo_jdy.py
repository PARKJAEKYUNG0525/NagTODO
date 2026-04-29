import csv
import uuid
from datetime import datetime

NAME = 'jdy'
USERID = 2

import csv
import uuid
from datetime import datetime


def parse_wide_csv(input_path):
    results = []

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    header = rows[0]

    # ✅ header에서 날짜만 추출
    dates = []
    for i in range(len(header)):
        if header[i] == "날짜":
            if i + 1 < len(header):
                dates.append(header[i + 1])

    # ✅ 데이터 파싱
    for row in rows[1:]:
        category = row[0]

        data_idx = 1  # TRUE/FALSE 시작 위치

        for date_str in dates:
            try:
                status_raw = row[data_idx]
                title = row[data_idx + 1]
            except IndexError:
                break

            data_idx += 2  # 다음 날짜로 이동

            # 빈 값 스킵
            if not date_str or not title:
                continue

            # 날짜 변환
            try:
                archived_at = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print(f"날짜 파싱 실패: {date_str}")
                continue

            # 상태 변환
            status = "완료" if status_raw == "TRUE" else "시작전"

            results.append({
                "history_id": str(uuid.uuid4()),
                "user_id": USERID,
                "title": title,
                "todo_status": status,
                "archived_at": archived_at.strftime("%Y-%m-%d %H:%M:%S"),
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
    data = parse_wide_csv(rf"C:\NagTODO\seed_data\todo_{NAME}.csv")
    save_to_csv(data, rf"C:\NagTODO\seed_data\{NAME}({USERID})_clean.csv")

    print(f"{len(data)}개 변환 완료")