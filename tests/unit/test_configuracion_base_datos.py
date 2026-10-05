import importlib

import pytest
from sqlalchemy import URL

import conftest
from infraestructura.basedatos import configuracion


def _url_demo(nombre: str) -> URL:
    return URL.create(
        "postgresql+psycopg",
        username="demo",
        password="placeholder",
        host="example.invalid",
        database=nombre,
    )


def test_database_url_explicita_tiene_prioridad_sobre_db_individuales(monkeypatch):
    url = _url_demo("demo")
    try:
        with monkeypatch.context() as entorno:
            entorno.setenv("DATABASE_URL", url.render_as_string(hide_password=False))
            entorno.setenv("TEST_DATABASE_URL", _url_demo("demo_test").render_as_string(hide_password=False))
            importlib.reload(configuracion)
            assert configuracion.DATABASE_URL == url
    finally:
        importlib.reload(configuracion)


def test_database_url_normal_no_depende_de_test_database_url(monkeypatch):
    original = configuracion.DATABASE_URL
    try:
        with monkeypatch.context() as entorno:
            entorno.delenv("DATABASE_URL", raising=False)
            entorno.setenv("TEST_DATABASE_URL", _url_demo("otra_test").render_as_string(hide_password=False))
            importlib.reload(configuracion)
            assert configuracion.DATABASE_URL == original
    finally:
        importlib.reload(configuracion)


def test_integracion_rechaza_url_igual(monkeypatch):
    url = _url_demo("demo_test")
    monkeypatch.setattr(conftest, "DATABASE_URL", url)
    monkeypatch.setenv("TEST_DATABASE_URL", url.render_as_string(hide_password=False))

    with pytest.raises(pytest.UsageError, match="misma base"):
        conftest._obtener_url_base_pruebas()


def test_integracion_sin_url_de_test_falla_de_forma_segura(monkeypatch):
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)

    with pytest.raises(pytest.skip.Exception, match="TEST_DATABASE_URL"):
        conftest._obtener_url_base_pruebas()


def test_integracion_acepta_url_distinta(monkeypatch):
    normal = _url_demo("demo")
    pruebas = _url_demo("demo_test")
    monkeypatch.setattr(conftest, "DATABASE_URL", normal)
    monkeypatch.setenv(
        "TEST_DATABASE_URL", pruebas.render_as_string(hide_password=False)
    )

    assert conftest._obtener_url_base_pruebas() == pruebas
