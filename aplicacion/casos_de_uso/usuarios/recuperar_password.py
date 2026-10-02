# ============================================================
# Caso de Uso: Recuperar Contraseña
# ============================================================
# Permite al usuario cambiar su contraseña verificando
# que el DNI y email coincidan con el registro.
# Solo el dueño de la cuenta puede hacer esto.
# ============================================================

from __future__ import annotations

from aplicacion.puertos.password_hasher import PasswordHasher
from dominio.excepciones import ErrorDeValidacion
from dominio.repositorios.repositorio_usuario import RepositorioUsuario
from dominio.validaciones import validar_password


class RecuperarPassword:
    def __init__(
        self,
        repositorio: RepositorioUsuario,
        password_hasher: PasswordHasher,
    ):
        self.repositorio = repositorio
        self.password_hasher = password_hasher

    def ejecutar(
        self,
        dni: str,
        email: str,
        nueva_password: str,
        repetir_password: str,
    ) -> None:
        # Validar que las contraseñas coincidan
        if nueva_password != repetir_password:
            raise ErrorDeValidacion("Las contraseñas no coinciden.")

        # Validar política de contraseña
        validar_password(nueva_password)

        # Buscar usuario por email
        usuario = self.repositorio.obtener_por_email(email)
        if usuario is None:
            raise ErrorDeValidacion("El email o DNI no coinciden con ningún registro.")

        # Verificar que el DNI coincida
        if usuario.dni != dni:
            raise ErrorDeValidacion("El email o DNI no coinciden con ningún registro.")

        # Hashear la nueva contraseña
        password_hash = self.password_hasher.generar_hash(nueva_password)

        # Actualizar contraseña
        assert usuario.id_usuario is not None
        actualizado = self.repositorio.actualizar_password(
            usuario.id_usuario,
            password_hash,
        )
        if not actualizado:
            raise ErrorDeValidacion(
                "El email o DNI no coinciden con ningún registro."
            )
