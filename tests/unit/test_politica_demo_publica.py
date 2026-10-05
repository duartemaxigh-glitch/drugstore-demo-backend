import importlib
from types import SimpleNamespace

import pytest

from api.dependencias import (
    obtener_password_hasher,
    obtener_repo_categoria,
    obtener_repo_cliente,
    obtener_repo_compra,
    obtener_repo_medio_pago,
    obtener_repo_producto,
    obtener_repo_proveedor,
    obtener_repo_usuario,
    obtener_repo_venta,
    obtener_session,
    obtener_usuario_actual,
)
from api.politica_demo_publica import MENSAJE_BLOQUEO
from aplicacion.casos_de_uso.compras.crear_compra import CrearCompra
from aplicacion.casos_de_uso.ventas.crear_venta import CrearVenta
from infraestructura.basedatos import configuracion
from infraestructura.seguridad.jwt_servicio import crear_token
from main import app


@pytest.fixture
def demo_publica(monkeypatch):
    monkeypatch.setattr(configuracion, "PUBLIC_DEMO_MODE", True)


@pytest.fixture
def modo_normal(monkeypatch):
    monkeypatch.setattr(configuracion, "PUBLIC_DEMO_MODE", False)


def _jefe():
    return {"id_usuario": 1, "email": "jefe@example.com", "rol": "jefe"}


def _bloqueada(respuesta):
    assert respuesta.status_code == 403
    assert respuesta.json() == {"detail": MENSAJE_BLOQUEO}


@pytest.mark.parametrize(
    ("ruta", "dependencia"),
    [
        ("categorias", obtener_repo_categoria),
        ("clientes", obtener_repo_cliente),
        ("proveedores", obtener_repo_proveedor),
        ("productos", obtener_repo_producto),
        ("medios-pago", obtener_repo_medio_pago),
    ],
)
def test_lecturas_de_maestros_siguen_disponibles(
    api_client, demo_publica, ruta, dependencia
):
    app.dependency_overrides[obtener_usuario_actual] = _jefe
    app.dependency_overrides[dependencia] = lambda: SimpleNamespace(
        obtener_todos=lambda: []
    )

    respuesta = api_client.get(f"/api/{ruta}/")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_reportes_conservan_autorizacion_jwt(api_client, demo_publica, monkeypatch):
    from api.rutas import rutas_reportes

    app.dependency_overrides[obtener_session] = lambda: object()
    monkeypatch.setattr(
        rutas_reportes,
        "obtener_reporte_ventas_por_dia",
        lambda session, fecha: {
            "fecha": str(fecha),
            "cantidad_ventas": 0,
            "total_dia": 0,
            "ventas": [],
        },
    )
    jefe = crear_token(1, "jefe@example.com", "jefe")
    empleado = crear_token(2, "empleado@example.com", "empleado")

    permitida = api_client.get(
        "/api/reportes/ventas", headers={"Authorization": f"Bearer {jefe}"}
    )
    rechazada = api_client.get(
        "/api/reportes/ventas", headers={"Authorization": f"Bearer {empleado}"}
    )
    sin_token = api_client.get("/api/reportes/ventas")

    assert permitida.status_code == 200
    assert rechazada.status_code == 403
    assert rechazada.json()["detail"] != MENSAJE_BLOQUEO
    assert sin_token.status_code == 403


