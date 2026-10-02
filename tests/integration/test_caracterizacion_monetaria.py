from datetime import date, datetime
from decimal import Decimal

import pytest

from api.dependencias import obtener_usuario_actual
from aplicacion.casos_de_uso.compras.crear_compra import CrearCompra
from aplicacion.casos_de_uso.productos.actualizar_producto import ActualizarProducto
from aplicacion.casos_de_uso.productos.crear_producto import CrearProducto
from infraestructura.basedatos.modelos.compra_modelo import (
    CompraDetalleModelo,
    CompraModelo,
)
from infraestructura.basedatos.modelos.medio_pago_modelo import MedioPagoModelo
from infraestructura.basedatos.modelos.producto_modelo import ProductoModelo
from infraestructura.basedatos.modelos.proveedor_modelo import ProveedorModelo
from infraestructura.basedatos.modelos.usuario_modelo import UsuarioModelo
from infraestructura.basedatos.modelos.venta_modelo import VentaModelo
from infraestructura.repositorios.repositorio_compra_sqlalchemy import (
    RepositorioCompraSQLAlchemy,
)
from infraestructura.repositorios.repositorio_producto_sqlalchemy import (
    RepositorioProductoSQLAlchemy,
)
from infraestructura.servicios.servicio_reportes import (
    obtener_reporte_compras_por_dia,
    obtener_reporte_ventas_por_dia,
)
from main import app


pytestmark = pytest.mark.integration


def _crear_referencias(session_factory):
    with session_factory() as session:
        usuario = UsuarioModelo(
            apellido="Perez",
            nombre="Ana",
            dni="22333444",
            email="ana.monetaria@example.com",
            password_hash="hash-de-prueba",
            rol="jefe",
        )
        proveedor = ProveedorModelo(
            razon_social="Proveedor Monetario SA",
            cuit_cuil="20333444556",
        )
        producto = ProductoModelo(
            codigo_barras="7792000000001",
            nombre="Producto monetario",
            precio_venta=Decimal("15.00"),
            precio_compra=Decimal("8.88"),
            stock=1,
        )
        session.add_all([usuario, proveedor, producto])
        session.commit()
        return usuario.id_usuario, proveedor.id_proveedor, producto.id_producto


def test_producto_usa_decimal_normalizado_en_dominio_y_orm_al_crear_y_actualizar(
    db_session,
):
    repo = RepositorioProductoSQLAlchemy(db_session)
    creado = CrearProducto(repo).ejecutar(
        nombre="Precio caracterizado",
        precio_venta=Decimal("10.125"),
        precio_compra=Decimal("5.555"),
        stock=1,
        codigo_barras="7792000000002",
    )

    assert creado.precio_venta == Decimal("10.13")
    assert creado.precio_compra == Decimal("5.56")
    assert isinstance(creado.precio_venta, Decimal)
    assert isinstance(creado.precio_compra, Decimal)

    db_session.commit()
    db_session.expire_all()
    modelo = db_session.get(ProductoModelo, creado.id_producto)
    assert modelo is not None
    assert modelo.precio_venta == Decimal("10.13")
    assert modelo.precio_compra == Decimal("5.56")
    assert isinstance(modelo.precio_venta, Decimal)
    assert isinstance(modelo.precio_compra, Decimal)

    dominio = repo.obtener_por_id(creado.id_producto)
    assert dominio is not None
    assert dominio.precio_venta == Decimal("10.13")
    assert dominio.precio_compra == Decimal("5.56")
    assert isinstance(dominio.precio_venta, Decimal)
    assert isinstance(dominio.precio_compra, Decimal)

    actualizado = ActualizarProducto(repo).ejecutar(
        id_producto=creado.id_producto,
        nombre="Precio actualizado",
        precio_venta=Decimal("20.345"),
        precio_compra=Decimal("7.895"),
        codigo_barras="7792000000002",
    )
    assert actualizado.precio_venta == Decimal("20.35")
    assert actualizado.precio_compra == Decimal("7.90")
    assert isinstance(actualizado.precio_venta, Decimal)

    db_session.commit()
    db_session.expire_all()
    modelo_actualizado = db_session.get(ProductoModelo, creado.id_producto)
    assert modelo_actualizado is not None
    assert modelo_actualizado.precio_venta == Decimal("20.35")
    assert modelo_actualizado.precio_compra == Decimal("7.90")


def test_compra_normaliza_precio_y_persiste_subtotal_consistente(
    test_session_factory,
    uow_factory,
):
    id_usuario, id_proveedor, id_producto = _crear_referencias(
        test_session_factory
    )

    with uow_factory() as uow:
        compra = CrearCompra(
            RepositorioCompraSQLAlchemy(uow.session),
            RepositorioProductoSQLAlchemy(uow.session),
        ).ejecutar(
            id_proveedor=id_proveedor,
            id_usuario=id_usuario,
            detalles=[
                {
                    "id_producto": id_producto,
                    "cantidad": 3,
                    "precio_unitario": Decimal("1.005"),
                }
            ],
        )

    assert compra.detalles[0].precio_unitario == Decimal("1.01")
    assert compra.detalles[0].subtotal == Decimal("3.03")
    assert isinstance(compra.detalles[0].precio_unitario, Decimal)

    with test_session_factory() as session:
        detalle = session.query(CompraDetalleModelo).one()
        assert detalle.precio_unitario == Decimal("1.01")
        assert detalle.subtotal == Decimal("3.03")
        assert detalle.precio_unitario * detalle.cantidad == Decimal("3.03")
        assert detalle.precio_unitario * detalle.cantidad == detalle.subtotal


