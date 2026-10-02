"""Caracterización unitaria de la política monetaria Decimal."""

from decimal import Decimal

import pytest

from aplicacion.casos_de_uso.compras.crear_compra import CrearCompra
from aplicacion.casos_de_uso.ventas.crear_venta import CrearVenta
from dominio.entidades.producto import Producto
from dominio.excepciones import ErrorDeValidacion
from dominio.validaciones import validar_precio


class RepositorioProductoFake:
    def __init__(self, productos: list[Producto]):
        self.productos = {producto.id_producto: producto for producto in productos}
        self.actualizados: list[Producto] = []

    def obtener_por_id(self, id_producto: int) -> Producto | None:
        return self.productos.get(id_producto)

    def obtener_para_modificar_stock(
        self,
        ids_producto,
    ) -> dict[int, Producto]:
        return {
            id_producto: self.productos[id_producto]
            for id_producto in sorted(set(ids_producto))
            if id_producto in self.productos
        }

    def actualizar_stocks(self, nuevos_stocks) -> None:
        for id_producto in sorted(nuevos_stocks):
            producto = self.productos[id_producto]
            producto.stock = nuevos_stocks[id_producto]
            self.actualizados.append(producto)


class RepositorioOperacionFake:
    def __init__(self):
        self.creadas = []

    def crear(self, operacion):
        self.creadas.append(operacion)
        return operacion


def _producto(
    id_producto: int,
    precio_venta: Decimal,
    precio_compra: Decimal = Decimal("8.88"),
    stock: int = 10,
) -> Producto:
    return Producto(
        id_producto=id_producto,
        nombre=f"Producto {id_producto}",
        precio_venta=precio_venta,
        precio_compra=precio_compra,
        stock=stock,
    )


def test_crear_venta_preserva_subtotal_y_total_con_dos_decimales():
    producto = _producto(1, precio_venta=Decimal("12.34"))
    repo_producto = RepositorioProductoFake([producto])

    venta = CrearVenta(
        RepositorioOperacionFake(),
        repo_producto,
    ).ejecutar(
        id_usuario=1,
        id_medio_pago=1,
        detalles=[{"id_producto": 1, "cantidad": 3}],
    )

    assert venta.detalles[0].precio_unitario == Decimal("12.34")
    assert venta.detalles[0].subtotal == Decimal("37.02")
    assert venta.total == Decimal("37.02")
    assert isinstance(venta.detalles[0].subtotal, Decimal)
    assert isinstance(venta.total, Decimal)


def test_crear_venta_aplica_round_half_up_a_2675_y_2685():
    productos = [
        _producto(1, precio_venta=Decimal("2.675")),
        _producto(2, precio_venta=Decimal("2.685")),
    ]

    venta = CrearVenta(
        RepositorioOperacionFake(),
        RepositorioProductoFake(productos),
    ).ejecutar(
        id_usuario=1,
        id_medio_pago=1,
        detalles=[
            {"id_producto": 1, "cantidad": 1},
            {"id_producto": 2, "cantidad": 1},
        ],
    )

    assert [detalle.precio_unitario for detalle in venta.detalles] == [
        Decimal("2.68"),
        Decimal("2.69"),
    ]
    assert [detalle.subtotal for detalle in venta.detalles] == [
        Decimal("2.68"),
        Decimal("2.69"),
    ]
    assert venta.total == Decimal("5.37")


def test_crear_compra_preserva_precio_recibido_y_no_usa_precio_del_producto():
    producto = _producto(
        1,
        precio_venta=Decimal("15.00"),
        precio_compra=Decimal("8.88"),
        stock=2,
    )
    repo_producto = RepositorioProductoFake([producto])

    compra = CrearCompra(
        RepositorioOperacionFake(),
        repo_producto,
    ).ejecutar(
        id_proveedor=1,
        id_usuario=1,
        detalles=[
            {
                "id_producto": 1,
                "cantidad": 2,
                "precio_unitario": Decimal("12.34"),
            }
        ],
    )

    assert compra.detalles[0].precio_unitario == Decimal("12.34")
    assert compra.detalles[0].precio_unitario != producto.precio_compra
    assert compra.detalles[0].subtotal == Decimal("24.68")
    assert compra.total == Decimal("24.68")
    assert producto.precio_compra == Decimal("8.88")
    assert producto.stock == 4
    assert isinstance(compra.total, Decimal)


def test_crear_compra_normaliza_precio_antes_de_calcular_subtotal():
    producto = _producto(1, precio_venta=Decimal("2.00"), stock=0)

    compra = CrearCompra(
        RepositorioOperacionFake(),
        RepositorioProductoFake([producto]),
    ).ejecutar(
        id_proveedor=1,
        id_usuario=1,
        detalles=[
            {
                "id_producto": 1,
                "cantidad": 3,
                "precio_unitario": Decimal("1.005"),
            }
        ],
    )

    assert compra.detalles[0].precio_unitario == Decimal("1.01")
    assert compra.detalles[0].subtotal == Decimal("3.03")
    assert compra.total == Decimal("3.03")


def test_validar_precio_preserva_cero_como_valido():
    validar_precio(Decimal("0.00"), "precio")


def test_validar_precio_preserva_rechazo_de_negativos():
    with pytest.raises(ErrorDeValidacion, match="no puede ser negativo"):
        validar_precio(Decimal("-0.01"), "precio")


@pytest.mark.parametrize("valor", [Decimal("NaN"), Decimal("Infinity")])
def test_validar_precio_rechaza_valores_no_finitos(valor):
    with pytest.raises(ErrorDeValidacion, match="decimal finito"):
        validar_precio(valor, "precio")
