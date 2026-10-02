# ============================================================
# Caso de Uso: Eliminar Categoría
# ============================================================

from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_categoria import RepositorioCategoria


class EliminarCategoria:
    def __init__(self, repositorio: RepositorioCategoria):
        self.repositorio = repositorio

    def ejecutar(self, id_categoria: int) -> None:
        existente = self.repositorio.obtener_por_id(id_categoria)
        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró la categoría con id {id_categoria}."
            )
        
        eliminada = self.repositorio.eliminar(id_categoria)
        if not eliminada:
            raise EntidadNoEncontrada(...)
