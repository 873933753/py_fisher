import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# 保证在 fisher/ 下执行 alembic 时能 import app
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.secure import DATABASE_URL

# 必须导入所有 table=True 的模型，否则 autogenerate 看不到表
from app.models.book import Book  # noqa: F401
from app.models.gift import Gift  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.wish import Wish  # noqa: F401
from app.models.drift import Drift  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 用 .env 中的 DATABASE_URL 覆盖 alembic.ini
config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
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
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
