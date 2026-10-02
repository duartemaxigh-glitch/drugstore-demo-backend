# ============================================================
# Caso de Uso: Listar todas las Categorías
# ============================================================

from dominio.entidades.categoria import Categoria
from dominio.repositorios.repositorio_categoria import RepositorioCategoria


class ListarCategorias:
    def __init__(self, repositorio: RepositorioCategoria):
        self.repositorio = repositorio

    def ejecutar(self) -> list[Categoria]:
        return self.repositorio.obtener_todos()