def test_legacy_reportes_preservan_suma_secuencial_de_floats(db_session):
    usuario = UsuarioModelo(
        apellido="Perez",
        nombre="Ana",
        dni="32333444",
        email="reportes.monetarios@example.com",
        password_hash="hash-de-prueba",
        rol="jefe",
    )
    medio = MedioPagoModelo(nombre="Efectivo")
    proveedor = ProveedorModelo(
        razon_social="Proveedor Reportes SA",
        cuit_cuil="20333444557",
    )
    db_session.add_all([usuario, medio, proveedor])
    db_session.flush()

    fecha_reporte = date(2025, 6, 15)
    db_session.add_all(
        [
            VentaModelo(
                fecha=datetime(2025, 6, 15, 9, 0),
                id_usuario=usuario.id_usuario,
                id_medio_pago=medio.id_medio_pago,
                total=Decimal("0.10"),
            ),
            VentaModelo(
                fecha=datetime(2025, 6, 15, 10, 0),
                id_usuario=usuario.id_usuario,
                id_medio_pago=medio.id_medio_pago,
                total=Decimal("0.20"),
            ),
        ]
    )
    db_session.add_all(
        [
            CompraModelo(
                fecha=datetime(2025, 6, 15, 11, 0),
                id_proveedor=proveedor.id_proveedor,
                id_usuario=usuario.id_usuario,
                total=Decimal("0.10"),
            ),
            CompraModelo(
                fecha=datetime(2025, 6, 15, 12, 0),
                id_proveedor=proveedor.id_proveedor,
                id_usuario=usuario.id_usuario,
                total=Decimal("0.20"),
            ),
        ]
    )
    db_session.flush()

    reporte_ventas = obtener_reporte_ventas_por_dia(
        db_session,
        fecha_reporte,
    )
    reporte_compras = obtener_reporte_compras_por_dia(
        db_session,
        fecha_reporte,
    )

    assert [venta["total"] for venta in reporte_ventas["ventas"]] == [0.1, 0.2]
    assert reporte_ventas["total_dia"] == 0.30000000000000004
    assert isinstance(reporte_ventas["total_dia"], float)
    assert [compra["total"] for compra in reporte_compras["compras"]] == [
        0.1,
        0.2,
    ]
    assert reporte_compras["total_dia"] == 0.30000000000000004
    assert isinstance(reporte_compras["total_dia"], float)


def test_reportes_sin_movimientos_preservan_total_float_cero(db_session):
    fecha_sin_movimientos = date(2040, 1, 1)

    ventas = obtener_reporte_ventas_por_dia(
        db_session,
        fecha_sin_movimientos,
    )
    compras = obtener_reporte_compras_por_dia(
        db_session,
        fecha_sin_movimientos,
    )

    assert ventas["ventas"] == []
    assert ventas["cantidad_ventas"] == 0
    assert ventas["total_dia"] == 0.0
    assert isinstance(ventas["total_dia"], float)
    assert compras["compras"] == []
    assert compras["cantidad_compras"] == 0
    assert compras["total_dia"] == 0.0
    assert isinstance(compras["total_dia"], float)


def test_api_producto_preserva_importes_como_json_numbers(api_client_db):
    app.dependency_overrides[obtener_usuario_actual] = lambda: {
        "id_usuario": 1,
        "email": "jefe@example.com",
        "rol": "jefe",
    }

    creada = api_client_db.post(
        "/api/productos/",
        json={
            "nombre": "Producto API monetaria",
            "precio_venta": 12.34,
            "precio_compra": 5.67,
            "stock": 2,
            "codigo_barras": "7792000000003",
        },
    )
    assert creada.status_code == 201
    cuerpo_creado = creada.json()
    assert cuerpo_creado["precio_venta"] == 12.34
    assert cuerpo_creado["precio_compra"] == 5.67
    assert isinstance(cuerpo_creado["precio_venta"], float)
    assert isinstance(cuerpo_creado["precio_compra"], float)

    actualizada = api_client_db.put(
        f'/api/productos/{cuerpo_creado["id_producto"]}',
        json={
            "nombre": "Producto API actualizado",
            "precio_venta": 13.45,
            "precio_compra": 6.78,
            "codigo_barras": "7792000000003",
        },
    )
    assert actualizada.status_code == 200
    cuerpo_actualizado = actualizada.json()
    assert cuerpo_actualizado["precio_venta"] == 13.45
    assert cuerpo_actualizado["precio_compra"] == 6.78
    assert isinstance(cuerpo_actualizado["precio_venta"], float)


def test_api_compra_preserva_request_y_response_como_json_numbers(
    api_client_db,
    test_session_factory,
):
    id_usuario, id_proveedor, id_producto = _crear_referencias(
        test_session_factory
    )
    app.dependency_overrides[obtener_usuario_actual] = lambda: {
        "id_usuario": id_usuario,
        "email": "ana.monetaria@example.com",
        "rol": "jefe",
    }

    respuesta = api_client_db.post(
        "/api/compras/",
        json={
            "id_proveedor": id_proveedor,
            "detalles": [
                {
                    "id_producto": id_producto,
                    "cantidad": 2,
                    "precio_unitario": 12.34,
                }
            ],
        },
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["detalles"][0]["precio_unitario"] == 12.34
    assert cuerpo["detalles"][0]["subtotal"] == 24.68
    assert cuerpo["total"] == 24.68
    assert isinstance(cuerpo["detalles"][0]["precio_unitario"], float)
    assert isinstance(cuerpo["detalles"][0]["subtotal"], float)
    assert isinstance(cuerpo["total"], float)
