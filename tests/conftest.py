from __future__ import annotations

import os
from collections.abc import Callable, Generator
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Connection, Engine, URL, make_url
from sqlalchemy.orm import Session, sessionmaker

from infraestructura.basedatos.base import Base
from infraestructura.basedatos.configuracion import DATABASE_URL
from infraestructura.basedatos.unidad_trabajo import UnidadDeTrabajoSQLAlchemy

# Registrar todos los modelos en Base.metadata antes de crear el esquema.
from infraestructura.basedatos.modelos import (  # noqa: E402, F401
    categoria_modelo,
    cliente_modelo,
    compra_modelo,
    medio_pago_modelo,
    producto_modelo,
    proveedor_modelo,
    usuario_modelo,
    venta_modelo,
)


SessionFactory = sessionmaker[Session]
UoWFactory = Callable[[], UnidadDeTrabajoSQLAlchemy]
PublicSchemaState = tuple[
    tuple[tuple[str, str], ...],
    tuple[tuple[str, str, str, str], ...],
    tuple[str, ...] | None,
]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"
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


class PasswordHasherFake:
    def __init__(self) -> None:
        self.hash_generado = "hash-determinista"
        self.resultado_verificacion = True
        self.passwords_hasheadas: list[str] = []
        self.verificaciones: list[tuple[str, str]] = []

    def generar_hash(self, password: str) -> str:
        self.passwords_hasheadas.append(password)
        return self.hash_generado

    def verificar(self, password: str, password_hash: str) -> bool:
        self.verificaciones.append((password, password_hash))
        return self.resultado_verificacion


@pytest.fixture
def password_hasher_fake() -> PasswordHasherFake:
    return PasswordHasherFake()


def _identidad_base(url: URL) -> tuple[str | None, str | None, int | None, str | None]:
    return url.username, url.host, url.port, url.database


def _obtener_url_base_pruebas() -> URL:
    valor = os.getenv("TEST_DATABASE_URL")
    if not valor:
        pytest.skip(
            "Integración omitida: configurá TEST_DATABASE_URL con una base "
            "PostgreSQL exclusiva para tests."
        )

    url = make_url(valor)
    if url.drivername != "postgresql+psycopg":
        raise pytest.UsageError(
            "TEST_DATABASE_URL debe usar el driver postgresql+psycopg."
        )

    nombre_base = (url.database or "").lower()
    if "test" not in nombre_base:
        raise pytest.UsageError(
            "La base indicada por TEST_DATABASE_URL debe incluir 'test' en "
            "su nombre."
        )

    if _identidad_base(url) == _identidad_base(make_url(DATABASE_URL)):
        raise pytest.UsageError(
            "TEST_DATABASE_URL apunta a la misma base configurada para "
            "desarrollo."
        )

    return url


@pytest.fixture(scope="session")
def test_database_url() -> URL:
    return _obtener_url_base_pruebas()


def _capturar_estado_public(connection: Connection) -> PublicSchemaState:
    relaciones = tuple(
        connection.execute(
            text(
                """
                SELECT clase.relname, clase.relkind
                FROM pg_catalog.pg_class AS clase
                JOIN pg_catalog.pg_namespace AS esquema
                  ON esquema.oid = clase.relnamespace
                WHERE esquema.nspname = 'public'
                ORDER BY clase.relname, clase.relkind
                """
            )
        ).tuples()
    )
    constraints = tuple(
        connection.execute(
            text(
                """
                SELECT restriccion.conname,
                       restriccion.contype,
                       tabla.relname,
                       pg_catalog.pg_get_constraintdef(restriccion.oid)
                FROM pg_catalog.pg_constraint AS restriccion
                JOIN pg_catalog.pg_class AS tabla
                  ON tabla.oid = restriccion.conrelid
                JOIN pg_catalog.pg_namespace AS esquema
                  ON esquema.oid = tabla.relnamespace
                WHERE esquema.nspname = 'public'
                ORDER BY restriccion.conname, tabla.relname
                """
            )
        ).tuples()
    )
    tablas_public = {
        nombre for nombre, tipo in relaciones if tipo in {"p", "r"}
    }
    versiones = None
    if "alembic_version" in tablas_public:
        versiones = tuple(
            connection.execute(
                text(
                    "SELECT version_num FROM public.alembic_version "
                    "ORDER BY version_num"
                )
            ).scalars()
        )
    return relaciones, constraints, versiones


@pytest.fixture(scope="session")
def public_schema_state(test_database_url: URL) -> PublicSchemaState:
    engine = create_engine(test_database_url)
    try:
        with engine.connect() as connection:
            state = _capturar_estado_public(connection)
    finally:
        engine.dispose()

    tablas_public = {
        nombre for nombre, tipo in state[0] if tipo in {"p", "r"}
    }
    prohibidas = tablas_public & (EXPECTED_TABLES | {"alembic_version"})
    if prohibidas:
        raise pytest.UsageError(
            "La base de tests debe tener public libre de tablas de la "
            f"aplicación y de Alembic. Encontradas: {sorted(prohibidas)}."
        )
    return state


