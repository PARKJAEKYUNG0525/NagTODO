import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# Windows에서 symlink 미지원 시 발생하는 huggingface_hub 경고 억제
# 기능에 영향 없음 — 캐시가 파일 복사 방식으로 동작할 뿐
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

'''BaseSetting 환경변수 기반 설정 관리 클래스(URL, DB, 환경설정)'''

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        case_sensitive=True,
        extra="ignore",   # 정의되지 않은 환경변수 무시
    )

    # LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b"
    OLLAMA_TIMEOUT: int = 60  # 로컬 Qwen2.5 3B 기준 여유 타임아웃(초)

    # 임베딩
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-small"

    # 백엔드 API
    BACKEND_API_URL: str = "http://localhost:8000"

    # 벡터 스토어
    FAISS_INDEX_PATH: str = "data/index.faiss"
    FAISS_METADATA_PATH: str = "data/metadata.json"

    # 리포트 / 클러스터링
    COSINE_THRESHOLD: float = 0.75
    MIN_CLUSTER_SIZE: int = 2
    TOP_K_SIMILAR: int = 20
    MIN_MONTHLY_TASKS: int = 20
    Min_MONTHLY_FAIL_TASKS : int = 5

# 싱글턴 인스턴스 생성
settings = Settings()