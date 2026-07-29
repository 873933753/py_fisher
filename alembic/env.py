import sys
from logging.config import fileConfig
from pathlib import Path

import sqlmodel.sql.sqltypes as sqltypes
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context

# 保证在 fisher/ 下执行 alembic 时能 import app
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 必须导入所有 table=True 的模型，否则 autogenerate 看不到表
from app.models.book import Book  # noqa: F401
from app.models.drift import Drift  # noqa: F401
from app.models.gift import Gift  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.wish import Wish  # noqa: F401
from app.secure import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 用 .env 中的 DATABASE_URL 覆盖 alembic.ini
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = SQLModel.metadata


def render_item(type_, obj, autogen_context):
    """把 SQLModel 的 AutoString 渲染成标准 sa.String"""
    if type_ == "type" and isinstance(obj, sqltypes.AutoString):
        if obj.length:
            return f"sa.String(length={obj.length})"
        return "sa.String()"
    return False


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_item=render_item,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_item=render_item,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
