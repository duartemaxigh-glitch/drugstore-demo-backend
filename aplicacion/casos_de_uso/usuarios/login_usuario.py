# ============================================================
# Caso de Uso: Login (Iniciar Sesión)
# ============================================================
# Busca al usuario por email, verifica la contraseña con
# el puerto PasswordHasher y devuelve el usuario si es correcto.
# Este caso de uso NO genera el JWT (eso es infraestructura).
# Solo valida credenciales.
# ============================================================

from aplicacion.puertos.password_hasher import PasswordHasher
from dominio.entidades.usuario import Usuario
from dominio.excepciones import ErrorDeValidacion
from dominio.repositorios.repositorio_usuario import RepositorioUsuario


class LoginUsuario:
    def __init__(
        self,
        repositorio: RepositorioUsuario,
        password_hasher: PasswordHasher,
    ):
        self.repositorio = repositorio
        self.password_hasher = password_hasher

    def ejecutar(self, email: str, password: str) -> Usuario:
        usuario = self.repositorio.obtener_por_email(email)
        if usuario is None:
            raise ErrorDeValidacion("Email o contraseña incorrectos.")

        # Verificamos la contraseña mediante el puerto de aplicación
        password_correcta = self.password_hasher.verificar(
            password,
            usuario.password_hash,
        )
        if not password_correcta:
            raise ErrorDeValidacion("Email o contraseña incorrectos.")

        return usuario
