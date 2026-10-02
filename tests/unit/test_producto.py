from decimal import Decimal

import pytest

from dominio.entidades.producto import Producto
from dominio.excepciones import ErrorDeValidacion


def test_producto_valido_acepta_stock_y_precios_no_negativos():
    producto = Producto(
        nombre="Agua",
        precio_venta=Decimal("1500.50"),
        precio_compra=Decimal("900.25"),
        stock=0,
    )

    producto.validar()


@pytest.mark.parametrize(
    ("cambios", "mensaje"),
    [
        ({"nombre": "  "}, "nombre"),
        ({"precio_venta": Decimal("-0.01")}, "precio_venta"),
        ({"precio_compra": "no-numérico"}, "precio_compra"),
        ({"stock": -1}, "stock"),
        ({"stock": 1.5}, "stock"),
    ],
)
def test_producto_invalido(cambios, mensaje):
    datos = {
        "nombre": "Agua",
        "precio_venta": Decimal("1500.50"),
        "precio_compra": Decimal("900.25"),
        "stock": 2,
    }
    datos.update(cambios)

    with pytest.raises(ErrorDeValidacion, match=mensaje):
        Producto(**datos).validar()
