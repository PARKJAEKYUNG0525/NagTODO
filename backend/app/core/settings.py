from pydantic_settings import BaseSettings
from pydantic import Field
from datetime import timedelta

'''BaseSetting 환경변수 기반 설정 관리 클래스(DB, API키, 환경설정)'''

class Settings(BaseSettings):
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_host: str = Field("localhost", alias="DB_HOST")
    db_port: int = Field("3306", alias="DB_PORT")
    db_name: str = Field(..., alias="DB_NAME")

    secret_key: str = Field(..., alias="SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_expire_seconds: int = Field(900, alias="ACCESS_TOKEN_EXPIRE")
    refresh_token_expire_seconds: int = Field(604800, alias="REFRESH_TOKEN_EXPIRE")

    class Config:
        env_file = ".env"
        # 환경변수 대소문자 구분
        case_sensitive = True
        extra = "allow"
        populate_by_name = True

    # 동적 프로퍼티
    # 메서드를 속성처럼 접근할 수 있게 해줌
    # "root:12345@localhost:3306/board"
    @property
    def tmp_db(self) -> str:
        return f"{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # 비동기 DB URL
    # "mysql+asyncmy://root:12345@localhost:3306/board"
    @property
    def db_url(self) -> str:
        return f"mysql+asyncmy://{self.tmp_db}"

    # 동기 DB URL
    @property
    def sync_db_url(self) -> str:
        return f"mysql+pymysql://{self.tmp_db}"

    @property
    def access_token_expire(self) -> timedelta:
        # 초 단위 -> timedelta 객체로 변환
        return timedelta(seconds=self.access_token_expire_seconds)

    @property
    def refresh_token_expire(self) -> timedelta:
        # 초 단위 -> timedelta 객체로 변환
        return timedelta(seconds=self.refresh_token_expire_seconds)

# @property를 사용했기 때문에
# settings.tmp_db / settings.db_url / settings.sync_db_url 형식으로 접근 가능
settings = Settings();
