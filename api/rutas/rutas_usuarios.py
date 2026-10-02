# ============================================================
# Rutas: Usuarios (CRUD completo)
# ============================================================
# TODO el CRUD de usuarios requiere rol 'jefe'.
# Los empleados no tienen acceso a esta sección.
# ============================================================

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencias import (
    obtener_password_hasher,
    obtener_repo_usuario,
    requiere_rol_jefe,
)
from api.esquemas import UsuarioActualizar, UsuarioCrear, UsuarioRespuesta
from aplicacion.casos_de_uso.usuarios.actualizar_usuario import ActualizarUsuario
from aplicacion.casos_de_uso.usuarios.crear_usuario import CrearUsuario
from aplicacion.casos_de_uso.usuarios.eliminar_usuario import EliminarUsuario
from aplicacion.casos_de_uso.usuarios.listar_usuarios import ListarUsuarios
from aplicacion.casos_de_uso.usuarios.obtener_usuario import ObtenerUsuario
from aplicacion.puertos.password_hasher import PasswordHasher
from dominio.excepciones import EntidadDuplicada, EntidadNoEncontrada, ErrorDeValidacion
from dominio.repositorios.repositorio_usuario import RepositorioUsuario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def _a_respuesta(u) -> UsuarioRespuesta:
    return UsuarioRespuesta(
        id_usuario=u.id_usuario,
        apellido=u.apellido,
        nombre=u.nombre,
        dni=u.dni,
        email=u.email,
        rol=u.rol,
        telefono=u.telefono,
        activo=u.activo,
    )


DepRepoUsuario = Annotated[RepositorioUsuario, Depends(obtener_repo_usuario)]
DepPasswordHasher = Annotated[PasswordHasher, Depends(obtener_password_hasher)]
DepJefe = Annotated[dict, Depends(requiere_rol_jefe)]


@router.post("/", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def crear(
    datos: UsuarioCrear,
    repo: DepRepoUsuario,
    password_hasher: DepPasswordHasher,
    usuario: DepJefe,
):
    try:
        caso_de_uso = CrearUsuario(repo, password_hasher)
        nuevo = caso_de_uso.ejecutar(
            apellido=datos.apellido,
            nombre=datos.nombre,
            dni=datos.dni,
            email=datos.email,
            password=datos.password,
            rol=datos.rol,
            telefono=datos.telefono,
        )
        return _a_respuesta(nuevo)
    except ErrorDeValidacion as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EntidadDuplicada as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/", response_model=list[UsuarioRespuesta])
def listar(repo: DepRepoUsuario, usuario: DepJefe):
    caso_de_uso = ListarUsuarios(repo)
    usuarios = caso_de_uso.ejecutar()
    return [_a_respuesta(u) for u in usuarios]


@router.get("/{id_usuario}", response_model=UsuarioRespuesta)
def obtener(id_usuario: int, repo: DepRepoUsuario, usuario: DepJefe):
    try:
        caso_de_uso = ObtenerUsuario(repo)
        u = caso_de_uso.ejecutar(id_usuario)
        return _a_respuesta(u)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{id_usuario}", response_model=UsuarioRespuesta)
def actualizar(id_usuario: int, datos: UsuarioActualizar, repo: DepRepoUsuario, usuario: DepJefe):
    try:
        caso_de_uso = ActualizarUsuario(repo)
        u = caso_de_uso.ejecutar(
            id_usuario=id_usuario,
            apellido=datos.apellido,
            nombre=datos.nombre,
            dni=datos.dni,
            email=datos.email,
            rol=datos.rol,
            telefono=datos.telefono,
        )
        return _a_respuesta(u)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ErrorDeValidacion as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EntidadDuplicada as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(id_usuario: int, repo: DepRepoUsuario, usuario: DepJefe):
    try:
        caso_de_uso = EliminarUsuario(repo)
        caso_de_uso.ejecutar(id_usuario)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))
