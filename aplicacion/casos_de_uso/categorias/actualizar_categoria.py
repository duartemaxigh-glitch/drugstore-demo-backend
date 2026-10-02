# ============================================================
# Caso de Uso: Actualizar Categoría
# ============================================================

from dominio.entidades.categoria import Categoria
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_categoria import RepositorioCategoria


class ActualizarCategoria:
    def __init__(self, repositorio: RepositorioCategoria):
        self.repositorio = repositorio

    def ejecutar(self, id_categoria: int, nombre: str) -> Categoria:
        # Primero verificamos que exista
        existente = self.repositorio.obtener_por_id(id_categoria)
        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró la categoría con id {id_categoria}."
            )

        # Creamos la entidad con los nuevos datos y validamos
        categoria = Categoria(nombre=nombre, id_categoria=id_categoria)
        categoria.validar()
        return self.repositorio.actualizar(categoria)
