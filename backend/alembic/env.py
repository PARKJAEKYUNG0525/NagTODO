from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 마이그레이션을 어떤 방식으로 실행할지 정의하는 스크립트

# 설정 로드
# ↓
# offline 모드인가?
#    → SQL만 생성
# online 모드인가?
#    → DB에 직접 적용

# alembic.ini 설정 접근 객체
config = context.config

# 로킹 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None


# 오프라인 모드에서 마이그레이션 실행
# DB Engine을 만들지 않고, URL만으로 context를 설정
# SQL 문자열이 스크립트 출력으로 생성
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# 온라인 모드에서 마이그레이션 실행
# db 직접 연결 / 실제 변경 수행
def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
