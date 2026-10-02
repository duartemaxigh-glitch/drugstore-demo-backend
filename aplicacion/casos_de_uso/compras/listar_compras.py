# ============================================================
# Caso de Uso: Listar todas las Compras
# ============================================================

from dominio.entidades.compra import Compra
from dominio.repositorios.repositorio_compra import RepositorioCompra


class ListarCompras:
    def __init__(self, repositorio: RepositorioCompra):
        self.repositorio = repositorio

    def ejecutar(self) -> list[Compra]:
        return self.repositorio.obtener_todos()
