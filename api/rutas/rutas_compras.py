# ============================================================
# Rutas: Compras (Crear, Listar, Obtener, Eliminar)
# ============================================================
# El id_usuario se toma del token JWT.
# Al crear una compra, se suma stock a los productos.
# Al eliminar, se reversa el stock.
#
# La composición externa comparte una única Session/UoW entre los
# repositorios para garantizar atomicidad (stock + compra).
# ============================================================

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencias import (
    obtener_repo_compra,
    obtener_repo_producto,
    obtener_usuario_actual,
)
from api.esquemas import CompraCrear, CompraDetalleRespuesta, CompraRespuesta
from aplicacion.casos_de_uso.compras.crear_compra import CrearCompra
from aplicacion.casos_de_uso.compras.eliminar_compra import EliminarCompra
from aplicacion.casos_de_uso.compras.listar_compras import ListarCompras
from aplicacion.casos_de_uso.compras.obtener_compra import ObtenerCompra
from dominio.excepciones import EntidadNoEncontrada, ErrorDeValidacion
from dominio.repositorios.repositorio_compra import RepositorioCompra
from dominio.repositorios.repositorio_producto import RepositorioProducto

router = APIRouter(prefix="/compras", tags=["Compras"])


def _a_respuesta(c) -> CompraRespuesta:
    return CompraRespuesta(
        id_compra=c.id_compra,
        fecha=c.fecha,
        id_proveedor=c.id_proveedor,
        id_usuario=c.id_usuario,
        total=c.total,
        detalles=[
            CompraDetalleRespuesta(
                id_detalle=d.id_detalle,
                id_producto=d.id_producto,
                cantidad=d.cantidad,
                precio_unitario=d.precio_unitario,
                subtotal=d.subtotal,
            )
            for d in c.detalles
        ],
    )


DepRepoCompra = Annotated[RepositorioCompra, Depends(obtener_repo_compra)]
DepRepoProducto = Annotated[RepositorioProducto, Depends(obtener_repo_producto)]
DepUsuario = Annotated[dict, Depends(obtener_usuario_actual)]


@router.post("/", response_model=CompraRespuesta, status_code=status.HTTP_201_CREATED)
def crear(
    datos: CompraCrear,
    repo_compra: DepRepoCompra,
    repo_producto: DepRepoProducto,
    usuario: DepUsuario,
):
    try:
        caso_de_uso = CrearCompra(repo_compra, repo_producto)

        detalles = [
            {
                'id_producto': d.id_producto,
                'cantidad': d.cantidad,
                'precio_unitario': d.precio_unitario,
            }
            for d in datos.detalles
        ]

        compra = caso_de_uso.ejecutar(
            id_proveedor=datos.id_proveedor,
            id_usuario=usuario['id_usuario'],  # Del token JWT
            detalles=detalles,
        )
        return _a_respuesta(compra)
    except ErrorDeValidacion as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=list[CompraRespuesta])
def listar(repo: DepRepoCompra, usuario: DepUsuario):
    caso_de_uso = ListarCompras(repo)
    compras = caso_de_uso.ejecutar()
    return [_a_respuesta(c) for c in compras]


@router.get("/{id_compra}", response_model=CompraRespuesta)
def obtener(id_compra: int, repo: DepRepoCompra, usuario: DepUsuario):
    try:
        caso_de_uso = ObtenerCompra(repo)
        compra = caso_de_uso.ejecutar(id_compra)
        return _a_respuesta(compra)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id_compra}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    id_compra: int,
    repo_compra: DepRepoCompra,
    repo_producto: DepRepoProducto,
    usuario: DepUsuario,
):
    try:
        caso_de_uso = EliminarCompra(repo_compra, repo_producto)
        caso_de_uso.ejecutar(id_compra)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))
