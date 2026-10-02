# ============================================================
# Caso de Uso: Listar todos los Usuarios
# ============================================================

from dominio.entidades.usuario import Usuario
from dominio.repositorios.repositorio_usuario import RepositorioUsuario


class ListarUsuarios:
    def __init__(self, repositorio: RepositorioUsuario):
        self.repositorio = repositorio

    def ejecutar(self) -> list[Usuario]:
        return self.repositorio.obtener_todos()
