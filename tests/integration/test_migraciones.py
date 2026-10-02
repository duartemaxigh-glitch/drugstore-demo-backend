from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect


pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parents[2]
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


def test_schema_de_integracion_proviene_de_alembic(
    test_engine,
    test_schema,
):
    with test_engine.connect() as connection:
        assert connection.exec_driver_sql(
            "SELECT current_schema()"
        ).scalar_one() == test_schema

        alembic_config = Config(str(PROJECT_ROOT / "alembic.ini"))
        alembic_config.attributes["connection"] = connection
        alembic_config.attributes["version_table_schema"] = test_schema

        head = ScriptDirectory.from_config(alembic_config).get_current_head()
        revision_actual = MigrationContext.configure(
            connection,
            opts={"version_table_schema": test_schema},
        ).get_current_revision()
        assert revision_actual == head

        inspector = inspect(connection)
        tablas_temporales = set(
            inspector.get_table_names(schema=test_schema)
        )
        assert tablas_temporales == EXPECTED_TABLES | {"alembic_version"}

        version_num = connection.exec_driver_sql(
            f'SELECT version_num FROM "{test_schema}".alembic_version'
        ).scalar_one()
        assert version_num == head

        tablas_public = set(inspector.get_table_names(schema="public"))
        assert EXPECTED_TABLES.isdisjoint(tablas_public)
        assert "alembic_version" not in tablas_public

        command.check(alembic_config)
