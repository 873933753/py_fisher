import os
from pathlib import Path

from dotenv import load_dotenv

# fisher/ 目录（本文件在 fisher/app/secure.py）
_BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_files() -> None:
    """先读开关 .env，再读 .env.{APP_ENV}。

    均使用 override=False：进程里已有的环境变量（测试 / Docker / CI）优先，
    不会被文件覆盖。因此 .env 里只放 APP_ENV，具体配置放 .env.dev 等。
    """
    load_dotenv(_BASE_DIR / ".env")
    app_env = os.getenv("APP_ENV", "dev").lower()
    env_file = _BASE_DIR / f".env.{app_env}"
    if env_file.is_file():
        load_dotenv(env_file)


_load_env_files()


# 缺少必要环境变量时，抛出异常
def _require_str(name: str) -> str:
    value = os.getenv(name)
    if value is None or str(value).strip() == "":
        raise SystemExit(
            f"[config] 缺少必要环境变量: {name} "
            f"(APP_ENV={os.getenv('APP_ENV', 'dev')}). "
            f"请检查 .env / .env.{{APP_ENV}} 或进程环境变量。"
        )
    return value


# 环境变量必须是整数时，抛出异常
def _require_int(name: str) -> int:
    raw = _require_str(name)
    try:
        return int(raw)
    except ValueError:
        raise SystemExit(
            f"[config] 环境变量 {name} 必须是整数，当前值: {raw!r} "
            f"(APP_ENV={os.getenv('APP_ENV', 'dev')})"
        )


# 运行环境：dev / staging / prod
APP_ENV = os.getenv("APP_ENV", "dev").lower()
IS_PROD = APP_ENV == "prod"

# 数据库连接串
DATABASE_URL = _require_str("DATABASE_URL")
# SQLAlchemy echo：控制台打印 SQL，开发可设 true，生产保持 false
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() in ("1", "true", "yes")

# jwt配置
JWT_SECRET_KEY = _require_str("JWT_SECRET_KEY")
JWT_ALGORITHM = _require_str("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = _require_int("JWT_EXPIRE_MINUTES")

# 邮箱配置
MAIL_SERVER = "smtp.qq.com"
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = _require_str("MAIL_USERNAME")
MAIL_PASSWORD = _require_str("MAIL_PASSWORD")
MAIL_SENDER = f"Hanber <{MAIL_USERNAME}>"

# redis配置
REDIS_URL = _require_str("REDIS_URL")


# 图书搜索API配置
ISBN_KEY = _require_str("AppKey")
# 第三方图书/商品接口根地址，末尾不要带 /
YU_SHU_API_BASE = _require_str("YU_SHU_API_BASE").rstrip("/")
