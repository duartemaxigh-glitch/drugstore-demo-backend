# ============================================================
# Caso de Uso: Obtener Producto por ID
# ============================================================

from dominio.entidades.producto import Producto
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_producto import RepositorioProducto


class ObtenerProducto:
    def __init__(self, repositorio: RepositorioProducto):
        self.repositorio = repositorio

    def ejecutar(self, id_producto: int) -> Producto:
        producto = self.repositorio.obtener_por_id(id_producto)
        if producto is None:
            raise EntidadNoEncontrada(
                f"No se encontró el producto con id {id_producto}."
            )
        return producto
