from decimal import Decimal

import pytest
from sqlalchemy import func, select

from aplicacion.casos_de_uso.ventas.crear_venta import CrearVenta
from dominio.excepciones import EntidadNoEncontrada, ErrorDeValidacion
from infraestructura.basedatos.modelos.categoria_modelo import CategoriaModelo
from infraestructura.basedatos.modelos.medio_pago_modelo import MedioPagoModelo
from infraestructura.basedatos.modelos.producto_modelo import ProductoModelo
from infraestructura.basedatos.modelos.usuario_modelo import UsuarioModelo
from infraestructura.basedatos.modelos.venta_modelo import (
    VentaDetalleModelo,
    VentaModelo,
)
from infraestructura.repositorios.repositorio_producto_sqlalchemy import (
    RepositorioProductoSQLAlchemy,
)
from infraestructura.repositorios.repositorio_venta_sqlalchemy import (
    RepositorioVentaSQLAlchemy,
)


pytestmark = pytest.mark.integration


def _crear_datos_base(session_factory, stock_segundo: int = 5):
    with session_factory() as session:
        categoria = CategoriaModelo(nombre="Bebidas")
        usuario = UsuarioModelo(
            apellido="Pérez",
            nombre="Ana",
            dni="12345678",
            email="ana@example.com",
            password_hash="hash-de-prueba",
            rol="empleado",
        )
        medio = MedioPagoModelo(nombre="Efectivo")
        session.add_all([categoria, usuario, medio])
        session.flush()

        primero = ProductoModelo(
            codigo_barras="7791000000001",
            nombre="Agua",
            precio_venta=Decimal("1000.00"),
            precio_compra=Decimal("600.00"),
            stock=10,
            id_categoria=categoria.id_categoria,
        )
        segundo = ProductoModelo(
            codigo_barras="7791000000002",
            nombre="Jugo",
            precio_venta=Decimal("1500.00"),
            precio_compra=Decimal("900.00"),
            stock=stock_segundo,
            id_categoria=categoria.id_categoria,
        )
        session.add_all([primero, segundo])
        session.commit()
        return usuario.id_usuario, medio.id_medio_pago, primero.id_producto, segundo.id_producto


def test_crear_venta_real_con_varios_productos(
    test_session_factory,
    uow_factory,
):
    id_usuario, id_medio, id_primero, id_segundo = _crear_datos_base(
        test_session_factory
    )

    with uow_factory() as uow:
        repo_venta = RepositorioVentaSQLAlchemy(uow.session)
        repo_producto = RepositorioProductoSQLAlchemy(uow.session)
        venta = CrearVenta(repo_venta, repo_producto).ejecutar(
            id_usuario=id_usuario,
            id_medio_pago=id_medio,
            detalles=[
                {"id_producto": id_primero, "cantidad": 2},
                {"id_producto": id_segundo, "cantidad": 3},
            ],
        )

    with test_session_factory() as session:
        assert session.get(ProductoModelo, id_primero).stock == 8
        assert session.get(ProductoModelo, id_segundo).stock == 2
        assert session.scalar(select(func.count()).select_from(VentaModelo)) == 1
        assert session.scalar(select(func.count()).select_from(VentaDetalleModelo)) == 2
        assert venta.total == Decimal("6500.00")
        assert isinstance(venta.total, Decimal)


def test_fallo_intermedio_revierte_stocks_venta_y_detalles(
    test_session_factory,
    uow_factory,
):
    id_usuario, id_medio, id_primero, id_segundo = _crear_datos_base(
        test_session_factory,
        stock_segundo=1,
    )

    with pytest.raises(ErrorDeValidacion, match="Stock insuficiente"):
        with uow_factory() as uow:
            repo_venta = RepositorioVentaSQLAlchemy(uow.session)
            repo_producto = RepositorioProductoSQLAlchemy(uow.session)
            CrearVenta(repo_venta, repo_producto).ejecutar(
                id_usuario=id_usuario,
                id_medio_pago=id_medio,
                detalles=[
                    {"id_producto": id_primero, "cantidad": 2},
                    {"id_producto": id_segundo, "cantidad": 2},
                ],
            )

    with test_session_factory() as session:
        assert session.get(ProductoModelo, id_primero).stock == 10
        assert session.get(ProductoModelo, id_segundo).stock == 1
        assert session.scalar(select(func.count()).select_from(VentaModelo)) == 0
        assert session.scalar(select(func.count()).select_from(VentaDetalleModelo)) == 0


def test_fallo_al_persistir_venta_revierte_ambos_stocks(
    test_session_factory,
    uow_factory,
):
    id_usuario, _, id_primero, id_segundo = _crear_datos_base(
        test_session_factory
    )

    with pytest.raises(EntidadNoEncontrada, match="medio de pago"):
        with uow_factory() as uow:
            repo_venta = RepositorioVentaSQLAlchemy(uow.session)
            repo_producto = RepositorioProductoSQLAlchemy(uow.session)
            CrearVenta(repo_venta, repo_producto).ejecutar(
                id_usuario=id_usuario,
                id_medio_pago=999999,
                detalles=[
                    {"id_producto": id_primero, "cantidad": 2},
                    {"id_producto": id_segundo, "cantidad": 3},
                ],
            )

    with test_session_factory() as session:
        assert session.get(ProductoModelo, id_primero).stock == 10
        assert session.get(ProductoModelo, id_segundo).stock == 5
        assert session.scalar(select(func.count()).select_from(VentaModelo)) == 0
        assert session.scalar(select(func.count()).select_from(VentaDetalleModelo)) == 0
