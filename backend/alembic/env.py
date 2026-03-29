"""Alembic env.py — Multi-tenant aware migrations.

Executa migrations no schema 'public' (tabelas globais) e depois
itera sobre todos os tenant schemas para aplicar tabelas do tenant.
"""

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override URL from env if available
database_url = os.getenv(
    "DATABASE_URL",
    config.get_main_option("sqlalchemy.url", ""),
)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (SQL script generation)."""
    context.configure(
        url=database_url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    engine = create_async_engine(database_url, poolclass=pool.NullPool)

    async with engine.connect() as connection:
        # 1. Migrate public schema
        await connection.execute(text("SET search_path TO public"))
        await connection.run_sync(do_run_migrations)

        # 2. Find all tenant schemas
        result = await connection.execute(
            text("SELECT schema_name FROM public.tenants WHERE status = 'active'")
        )
        tenant_schemas = [row[0] for row in result.fetchall()]

        # 3. Migrate each tenant schema
        for schema in tenant_schemas:
            await connection.execute(text(f"SET search_path TO {schema}, public"))
            await connection.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