@pytest.fixture(scope="session")
def test_schema() -> str:
    return f"pytest_{uuid4().hex}"


def _configurar_alembic(connection: Connection, schema: str) -> Config:
    alembic_config = Config(str(ALEMBIC_INI))
    alembic_config.attributes["connection"] = connection
    alembic_config.attributes["version_table_schema"] = schema
    return alembic_config


def _validar_schema_migrado(
    connection: Connection,
    schema: str,
    alembic_config: Config,
) -> None:
    tablas = set(inspect(connection).get_table_names(schema=schema))
    esperadas = EXPECTED_TABLES | {"alembic_version"}
    if tablas != esperadas:
        raise RuntimeError(
            "Alembic no creó exactamente las tablas esperadas en el schema "
            f"temporal. Faltantes: {sorted(esperadas - tablas)}. "
            f"Inesperadas: {sorted(tablas - esperadas)}."
        )

    head = ScriptDirectory.from_config(alembic_config).get_current_head()
    revision_actual = MigrationContext.configure(
        connection,
        opts={"version_table_schema": schema},
    ).get_current_revision()
    version_num = connection.exec_driver_sql(
        f'SELECT version_num FROM "{schema}".alembic_version'
    ).scalar_one()
    if revision_actual != head or version_num != head:
        raise RuntimeError(
            "El schema temporal no quedó en Alembic head. "
            f"Head: {head}; revisión actual: {revision_actual}; "
            f"alembic_version: {version_num}."
        )


@pytest.fixture(scope="session")
def test_engine(
    test_database_url: URL,
    test_schema: str,
    public_schema_state: PublicSchemaState,
) -> Generator[Engine, None, None]:
    bootstrap_engine = create_engine(test_database_url)
    try:
        with bootstrap_engine.begin() as connection:
            connection.exec_driver_sql(f'CREATE SCHEMA "{test_schema}"')
    finally:
        bootstrap_engine.dispose()

    engine = create_engine(
        test_database_url,
        pool_pre_ping=True,
        connect_args={"options": f"-csearch_path={test_schema}"},
    )

    isolation_error: BaseException | None = None
    try:
        with engine.begin() as connection:
            current_schema = connection.exec_driver_sql(
                "SELECT current_schema()"
            ).scalar_one()
            if current_schema != test_schema:
                raise RuntimeError(
                    "La conexión de integración no quedó aislada en el "
                    f"schema temporal. Esperado: {test_schema}; "
                    f"obtenido: {current_schema}."
                )

            alembic_config = _configurar_alembic(connection, test_schema)
            command.upgrade(alembic_config, "head")
            _validar_schema_migrado(
                connection,
                test_schema,
                alembic_config,
            )
            if _capturar_estado_public(connection) != public_schema_state:
                raise RuntimeError(
                    "La ejecución de Alembic modificó el schema public de "
                    "la base de tests."
                )
        yield engine
    finally:
        try:
            with engine.connect() as connection:
                if _capturar_estado_public(connection) != public_schema_state:
                    isolation_error = RuntimeError(
                        "La suite de integración modificó el schema public "
                        "de la base de tests."
                    )
        except BaseException as exc:
            isolation_error = exc
        engine.dispose()
        cleanup_engine = create_engine(test_database_url)
        try:
            with cleanup_engine.begin() as connection:
                connection.exec_driver_sql(
                    f'DROP SCHEMA IF EXISTS "{test_schema}" CASCADE'
                )
        finally:
            cleanup_engine.dispose()
        if isolation_error is not None:
            raise isolation_error


@pytest.fixture(scope="session")
def test_session_factory(test_engine: Engine) -> SessionFactory:
    return sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest.fixture(autouse=True)
def limpiar_integracion(
    request: pytest.FixtureRequest,
) -> Generator[None, None, None]:
    if request.node.get_closest_marker("integration") is None:
        yield
        return

    engine: Engine = request.getfixturevalue("test_engine")
    yield

    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())


@pytest.fixture
def db_session(
    test_session_factory: SessionFactory,
) -> Generator[Session, None, None]:
    session = test_session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def uow(
    test_session_factory: SessionFactory,
) -> Generator[UnidadDeTrabajoSQLAlchemy, None, None]:
    with UnidadDeTrabajoSQLAlchemy(test_session_factory) as unidad:
        yield unidad


@pytest.fixture
def uow_factory(test_session_factory: SessionFactory) -> UoWFactory:
    return lambda: UnidadDeTrabajoSQLAlchemy(test_session_factory)


@pytest.fixture
def api_client() -> Generator[TestClient, None, None]:
    from main import app

    app.dependency_overrides.clear()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def api_client_db(
    test_session_factory: SessionFactory,
) -> Generator[TestClient, None, None]:
    from api.dependencias import obtener_uow
    from main import app

    def override_uow():
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as unidad:
            yield unidad

    app.dependency_overrides.clear()
    app.dependency_overrides[obtener_uow] = override_uow
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
