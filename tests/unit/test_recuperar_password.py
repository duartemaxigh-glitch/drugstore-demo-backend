import pytest

from aplicacion.casos_de_uso.usuarios.recuperar_password import RecuperarPassword
from dominio.entidades.usuario import Usuario
from dominio.excepciones import ErrorDeValidacion


class RepositorioUsuarioFake:
    def __init__(
        self,
        usuario: Usuario | None = None,
        actualizacion_exitosa: bool = True,
    ):
        self.usuario = usuario
        self.actualizacion_exitosa = actualizacion_exitosa
        self.emails_buscados: list[str] = []
        self.passwords_actualizadas: list[tuple[int, str]] = []

    def obtener_por_email(self, email: str) -> Usuario | None:
        self.emails_buscados.append(email)
        if self.usuario is not None and self.usuario.email == email:
            return self.usuario
        return None

    def actualizar_password(self, id_usuario: int, password_hash: str) -> bool:
        self.passwords_actualizadas.append((id_usuario, password_hash))
        return self.actualizacion_exitosa


def test_recuperar_password_rechaza_passwords_distintas(password_hasher_fake):
    repo = RepositorioUsuarioFake()

    with pytest.raises(ErrorDeValidacion, match="no coinciden"):
        RecuperarPassword(repo, password_hasher_fake).ejecutar(
            dni="12345678",
            email="persona@example.com",
            nueva_password="secreto1",
            repetir_password="secreto2",
        )

    assert repo.emails_buscados == []
    assert repo.passwords_actualizadas == []
    assert password_hasher_fake.passwords_hasheadas == []


def test_recuperar_password_rechaza_password_corta(password_hasher_fake):
    repo = RepositorioUsuarioFake()

    with pytest.raises(ErrorDeValidacion, match="al menos 6 caracteres"):
        RecuperarPassword(repo, password_hasher_fake).ejecutar(
            dni="12345678",
            email="persona@example.com",
            nueva_password="12345",
            repetir_password="12345",
        )

    assert repo.emails_buscados == []
    assert repo.passwords_actualizadas == []
    assert password_hasher_fake.passwords_hasheadas == []


def test_recuperar_password_rechaza_email_inexistente(password_hasher_fake):
    repo = RepositorioUsuarioFake()

    with pytest.raises(ErrorDeValidacion, match="email o DNI"):
        RecuperarPassword(repo, password_hasher_fake).ejecutar(
            dni="12345678",
            email="inexistente@example.com",
            nueva_password="secreto",
            repetir_password="secreto",
        )

    assert repo.emails_buscados == ["inexistente@example.com"]
    assert repo.passwords_actualizadas == []
    assert password_hasher_fake.passwords_hasheadas == []


def test_recuperar_password_usa_hash_generado_y_lo_entrega_al_repositorio(
    password_hasher_fake,
):
    usuario = Usuario(
        id_usuario=7,
        apellido="Perez",
        nombre="Ana",
        dni="12345678",
        email="persona@example.com",
        password_hash="hash-anterior",
    )
    repo = RepositorioUsuarioFake(usuario)
    password_hasher_fake.hash_generado = "hash-nuevo-determinista"

    RecuperarPassword(repo, password_hasher_fake).ejecutar(
        dni="12345678",
        email="persona@example.com",
        nueva_password="123456",
        repetir_password="123456",
    )

    assert password_hasher_fake.passwords_hasheadas == ["123456"]
    assert repo.passwords_actualizadas == [(7, "hash-nuevo-determinista")]


def test_recuperar_password_rechaza_usuario_que_dejo_de_ser_elegible(
    password_hasher_fake,
):
    usuario = Usuario(
        id_usuario=7,
        apellido="Perez",
        nombre="Ana",
        dni="12345678",
        email="persona@example.com",
        password_hash="hash-anterior",
    )
    repo = RepositorioUsuarioFake(
        usuario,
        actualizacion_exitosa=False,
    )
    password_hasher_fake.hash_generado = "hash-nuevo-determinista"

    with pytest.raises(
        ErrorDeValidacion,
        match="email o DNI no coinciden",
    ):
        RecuperarPassword(repo, password_hasher_fake).ejecutar(
            dni="12345678",
            email="persona@example.com",
            nueva_password="secreto",
            repetir_password="secreto",
        )

    assert password_hasher_fake.passwords_hasheadas == ["secreto"]
    assert repo.passwords_actualizadas == [(7, "hash-nuevo-determinista")]
