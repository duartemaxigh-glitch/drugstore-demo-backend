from dominio.entidades.producto import Producto
from infraestructura.basedatos.modelos.producto_modelo import ProductoModelo


def a_dominio(modelo: ProductoModelo) -> Producto:
    return Producto(
        id_producto=modelo.id_producto,
        codigo_barras=modelo.codigo_barras,
        nombre=modelo.nombre,
        precio_venta=modelo.precio_venta,
        precio_compra=modelo.precio_compra,
        stock=modelo.stock,
        id_categoria=modelo.id_categoria,
    )


def nuevo_modelo(producto: Producto) -> ProductoModelo:
    return ProductoModelo(
        codigo_barras=producto.codigo_barras,
        nombre=producto.nombre,
        precio_venta=producto.precio_venta,
        precio_compra=producto.precio_compra,
        stock=producto.stock,
        id_categoria=producto.id_categoria,
    )
