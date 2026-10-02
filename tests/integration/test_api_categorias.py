import pytest

from api.dependencias import obtener_usuario_actual
from main import app


pytestmark = pytest.mark.integration


def test_crud_categoria(api_client_db):
    app.dependency_overrides[obtener_usuario_actual] = lambda: {
        "id_usuario": 1,
        "email": "jefe@example.com",
        "rol": "jefe",
    }

    creada = api_client_db.post(
        "/api/categorias/",
        json={"nombre": "Bebidas"},
    )
    assert creada.status_code == 201
    id_categoria = creada.json()["id_categoria"]

    listado = api_client_db.get("/api/categorias/")
    assert listado.status_code == 200
    assert listado.json() == [
        {"id_categoria": id_categoria, "nombre": "Bebidas"}
    ]

    actualizada = api_client_db.put(
        f"/api/categorias/{id_categoria}",
        json={"nombre": "Almacén"},
    )
    assert actualizada.status_code == 200
    assert actualizada.json() == {
        "id_categoria": id_categoria,
        "nombre": "Almacén",
    }

    eliminada = api_client_db.delete(f"/api/categorias/{id_categoria}")
    assert eliminada.status_code == 204

    inexistente = api_client_db.get(f"/api/categorias/{id_categoria}")
    assert inexistente.status_code == 404
