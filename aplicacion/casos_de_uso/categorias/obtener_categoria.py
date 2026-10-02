# ============================================================
# Caso de Uso: Obtener Categoría por ID
# ============================================================

from dominio.entidades.categoria import Categoria
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_categoria import RepositorioCategoria


class ObtenerCategoria:
    def __init__(self, repositorio: RepositorioCategoria):
        self.repositorio = repositorio

    def ejecutar(self, id_categoria: int) -> Categoria:
        categoria = self.repositorio.obtener_por_id(id_categoria)
        if categoria is None:
            raise EntidadNoEncontrada(
                f"No se encontró la categoría con id {id_categoria}."
            )
        return categoria
