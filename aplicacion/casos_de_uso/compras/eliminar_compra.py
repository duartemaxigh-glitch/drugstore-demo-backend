# ============================================================
# Caso de Uso: Eliminar Compra
# ============================================================
# Al eliminar una compra, se REVERSA el stock de cada producto.
# Es decir, se resta la cantidad que se había sumado.
#
# Todo ocurre dentro de una transacción.
# ============================================================

from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_compra import RepositorioCompra
from dominio.repositorios.repositorio_producto import RepositorioProducto


class EliminarCompra:
    def __init__(
        self,
        repositorio_compra: RepositorioCompra,
        repositorio_producto: RepositorioProducto,
    ):
        self.repositorio_compra = repositorio_compra
        self.repositorio_producto = repositorio_producto

    def ejecutar(self, id_compra: int) -> None:
        compra = self.repositorio_compra.obtener_para_eliminar(id_compra)
        if compra is None:
            raise EntidadNoEncontrada(
                f"No se encontró la compra con id {id_compra}."
            )

        productos = self.repositorio_producto.obtener_para_modificar_stock(
            [detalle.id_producto for detalle in compra.detalles]
        )

        # Reversamos el stock de cada producto comprado
        for detalle in compra.detalles:
            producto = productos.get(detalle.id_producto)
            if producto is not None:
                producto.stock -= detalle.cantidad
                # Validar que el stock no quede negativo
                producto.stock = max(producto.stock, 0)

        self.repositorio_producto.actualizar_stocks(
            {
                id_producto: producto.stock
                for id_producto, producto in productos.items()
            }
        )

        eliminada = self.repositorio_compra.eliminar(id_compra)

        if not eliminada:
            raise EntidadNoEncontrada(
                f"No se encontró la compra con id {id_compra}."
            )
