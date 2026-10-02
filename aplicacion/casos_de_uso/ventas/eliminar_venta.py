# ============================================================
# Caso de Uso: Eliminar Venta
# ============================================================
# Al eliminar una venta, se REVERSA el stock de cada producto.
# Es decir, se suma la cantidad que se había descontado.
#
# Todo ocurre dentro de una transacción.
# ============================================================

from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_producto import RepositorioProducto
from dominio.repositorios.repositorio_venta import RepositorioVenta


class EliminarVenta:
    def __init__(
        self,
        repositorio_venta: RepositorioVenta,
        repositorio_producto: RepositorioProducto,
    ):
        self.repositorio_venta = repositorio_venta
        self.repositorio_producto = repositorio_producto

    def ejecutar(self, id_venta: int) -> None:
        venta = self.repositorio_venta.obtener_para_eliminar(id_venta)
        if venta is None:
            raise EntidadNoEncontrada(
                f"No se encontró la venta con id {id_venta}."
            )

        productos = self.repositorio_producto.obtener_para_modificar_stock(
            [detalle.id_producto for detalle in venta.detalles]
        )

        # Reversamos el stock de cada producto vendido
        for detalle in venta.detalles:
            producto = productos.get(detalle.id_producto)
            if producto is not None:
                producto.stock += detalle.cantidad

        self.repositorio_producto.actualizar_stocks(
            {
                id_producto: producto.stock
                for id_producto, producto in productos.items()
            }
        )

        eliminada = self.repositorio_venta.eliminar(id_venta)

        if not eliminada:
            raise EntidadNoEncontrada(
                f"No se encontró la venta con id {id_venta}."
            )
