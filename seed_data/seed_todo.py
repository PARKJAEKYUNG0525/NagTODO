"""
todo 테이블 + FAISS 벡터 스토어 시드 스크립트

실행: python seed_data/seed_todo.py  (프로젝트 루트에서)

seed_data/*_clean.csv 파일을 모두 읽어
  1. MySQL todo 테이블에 삽입 (중복 todo_id는 건너뜀)
  2. FAISS 벡터 스토어에 임베딩 저장 (중복 todo_id는 건너뜀)

CSV 컬럼: history_id, user_id, title, todo_status, archived_at, category_name
매핑:
  history_id    → todo_id
  archived_at   → created_at, updated_at
  category_name → category_id  (_CATEGORY_MAP 참조)
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import os
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "backend" / ".env")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from ai.core.dependencies import get_embedding_model, get_embedding_store

# category_name(한글) → category_id 매핑 (backend/app/db/seed.py 기준)
_CATEGORY_MAP: dict[str, str] = {
    "공부": "study",
    "운동": "workout",
    "일상": "daily",
    "약속": "appointment",
    "업무": "work",
    "기타": "etc",
}


def _db_url() -> str:
    user     = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    host     = os.environ.get("DB_HOST", "localhost")
    port     = os.environ.get("DB_PORT", "3306")
    name     = os.environ["DB_NAME"]
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"


def _load_csv_rows() -> list[dict]:
    seed_dir = Path(__file__).resolve().parent
    csv_files = sorted(seed_dir.glob("*_clean.csv"))
    if not csv_files:
        print("seed_data/*_clean.csv 파일이 없습니다.")
        sys.exit(1)

    rows: list[dict] = []
    for path in csv_files:
        with open(path, encoding="utf-8-sig") as f:
            rows.extend(list(csv.DictReader(f)))
        print(f"  로드: {path.name} ({len(rows)}행 누계)")
    return rows


def _seed_db(rows: list[dict]) -> int:
    engine = create_engine(_db_url())
    Session = sessionmaker(bind=engine)

    with Session() as session:
        existing = {r[0] for r in session.execute(text("SELECT todo_id FROM todo"))}

        # todo 테이블은 user_id, category_id에 FK 제약이 있으므로 일시 해제
        session.execute(text("SET FOREIGN_KEY_CHECKS=0"))

        inserted = 0
        skipped = 0
        for row in rows:
            todo_id = row["history_id"]
            if todo_id in existing:
                skipped += 1
                continue

            category_name = row["category_name"]
            category_id = _CATEGORY_MAP.get(category_name)
            if category_id is None:
                print(f"  경고: 알 수 없는 category_name '{category_name}', 'etc'로 대체")
                category_id = "etc"

            archived_at = datetime.fromisoformat(row["archived_at"])

            session.execute(
                text("""
                    INSERT INTO todo
                        (todo_id, title, todo_status, detail, visibility,
                         created_at, updated_at, user_id, category_id)
                    VALUES
                        (:todo_id, :title, :todo_status, NULL, '친구공개',
                         :created_at, :updated_at, :user_id, :category_id)
                """),
                {
                    "todo_id":     todo_id,
                    "title":       row["title"],
                    "todo_status": row["todo_status"],
                    "created_at":  archived_at,
                    "updated_at":  archived_at,
                    "user_id":     int(row["user_id"]),
                    "category_id": category_id,
                },
            )
            inserted += 1

        session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        session.commit()

    if skipped:
        print(f"  (중복 {skipped}개 건너뜀)")
    return inserted


def _seed_vector_store(rows: list[dict]) -> int:
    print("임베딩 모델 로딩 중...")
    model = get_embedding_model()
    store = get_embedding_store()

    existing = {m["todo_id"] for m in store._metadata if not m["is_deleted"]}

    added = 0
    total = len(rows)
    for i, row in enumerate(rows, 1):
        todo_id = row["history_id"]
        if todo_id in existing:
            continue

        category_id = _CATEGORY_MAP.get(row["category_name"], "etc")
        vec = model.encode_passage(row["title"])
        store.add(
            todo_id=todo_id,
            vec=vec,
            meta={
                "user_id":   str(row["user_id"]),
                "text":      row["title"],
                "category":  category_id,
                "completed": row["todo_status"] == "완료",
            },
        )
        added += 1
        if added % 50 == 0:
            print(f"  임베딩 진행: {i}/{total}")

    store.save()
    return added


def main() -> None:
    print("=== todo 시드 시작 ===")

    rows = _load_csv_rows()
    print(f"총 {len(rows)}개 레코드\n")

    print("[1/2] DB 삽입 중...")
    inserted = _seed_db(rows)
    print(f"  → {inserted}개 삽입 완료\n")

    print("[2/2] 벡터 스토어 임베딩 중...")
    added = _seed_vector_store(rows)
    print(f"  → {added}개 임베딩 저장 완료\n")

    print("=== 완료 ===")


if __name__ == "__main__":
    main()
