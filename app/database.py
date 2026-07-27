# 数据库连接与会话管理
from sqlmodel import create_engine, Session
from app.secure import DATABASE_URL, SQL_ECHO
from sqlalchemy import event
from sqlalchemy.orm import with_loader_criteria
from app.models.base import BaseModel

# 上下文管理器
from contextlib import contextmanager

# SQLite 多线程下需要 check_same_thread=False；MySQL 不需要额外 connect_args
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL and DATABASE_URL.startswith("sqlite")
    else {}
)

# 创建数据库引擎；echo 由 .env 中 SQL_ECHO 控制（true/1/yes 开启 SQL 日志）
engine = create_engine(DATABASE_URL, echo=SQL_ECHO, connect_args=connect_args)


# 不再使用init_db，使用Alembic迁移
# def init_db():
#     """应用启动时根据模型自动建表（开发阶段使用，生产建议用 Alembic 迁移）"""
#     # 必须导入模型，否则 metadata 中无表定义，create_all 不会建表
#     from app.models.book import Book  # noqa: F401
#     from app.models.gift import Gift  # noqa: F401
#     from app.models.user import User  # noqa: F401
#     from app.models.wish import Wish  # noqa: F401
#     from app.models.drift import Drift  # noqa: F401

#     SQLModel.metadata.create_all(engine)


# 获取数据库会话，供路由通过 Depends(get_session) 注入使用
def get_session():
    """
    数据库会话依赖，供路由通过 Depends(get_session) 注入使用。

    用法示例（在路由文件中）：
        from fastapi import Depends
        from sqlmodel import Session
        from app.database import get_session

        @router.get("/book/{isbn}")
        def get_book(isbn: str, session: Session = Depends(get_session)):
            ...

    FastAPI 会在每个请求前创建 Session，请求结束后自动关闭，无需手动 session.close()。
    """
    # 1、with Session(engine) as session：从连接池拿到一个数据库会话（相当于“连接上数据库”）
    # 2、yield session：把 session 交给 FastAPI 路由使用
    # 3、请求结束后：with 块结束，Session 自动 close()，连接归还连接池
    # 所以注释里写“无需手动 session.close()”——with 帮你做了这件事。
    with Session(engine) as session:
        yield session


# 上下文管理器：块成功则 commit，失败则 rollback 再抛出。
@contextmanager
def auto_commit(session: Session):
    """业务写库时使用：块成功则 commit，失败则 rollback 再抛出。"""
    try:
        yield
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


# 监听SQL执行，过滤软删除数据
# 只查询未删除的数据
@event.listens_for(Session, "do_orm_execute")
def _filter_soft_deleted(execute_state):
    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                BaseModel,
                lambda cls: cls.is_deleted == 0,
                include_aliases=True,
            )
        )
