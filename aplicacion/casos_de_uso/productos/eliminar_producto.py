# ============================================================
# Caso de Uso: Eliminar Producto
# ============================================================
# Antes de eliminar, verifica que no tenga ventas ni compras
# asociadas. Si las tiene, rechaza la operación.
# ============================================================

from dominio.excepciones import EntidadNoEncontrada, ErrorDeValidacion
from dominio.repositorios.repositorio_compra import RepositorioCompra
from dominio.repositorios.repositorio_producto import RepositorioProducto
from dominio.repositorios.repositorio_venta import RepositorioVenta


class EliminarProducto:
    def __init__(
        self,
        repositorio: RepositorioProducto,
        repositorio_venta: RepositorioVenta,
        repositorio_compra: RepositorioCompra,
    ):
        self.repositorio = repositorio
        self.repositorio_venta = repositorio_venta
        self.repositorio_compra = repositorio_compra

    def ejecutar(self, id_producto: int) -> None:
        existente = self.repositorio.obtener_por_id(id_producto)
        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el producto con id {id_producto}."
            )

        # Verificar si tiene ventas asociadas
        ventas = self.repositorio_venta.obtener_todos()
        for venta in ventas:
            for detalle in venta.detalles:
                if detalle.id_producto == id_producto:
                    raise ErrorDeValidacion(
                        f"No se puede eliminar el producto porque tiene ventas asociadas "
                        f"(venta #{venta.id_venta})."
                    )

        # Verificar si tiene compras asociadas
        compras = self.repositorio_compra.obtener_todos()
        for compra in compras:
            for detalle in compra.detalles:
                if detalle.id_producto == id_producto:
                    raise ErrorDeValidacion(
                        f"No se puede eliminar el producto porque tiene compras asociadas "
                        f"(compra #{compra.id_compra})."
                    )

        eliminado = self.repositorio.eliminar(id_producto)

        if not eliminado:
            raise EntidadNoEncontrada(
                f"No se encontró el producto con id {id_producto}."
            )
