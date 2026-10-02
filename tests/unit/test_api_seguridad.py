from api.dependencias import (
    obtener_password_hasher,
    obtener_repo_categoria,
    obtener_repo_usuario,
    requiere_rol_jefe,
)
from main import app


class RepositorioUsuarioSinCoincidencias:
    def __init__(self):
        self.emails_buscados: list[str] = []
        self.usuarios_creados = []

    def obtener_por_email(self, email: str):
        self.emails_buscados.append(email)
        return None

    def crear(self, usuario):
        self.usuarios_creados.append(usuario)
        return usuario


class RepositorioCategoriaFake:
    def obtener_todos(self):
        return []


def test_login_invalido_devuelve_401(api_client):
    app.dependency_overrides[obtener_repo_usuario] = (
        lambda: RepositorioUsuarioSinCoincidencias()
    )

    respuesta = api_client.post(
        "/api/auth/login",
        json={"email": "nadie@example.com", "password": "incorrecta"},
    )

    assert respuesta.status_code == 401
    assert respuesta.json() == {"detail": "Email o contraseña incorrectos."}


def test_endpoint_protegido_sin_token_rechaza_peticion(api_client):
    app.dependency_overrides[obtener_repo_categoria] = (
        lambda: RepositorioCategoriaFake()
    )

    respuesta = api_client.get("/api/categorias/")

    assert respuesta.status_code == 403


def test_crear_usuario_con_password_corto_devuelve_400_y_no_422(
    api_client,
    password_hasher_fake,
):
    repo = RepositorioUsuarioSinCoincidencias()
    app.dependency_overrides[obtener_repo_usuario] = lambda: repo
    app.dependency_overrides[obtener_password_hasher] = (
        lambda: password_hasher_fake
    )
    app.dependency_overrides[requiere_rol_jefe] = lambda: {
        "id_usuario": 1,
        "rol": "jefe",
    }

    respuesta = api_client.post(
        "/api/usuarios/",
        json={
            "apellido": "Perez",
            "nombre": "Ana",
            "dni": "12345678",
            "email": "ana@example.com",
            "password": "12345",
            "rol": "empleado",
        },
    )

    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "detail": "La contraseña debe tener al menos 6 caracteres."
    }
    assert password_hasher_fake.passwords_hasheadas == []
    assert repo.usuarios_creados == []


def test_recuperar_password_corto_conserva_400_y_no_422(
    api_client,
    password_hasher_fake,
):
    repo = RepositorioUsuarioSinCoincidencias()
    app.dependency_overrides[obtener_repo_usuario] = lambda: repo
    app.dependency_overrides[obtener_password_hasher] = (
        lambda: password_hasher_fake
    )

    respuesta = api_client.post(
        "/api/auth/recuperar-password",
        json={
            "dni": "12345678",
            "email": "ana@example.com",
            "nueva_password": "12345",
            "repetir_password": "12345",
        },
    )

    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "detail": "La contraseña debe tener al menos 6 caracteres."
    }
    assert repo.emails_buscados == []
    assert password_hasher_fake.passwords_hasheadas == []
