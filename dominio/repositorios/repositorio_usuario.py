# ============================================================
# Interfaz: RepositorioUsuario
# ============================================================
# Contrato para operaciones CRUD de usuarios.
# Incluye 'obtener_por_email' que es necesario para el login.
# ============================================================

from abc import ABC, abstractmethod

from dominio.entidades.usuario import Usuario


class RepositorioUsuario(ABC):

    @abstractmethod
    def crear(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def obtener_por_id(self, id_usuario: int) -> Usuario | None:
        pass

    @abstractmethod
    def obtener_por_email(self, email: str) -> Usuario | None:
        pass

    @abstractmethod
    def obtener_todos(self) -> list[Usuario]:
        pass

    @abstractmethod
    def actualizar(self, usuario: Usuario) -> Usuario | None:
        pass

    @abstractmethod
    def actualizar_password(
        self,
        id_usuario: int,
        password_hash: str,
    ) -> bool:
        pass

    @abstractmethod
    def eliminar(
        self,
        id_usuario: int,
    ) -> bool:
        pass
