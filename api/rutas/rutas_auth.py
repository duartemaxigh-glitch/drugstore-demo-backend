# ============================================================
# Rutas: Autenticación (Login, Recuperar Password)
# ============================================================
# POST /auth/login            → Recibe email y password, devuelve JWT.
# POST /auth/recuperar-password → Verifica DNI + email, cambia contraseña.
# Estos son los ÚNICOS endpoints que no requieren token.
# ============================================================

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencias import obtener_password_hasher, obtener_repo_usuario
from api.esquemas import LoginEsquema, RecuperarPasswordEsquema, TokenEsquema
from aplicacion.casos_de_uso.usuarios.login_usuario import LoginUsuario
from aplicacion.casos_de_uso.usuarios.recuperar_password import RecuperarPassword
from aplicacion.puertos.password_hasher import PasswordHasher
from dominio.excepciones import ErrorDeValidacion
from dominio.repositorios.repositorio_usuario import RepositorioUsuario
from infraestructura.seguridad.jwt_servicio import crear_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

DepRepoUsuario = Annotated[RepositorioUsuario, Depends(obtener_repo_usuario)]
DepPasswordHasher = Annotated[PasswordHasher, Depends(obtener_password_hasher)]


@router.post("/login", response_model=TokenEsquema)
def login(
    datos: LoginEsquema,
    repo: DepRepoUsuario,
    password_hasher: DepPasswordHasher,
):
    try:
        caso_de_uso = LoginUsuario(repo, password_hasher)
        usuario = caso_de_uso.ejecutar(datos.email, datos.password)

        assert usuario.id_usuario is not None
        token = crear_token(usuario.id_usuario, usuario.email, usuario.rol)

        return TokenEsquema(token=token, rol=usuario.rol)

    except ErrorDeValidacion as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/recuperar-password", status_code=status.HTTP_200_OK)
def recuperar_password(
    datos: RecuperarPasswordEsquema,
    repo: DepRepoUsuario,
    password_hasher: DepPasswordHasher,
):
    try:
        caso_de_uso = RecuperarPassword(repo, password_hasher)
        caso_de_uso.ejecutar(
            dni=datos.dni,
            email=datos.email,
            nueva_password=datos.nueva_password,
            repetir_password=datos.repetir_password,
        )
        return {"mensaje": "Contraseña actualizada correctamente."}

    except ErrorDeValidacion as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
