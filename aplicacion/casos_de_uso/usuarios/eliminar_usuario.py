# ============================================================
# Caso de Uso: Eliminar Usuario
# ============================================================

from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_usuario import RepositorioUsuario


class EliminarUsuario:
    def __init__(self, repositorio: RepositorioUsuario):
        self.repositorio = repositorio

    def ejecutar(self, id_usuario: int) -> None:
        existente = self.repositorio.obtener_por_id(id_usuario)
        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el usuario con id {id_usuario}."
            )
        eliminado = self.repositorio.eliminar(id_usuario)
        if not eliminado:
            raise EntidadNoEncontrada(
                f"No se encontró el usuario con id {id_usuario}."
            )