def test_login_sigue_disponible(api_client, demo_publica, password_hasher_fake):
    usuario = SimpleNamespace(
        id_usuario=1,
        email="jefe@example.com",
        rol="jefe",
        password_hash="hash",
    )
    app.dependency_overrides[obtener_repo_usuario] = lambda: SimpleNamespace(
        obtener_por_email=lambda email: usuario
    )
    app.dependency_overrides[obtener_password_hasher] = lambda: password_hasher_fake

    respuesta = api_client.post(
        "/api/auth/login",
        json={"email": usuario.email, "password": "demo"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "jefe"
    assert respuesta.json()["token"]


def test_crear_venta_sigue_exigiendo_token(api_client, demo_publica):
    respuesta = api_client.post(
        "/api/ventas/",
        json={"id_medio_pago": 1, "detalles": [{"id_producto": 1, "cantidad": 1}]},
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["detail"] != MENSAJE_BLOQUEO


@pytest.mark.parametrize(
    ("ruta", "dependencia", "caso_de_uso", "datos", "resultado"),
    [
        (
            "/api/ventas/",
            obtener_repo_venta,
            CrearVenta,
            {"id_medio_pago": 1, "detalles": [{"id_producto": 1, "cantidad": 1}]},
            SimpleNamespace(
                id_venta=1, fecha=None, id_usuario=1, id_cliente=None,
                id_medio_pago=1, total=10, detalles=[],
            ),
        ),
        (
            "/api/compras/",
            obtener_repo_compra,
            CrearCompra,
            {
                "id_proveedor": 1,
                "detalles": [
                    {"id_producto": 1, "cantidad": 1, "precio_unitario": "10"}
                ],
            },
            SimpleNamespace(
                id_compra=1, fecha=None, id_proveedor=1, id_usuario=1,
                total=10, detalles=[],
            ),
        ),
    ],
)
def test_crear_ventas_y_compras_sigue_disponible(
    api_client, demo_publica, monkeypatch, ruta, dependencia, caso_de_uso,
    datos, resultado,
):
    llamadas = []

    def ejecutar(self, **kwargs):
        llamadas.append(kwargs)
        return resultado

    monkeypatch.setattr(caso_de_uso, "ejecutar", ejecutar)
    app.dependency_overrides[obtener_usuario_actual] = _jefe
    app.dependency_overrides[dependencia] = lambda: object()
    app.dependency_overrides[obtener_repo_producto] = lambda: object()

    respuesta = api_client.post(ruta, json=datos)

    assert respuesta.status_code == 201
    assert llamadas[0]["id_usuario"] == 1


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [
        ("DELETE", "/api/ventas/1"),
        ("PUT", "/api/ventas/1"),
        ("PATCH", "/api/ventas/1"),
        ("DELETE", "/api/compras/1"),
        ("PUT", "/api/compras/1"),
        ("PATCH", "/api/compras/1"),
        *[
            (metodo, f"/api/{recurso}/{sufijo}")
            for recurso in (
                "productos", "categorias", "clientes", "proveedores",
                "medios-pago",
            )
            for metodo, sufijo in (("POST", ""), ("PUT", "1"),
                                    ("PATCH", "1"), ("DELETE", "1"))
        ],
        ("GET", "/api/usuarios/"),
        ("GET", "/api/usuarios/1"),
        ("POST", "/api/usuarios/"),
        ("PUT", "/api/usuarios/1"),
        ("PATCH", "/api/usuarios/1"),
        ("DELETE", "/api/usuarios/1"),
        ("POST", "/api/auth/recuperar-password"),
        ("POST", "/api/imprimir"),
        ("POST", "/api/productos/alta-rapida"),
        ("POST", "/api/proveedores/alta-rapida"),
        ("POST", "/api/otra-mutacion"),
    ],
)
def test_demo_bloquea_operaciones_no_permitidas(
    api_client, demo_publica, metodo, ruta
):
    _bloqueada(api_client.request(metodo, ruta))


@pytest.mark.parametrize("ruta", ["/api/productos/", "/api/usuarios/"])
def test_cors_preflight_y_documentacion_funcionan(api_client, demo_publica,
                                                  ruta):
    preflight = api_client.options(
        ruta,
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert api_client.get("/docs").status_code == 200
    assert api_client.get("/openapi.json").status_code == 200
    assert api_client.get("/").status_code == 200


def test_respuesta_bloqueada_conserva_cors(api_client, demo_publica):
    respuesta = api_client.post(
        "/api/productos/", headers={"Origin": "http://localhost:3000"}
    )
    _bloqueada(respuesta)
    assert respuesta.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_origins_configurables(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    assert configuracion.obtener_cors_origins() == [
        "http://localhost:3000", "http://localhost:5165"
    ]
    monkeypatch.setenv(
        "CORS_ORIGINS", " http://localhost:3000, , https://demo.example, "
    )
    assert configuracion.obtener_cors_origins() == [
        "http://localhost:3000", "https://demo.example"
    ]


def test_variables_del_deployment_prevalecen_sobre_dotenv(monkeypatch):
    try:
        with monkeypatch.context() as entorno:
            entorno.setenv("PUBLIC_DEMO_MODE", "true")
            entorno.setenv("CORS_ORIGINS", " https://demo.example, , ")
            importlib.reload(configuracion)
            assert configuracion.PUBLIC_DEMO_MODE is True
            assert configuracion.obtener_cors_origins() == ["https://demo.example"]
    finally:
        importlib.reload(configuracion)


def test_public_demo_mode_rechaza_valores_invalidos(monkeypatch):
    try:
        with monkeypatch.context() as entorno:
            entorno.setenv("PUBLIC_DEMO_MODE", "yes")
            with pytest.raises(ValueError, match="true o false"):
                importlib.reload(configuracion)
    finally:
        importlib.reload(configuracion)


def test_modo_normal_conserva_creacion_crud(api_client, modo_normal):
    class RepoCategorias:
        def crear(self, categoria):
            categoria.id_categoria = 1
            return categoria

    app.dependency_overrides[obtener_usuario_actual] = _jefe
    app.dependency_overrides[obtener_repo_categoria] = lambda: RepoCategorias()

    respuesta = api_client.post("/api/categorias/", json={"nombre": "Bebidas"})

    assert respuesta.status_code == 201
    assert respuesta.json() == {"id_categoria": 1, "nombre": "Bebidas"}


def test_modo_normal_usuarios_sigue_exigiendo_jefe(api_client, modo_normal):
    app.dependency_overrides[obtener_repo_usuario] = lambda: SimpleNamespace(
        obtener_todos=lambda: []
    )
    empleado = crear_token(2, "empleado@example.com", "empleado")
    jefe = crear_token(1, "jefe@example.com", "jefe")

    rechazado = api_client.get(
        "/api/usuarios/", headers={"Authorization": f"Bearer {empleado}"}
    )
    permitido = api_client.get(
        "/api/usuarios/", headers={"Authorization": f"Bearer {jefe}"}
    )

    assert rechazado.status_code == 403
    assert rechazado.json()["detail"] != MENSAJE_BLOQUEO
    assert permitido.status_code == 200
    assert permitido.json() == []


def test_modo_normal_conserva_recuperacion(api_client, modo_normal,
                                           password_hasher_fake):
    app.dependency_overrides[obtener_repo_usuario] = lambda: SimpleNamespace()
    app.dependency_overrides[obtener_password_hasher] = lambda: password_hasher_fake
    respuesta = api_client.post(
        "/api/auth/recuperar-password",
        json={
            "dni": "12345678", "email": "ana@example.com",
            "nueva_password": "12345", "repetir_password": "12345",
        },
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] != MENSAJE_BLOQUEO


@pytest.mark.parametrize("ruta", ["/api/ventas/1", "/api/compras/1"])
def test_modo_normal_conserva_eliminaciones(api_client, modo_normal, ruta):
    app.dependency_overrides[obtener_usuario_actual] = _jefe
    app.dependency_overrides[obtener_repo_producto] = lambda: object()
    dependencia = obtener_repo_venta if "ventas" in ruta else obtener_repo_compra
    app.dependency_overrides[dependencia] = lambda: SimpleNamespace(
        obtener_para_eliminar=lambda id_registro: None
    )

    respuesta = api_client.delete(ruta)

    # Sin un registro real, la ruta conserva su 404 de dominio.
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] != MENSAJE_BLOQUEO


def test_modo_normal_no_bloquea_impresion(api_client, modo_normal):
    # El cuerpo vacío se rechaza antes de abrir el dispositivo físico.
    respuesta = api_client.post("/api/imprimir", json={"texto": ""})
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Texto vacío."
