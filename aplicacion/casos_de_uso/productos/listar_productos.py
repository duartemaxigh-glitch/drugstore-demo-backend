# ============================================================
# Caso de Uso: Listar todos los Productos
# ============================================================

from dominio.entidades.producto import Producto
from dominio.repositorios.repositorio_producto import RepositorioProducto


class ListarProductos:
    def __init__(self, repositorio: RepositorioProducto):
        self.repositorio = repositorio

    def ejecutar(self) -> list[Producto]:
        return self.repositorio.obtener_todos()
