# ============================================================
# Caso de Uso: Crear Usuario
# ============================================================
# Recibe la contraseña en texto plano y la hashea mediante el puerto
# PasswordHasher
# antes de guardarla. NUNCA se guarda la contraseña sin hash.
# ============================================================

from __future__ import annotations

from aplicacion.puertos.password_hasher import PasswordHasher
from dominio.entidades.usuario import Usuario
from dominio.repositorios.repositorio_usuario import RepositorioUsuario
from dominio.validaciones import validar_password


class CrearUsuario:
    def __init__(
        self,
        repositorio: RepositorioUsuario,
        password_hasher: PasswordHasher,
    ):
        self.repositorio = repositorio
        self.password_hasher = password_hasher

    def ejecutar(
        self,
        apellido: str,
        nombre: str,
        dni: str,
        email: str,
        password: str,
        rol: str = 'empleado',
        telefono: str | None = None,
    ) -> Usuario:
        validar_password(password)

        # Hasheamos la contraseña antes de crear la entidad
        password_hash = self.password_hasher.generar_hash(password)

        usuario = Usuario(
            apellido=apellido,
            nombre=nombre,
            dni=dni,
            email=email,
            password_hash=password_hash,
            rol=rol,
            telefono=telefono,
        )
        usuario.validar()
        return self.repositorio.crear(usuario)
