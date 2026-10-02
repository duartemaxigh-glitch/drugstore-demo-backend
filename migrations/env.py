import os
from logging.config import fileConfig

from sqlalchemy import create_engine, make_url, pool

from alembic import context
from infraestructura.basedatos.base import Base
from infraestructura.basedatos.modelos import (
    categoria_modelo,
    cliente_modelo,
    compra_modelo,
    medio_pago_modelo,
    producto_modelo,
    proveedor_modelo,
    usuario_modelo,
    venta_modelo,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

EXPECTED_TABLES = {
    "categorias",
    "clientes",
    "compra_detalle",
    "compras",
    "medios_pago",
    "productos",
    "proveedores",
    "usuarios",
    "venta_detalle",
    "ventas",
}


def _database_url():
    raw_url = os.getenv("ALEMBIC_DATABASE_URL")
    if not raw_url:
        raise RuntimeError(
            "ALEMBIC_DATABASE_URL no está configurada. Alembic requiere una "
            "URL PostgreSQL explícita y no usa la base de la aplicación como "
            "fallback."
        )

    url = make_url(raw_url)
    if url.drivername != "postgresql+psycopg":
        raise RuntimeError(
            "ALEMBIC_DATABASE_URL debe usar el driver postgresql+psycopg."
        )
    return url


def _validate_metadata() -> None:
    actual_tables = set(Base.metadata.tables)
    if actual_tables != EXPECTED_TABLES:
        missing = sorted(EXPECTED_TABLES - actual_tables)
        unexpected = sorted(actual_tables - EXPECTED_TABLES)
        raise RuntimeError(
            "Base.metadata no contiene exactamente las diez tablas esperadas. "
            f"Faltantes: {missing or 'ninguna'}. "
            f"Inesperadas: {unexpected or 'ninguna'}."
        )


_validate_metadata()
target_metadata = Base.metadata


def _include_object(object_, name, type_, reflected, compare_to) -> bool:
    return not (type_ == "table" and name == "alembic_version")


CONTEXT_OPTIONS = {
    "compare_type": True,
    "compare_server_default": False,
    "include_schemas": False,
    "include_object": _include_object,
}


def _configure_context(connection) -> None:
    options = dict(CONTEXT_OPTIONS)
    version_table_schema = config.attributes.get("version_table_schema")
    if version_table_schema is not None:
        options["version_table_schema"] = version_table_schema

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        **options,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    database_url = _database_url()
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **CONTEXT_OPTIONS,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    external_connection = config.attributes.get("connection")
    if external_connection is not None:
        _configure_context(external_connection)
        return

    connectable = create_engine(
        _database_url(),
        poolclass=pool.NullPool,
    )

    try:
        with connectable.connect() as connection:
            _configure_context(connection)
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
