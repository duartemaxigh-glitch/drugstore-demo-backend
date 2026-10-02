# ============================================================
# Rutas: Proveedores (CRUD completo)
# ============================================================

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencias import (
    obtener_repo_proveedor,
    obtener_usuario_actual,
)
from api.esquemas import (
    ProveedorActualizarParcial,
    ProveedorCrear,
    ProveedorReemplazar,
    ProveedorRespuesta,
)

from aplicacion.casos_de_uso.proveedores.actualizar_proveedor import (
    ActualizarProveedor,
)
from aplicacion.casos_de_uso.proveedores.actualizar_proveedor_parcial import (
    ActualizarProveedorParcial,
)
from aplicacion.casos_de_uso.proveedores.crear_proveedor import (
    CrearProveedor,
)
from aplicacion.casos_de_uso.proveedores.eliminar_proveedor import (
    EliminarProveedor,
)
from aplicacion.casos_de_uso.proveedores.listar_proveedores import (
    ListarProveedores,
)
from aplicacion.casos_de_uso.proveedores.obtener_proveedor import (
    ObtenerProveedor,
)

from dominio.excepciones import (
    EntidadDuplicada,
    EntidadNoEncontrada,
    ErrorDeValidacion,
)
from dominio.repositorios.repositorio_proveedor import (
    RepositorioProveedor,
)


router = APIRouter(
    prefix="/proveedores",
    tags=["Proveedores"],
)


def _a_respuesta(p) -> ProveedorRespuesta:
    return ProveedorRespuesta(
        id_proveedor=p.id_proveedor,
        razon_social=p.razon_social,
        cuit_cuil=p.cuit_cuil,
        contacto_nombre=p.contacto_nombre,
        telefono=p.telefono,
        email=p.email,
        activo=p.activo,
    )


DepRepoProveedor = Annotated[
    RepositorioProveedor,
    Depends(obtener_repo_proveedor),
]

DepUsuario = Annotated[
    dict,
    Depends(obtener_usuario_actual),
]


@router.post(
    "/",
    response_model=ProveedorRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    datos: ProveedorCrear,
    repo: DepRepoProveedor,
    usuario: DepUsuario,
):
    try:
        caso_de_uso = CrearProveedor(repo)

        proveedor = caso_de_uso.ejecutar(
            razon_social=datos.razon_social,
            cuit_cuil=datos.cuit_cuil,
            contacto_nombre=datos.contacto_nombre,
            telefono=datos.telefono,
            email=datos.email,
        )

        return _a_respuesta(proveedor)

    except ErrorDeValidacion as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except EntidadDuplicada as e:
        raise HTTPException(
            status_code=409,
            detail=str(e),
        )


@router.get(
    "/",
    response_model=list[ProveedorRespuesta],
)
def listar(
    repo: DepRepoProveedor,
    usuario: DepUsuario,
):
    caso_de_uso = ListarProveedores(repo)
    proveedores = caso_de_uso.ejecutar()

    return [
        _a_respuesta(p)
        for p in proveedores
    ]


@router.get(
    "/{id_proveedor}",
    response_model=ProveedorRespuesta,
)
def obtener(
    id_proveedor: int,
    repo: DepRepoProveedor,
    usuario: DepUsuario,
):
    try:
        caso_de_uso = ObtenerProveedor(repo)
        proveedor = caso_de_uso.ejecutar(id_proveedor)

        return _a_respuesta(proveedor)

    except EntidadNoEncontrada as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.put(
    "/{id_proveedor}",
    response_model=ProveedorRespuesta,
)
def actualizar(
    id_proveedor: int,
    datos: ProveedorReemplazar,
    repo: DepRepoProveedor,
    usuario: DepUsuario,
):
    try:
        caso_de_uso = ActualizarProveedor(repo)

        proveedor = caso_de_uso.ejecutar(
            id_proveedor=id_proveedor,
            razon_social=datos.razon_social,
            cuit_cuil=datos.cuit_cuil,
            contacto_nombre=datos.contacto_nombre,
            telefono=datos.telefono,
            email=datos.email,
        )

        return _a_respuesta(proveedor)

    except EntidadNoEncontrada as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ErrorDeValidacion as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except EntidadDuplicada as e:
        raise HTTPException(
            status_code=409,
            detail=str(e),
        )


@router.patch(
    "/{id_proveedor}",
    response_model=ProveedorRespuesta,
)
def actualizar_parcial(
    id_proveedor: int,
    datos: ProveedorActualizarParcial,
    repo: DepRepoProveedor,
    usuario: DepUsuario,
):
    try:
        cambios = datos.model_dump(
            exclude_unset=True,
        )

        caso_de_uso = ActualizarProveedorParcial(repo)

        proveedor = caso_de_uso.ejecutar(
            id_proveedor=id_proveedor,
            cambios=cambios,
        )

        return _a_respuesta(proveedor)

    except EntidadNoEncontrada as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ErrorDeValidacion as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except EntidadDuplicada as e:
        raise HTTPException(
            status_code=409,
            detail=str(e),
        )


@router.delete(
    "/{id_proveedor}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar(
    id_proveedor: int,
    repo: DepRepoProveedor,
    usuario: DepUsuario,
):
    try:
        caso_de_uso = EliminarProveedor(repo)
        caso_de_uso.ejecutar(id_proveedor)

    except EntidadNoEncontrada as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )