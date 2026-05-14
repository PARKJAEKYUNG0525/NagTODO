import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Suppress HF symlink warning on Windows.
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        case_sensitive=True,
        extra="ignore",
    )

    # LLM
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TIMEOUT: int = 30

    # Embedding
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-small"
    VECTOR_DIM: int = 384

    # Backend API
    BACKEND_API_URL: str = "https://f30b-1-215-146-37.ngrok-free.app"

    # Vector store
    FAISS_INDEX_PATH: str = "data/index.faiss"
    FAISS_METADATA_PATH: str = "data/metadata.json"

    # Report and clustering
    COSINE_THRESHOLD: float = 0.75
    MIN_CLUSTER_SIZE: int = 2
    TOP_K_SIMILAR: int = 50
    MIN_PERSONAL_TODOS: int = 15
    MIN_MONTHLY_TASKS: int = 30
    MIN_MONTHLY_FAIL_TASKS: int = 5

    # Demo mode
    DEMO_MODE: bool = False


settings = Settings()
