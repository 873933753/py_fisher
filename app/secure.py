import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_files() -> None:
    """先读 .env，再读 .env.{APP_ENV}。进程已有环境变量优先（override=False）。"""
    load_dotenv(_BASE_DIR / ".env")
    app_env = os.getenv("APP_ENV", "dev").lower()
    env_file = _BASE_DIR / f".env.{app_env}"
    if env_file.is_file():
        load_dotenv(env_file)


_load_env_files()


class Settings(BaseSettings):
    # 不在这里读 env_file：已由 _load_env_files 注入 os.environ
    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
    )

    APP_ENV: str = "dev"
    DATABASE_URL: str
    SQL_ECHO: bool = False
    # --------------------- 认证 ---------------------
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int
    # --------------------- Redis ---------------------
    REDIS_URL: str

    # --------------------- Email ---------------------
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_SERVER: str = "smtp.qq.com"
    MAIL_PORT: int = 465
    MAIL_USE_SSL: bool = True

    # --------------------- ISBN ---------------------
    ISBN_KEY: str = Field(validation_alias="AppKey")
    # --------------------- 三方 API ---------------------
    YU_SHU_API_BASE: str

    @field_validator("YU_SHU_API_BASE")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")

    @property
    def IS_PROD(self) -> bool:
        return self.APP_ENV.lower() == "prod"

    @property
    def MAIL_SENDER(self) -> str:
        return f"Hanber <{self.MAIL_USERNAME}>"


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        raise SystemExit(
            f"[config] 配置校验失败 (APP_ENV={os.getenv('APP_ENV', 'dev')}): {e}"
        ) from e


settings = get_settings()
