from decimal import Decimal

import pytest

from aplicacion.casos_de_uso.ventas.crear_venta import CrearVenta
from dominio.entidades.producto import Producto
from dominio.excepciones import EntidadNoEncontrada, ErrorDeValidacion


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


class RepositorioVentaFake:
    def __init__(self):
        self.creadas = []

    def crear(self, venta):
        venta.id_venta = 1
        self.creadas.append(venta)
        return venta


def _producto(stock: int = 5) -> Producto:
    return Producto(
        id_producto=10,
        nombre="Agua",
        precio_venta=Decimal("1250.50"),
        precio_compra=Decimal("800.00"),
        stock=stock,
    )


def test_crear_venta_con_stock_suficiente():
    producto = _producto()
    repo_producto = RepositorioProductoFake([producto])
    repo_venta = RepositorioVentaFake()

    venta = CrearVenta(repo_venta, repo_producto).ejecutar(
        id_usuario=1,
        id_medio_pago=2,
        detalles=[{"id_producto": 10, "cantidad": 2}],
    )

    assert venta.id_venta == 1
    assert venta.total == Decimal("2501.00")
    assert venta.detalles[0].precio_unitario == Decimal("1250.50")
    assert isinstance(venta.total, Decimal)
    assert isinstance(venta.detalles[0].precio_unitario, Decimal)
    assert producto.stock == 3
    assert repo_producto.actualizados == [producto]
    assert repo_venta.creadas == [venta]


def test_crear_venta_con_producto_inexistente():
    repo_producto = RepositorioProductoFake([])
    repo_venta = RepositorioVentaFake()

    with pytest.raises(EntidadNoEncontrada, match="producto con id 99"):
        CrearVenta(repo_venta, repo_producto).ejecutar(
            id_usuario=1,
            id_medio_pago=2,
            detalles=[{"id_producto": 99, "cantidad": 1}],
        )

    assert repo_producto.actualizados == []
    assert repo_venta.creadas == []


def test_crear_venta_con_stock_insuficiente():
    producto = _producto(stock=1)
    repo_producto = RepositorioProductoFake([producto])
    repo_venta = RepositorioVentaFake()

    with pytest.raises(ErrorDeValidacion, match="Stock insuficiente"):
        CrearVenta(repo_venta, repo_producto).ejecutar(
            id_usuario=1,
            id_medio_pago=2,
            detalles=[{"id_producto": 10, "cantidad": 2}],
        )

    assert producto.stock == 1
    assert repo_producto.actualizados == []
    assert repo_venta.creadas == []
