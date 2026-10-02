import pytest

from aplicacion.casos_de_uso.usuarios.crear_usuario import CrearUsuario
from aplicacion.casos_de_uso.usuarios.login_usuario import LoginUsuario
from dominio.entidades.usuario import Usuario
from dominio.excepciones import ErrorDeValidacion


class RepositorioUsuarioFake:
    def __init__(self, usuario: Usuario | None = None):
        self.usuario = usuario
        self.usuarios_creados: list[Usuario] = []

    def crear(self, usuario: Usuario) -> Usuario:
        self.usuarios_creados.append(usuario)
        usuario.id_usuario = 1
        return usuario

    def obtener_por_email(self, email: str) -> Usuario | None:
        if self.usuario is not None and self.usuario.email == email:
            return self.usuario
        return None


def test_crear_usuario_usa_hash_producido_por_password_hasher(
    password_hasher_fake,
):
    repo = RepositorioUsuarioFake()
    password_hasher_fake.hash_generado = "hash-sin-bcrypt-real"

    usuario = CrearUsuario(repo, password_hasher_fake).ejecutar(
        apellido="Perez",
        nombre="Ana",
        dni="12345678",
        email="ana@example.com",
        password="123456",
    )

    assert password_hasher_fake.passwords_hasheadas == ["123456"]
    assert usuario.password_hash == "hash-sin-bcrypt-real"
    assert repo.usuarios_creados == [usuario]


def test_crear_usuario_rechaza_password_corto_antes_de_hashear_o_persistir(
    password_hasher_fake,
):
    repo = RepositorioUsuarioFake()

    with pytest.raises(
        ErrorDeValidacion,
        match="La contraseña debe tener al menos 6 caracteres",
    ):
        CrearUsuario(repo, password_hasher_fake).ejecutar(
            apellido="Perez",
            nombre="Ana",
            dni="12345678",
            email="ana@example.com",
            password="12345",
        )

    assert password_hasher_fake.passwords_hasheadas == []
    assert repo.usuarios_creados == []


def test_login_permite_acceso_cuando_password_hasher_verifica(
    password_hasher_fake,
):
    usuario = Usuario(
        id_usuario=1,
        apellido="Perez",
        nombre="Ana",
        dni="12345678",
        email="ana@example.com",
        password_hash="hash-guardado",
    )
    repo = RepositorioUsuarioFake(usuario)
    password_hasher_fake.resultado_verificacion = True

    resultado = LoginUsuario(repo, password_hasher_fake).ejecutar(
        "ana@example.com",
        "secreto",
    )

    assert resultado is usuario
    assert password_hasher_fake.verificaciones == [
        ("secreto", "hash-guardado")
    ]


def test_login_rechaza_password_cuando_password_hasher_no_verifica(
    password_hasher_fake,
):
    usuario = Usuario(
        id_usuario=1,
        apellido="Perez",
        nombre="Ana",
        dni="12345678",
        email="ana@example.com",
        password_hash="hash-guardado",
    )
    repo = RepositorioUsuarioFake(usuario)
    password_hasher_fake.resultado_verificacion = False

    with pytest.raises(
        ErrorDeValidacion,
        match="Email o contraseña incorrectos",
    ):
        LoginUsuario(repo, password_hasher_fake).ejecutar(
            "ana@example.com",
            "incorrecta",
        )

    assert password_hasher_fake.verificaciones == [
        ("incorrecta", "hash-guardado")
    ]
