# 健康检查接口
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlmodel import text

from app.database import engine
from app.libs.redis import redis_client

health_router = APIRouter()


# 检查redis和mysql连接
@health_router.get("/health")
async def health_check():
    checks: dict[str, str] = {}

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["mysql"] = "ok"
    except Exception:
        checks["mysql"] = "error"

    try:
        redis_client.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"

    ok = all(v == "ok" for v in checks.values())

    return JSONResponse(
        status_code=200 if ok else 503,
        content={
            "status": "ok" if ok else "unavailable",
            "checks": checks,
        },
    )
