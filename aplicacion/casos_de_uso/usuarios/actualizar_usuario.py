# ============================================================
# Caso de Uso: Actualizar Usuario
# ============================================================
# Al actualizar NO se cambia la contraseña aquí.
# Si se necesitara cambiar contraseña, sería otro caso de uso.
# ============================================================

from __future__ import annotations

from dominio.entidades.usuario import Usuario
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_usuario import RepositorioUsuario


class ActualizarUsuario:
    def __init__(self, repositorio: RepositorioUsuario):
        self.repositorio = repositorio

    def ejecutar(
        self,
        id_usuario: int,
        apellido: str,
        nombre: str,
        dni: str,
        email: str,
        rol: str = 'empleado',
        telefono: str | None = None,
    ) -> Usuario:
        existente = self.repositorio.obtener_por_id(id_usuario)
        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el usuario con id {id_usuario}."
            )

        # Mantenemos el password_hash que ya tenía
        usuario = Usuario(
            id_usuario=id_usuario,
            apellido=apellido,
            nombre=nombre,
            dni=dni,
            email=email,
            password_hash=existente.password_hash,
            rol=rol,
            telefono=telefono,
        )
        usuario.validar()
        return self.repositorio.actualizar(usuario)
