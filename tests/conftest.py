import os

# 必须在 import app 之前
os.environ.setdefault("APP_ENV", "dev")
os.environ.setdefault("DATABASE_URL", "mysql+pymysql://u:p@127.0.0.1:3306/test")
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "WUuna28VYCNhdugJZ3bhdbfmEmFJ7_3mtTF6u3UFjxg8KgbhMBC54SiL-l_D3o2oeUvbhmI4-FE-vYTQ_ubQgQ",
)
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6379/15")
os.environ.setdefault("MAIL_USERNAME", "test@example.com")
os.environ.setdefault("MAIL_PASSWORD", "x")
os.environ.setdefault("AppKey", "test-isbn-key")  # ISBN_KEY 的 alias
os.environ.setdefault("YU_SHU_API_BASE", "https://example.com")
# 若 import 链会校验 OSS，再补 OSS_*（看报错缺什么加什么）
os.environ.setdefault("OSS_ACCESS_KEY_ID", "test-oss-key-id")
os.environ.setdefault("OSS_ACCESS_KEY_SECRET", "test-oss-key-secret")
os.environ.setdefault("OSS_BUCKET_NAME", "test-bucket")
os.environ.setdefault("OSS_ENDPOINT", "https://oss-cn-hangzhou.aliyuncs.com")
os.environ.setdefault(
    "OSS_PUBLIC_BASE_URL", "https://test-bucket.oss-cn-hangzhou.aliyuncs.com"
)

import pytest
from httpx import ASGITransport, AsyncClient

from app import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    # lifespan="off"：冒烟测试不启动 Redis ping，避免依赖本机 Redis
    # transport = ASGITransport(app=app, lifespan="off")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
