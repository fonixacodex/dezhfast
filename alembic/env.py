# alembic/env.py
"""
تنظیمات Alembic برای Dezh — async.
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.core.config import settings

# ⚠️ همه‌ی modelها باید import بشن
from app.database.base import Base  # noqa
from app.modules.analytics import model as _a_model  # noqa
from app.modules.auth import model as _auth_model  # noqa
from app.modules.instagram import model as _ig_model  # noqa
from app.modules.tickets import model as _t_model  # noqa

# Alembic Config
config = context.config

# لاگینگ
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# URL دیتابیس از settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Metadata
target_metadata = Base.metadata


# ==================== Offline ====================
def run_migrations_offline() -> None:
    """Offline mode — فقط SQL تولید می‌کنه."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ==================== Online (async) ====================
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Async migration."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Online mode."""
    asyncio.run(run_async_migrations())


# ==================== اجرا ====================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()