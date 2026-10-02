# ============================================================
# Caso de Uso: Obtener Usuario por ID
# ============================================================

from dominio.entidades.usuario import Usuario
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_usuario import RepositorioUsuario


class ObtenerUsuario:
    def __init__(self, repositorio: RepositorioUsuario):
        self.repositorio = repositorio

    def ejecutar(self, id_usuario: int) -> Usuario:
        usuario = self.repositorio.obtener_por_id(id_usuario)
        if usuario is None:
            raise EntidadNoEncontrada(
                f"No se encontró el usuario con id {id_usuario}."
            )
        return usuario
