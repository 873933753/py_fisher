from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.errors import register_exception_handlers
from app.secure import settings


# 在应用启动和关闭时初始化和关闭数据库
@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.libs.redis import get_redis_client

    # 表结构由 Alembic 管理，启动时不再 create_all
    get_redis_client().ping()  # 启动时确认 Redis 可用
    yield
    get_redis_client().close()  # 关闭连接池


def create_app():
    # 生产禁用 /docs、/redoc

    app_kwargs = {"lifespan": lifespan}
    if settings.IS_PROD:
        app_kwargs["openapi_url"] = None  # 同时禁用 /docs、/redoc

    app = FastAPI(**app_kwargs)

    # app = FastAPI(lifespan=lifespan)
    register_exception_handlers(app)
    register_apirouter(app)

    # 注册静态文件路由 - 用于访问静态文件,如图片
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # app/web/static → /web/static
    web_static_dir = Path(__file__).parent / "web" / "static"
    app.mount("/web/static", StaticFiles(directory=web_static_dir), name="web_static")

    return app


# 注册web路由
def register_apirouter(app):
    from app.admin.router import admin_router
    from app.web import web_router

    app.include_router(web_router)
    app.include_router(admin_router, prefix="/admin")

    # 练习/调试路由仅非生产环境挂载

    if not settings.IS_PROD:
        from test import test_router

        app.include_router(test_router)
