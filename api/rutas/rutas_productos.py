# ============================================================
# Rutas: Productos (CRUD completo)
# ============================================================

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencias import (
    obtener_repo_compra,
    obtener_repo_producto,
    obtener_repo_venta,
    obtener_usuario_actual,
)
from api.esquemas import ProductoActualizar, ProductoCrear, ProductoRespuesta
from aplicacion.casos_de_uso.productos.actualizar_producto import ActualizarProducto
from aplicacion.casos_de_uso.productos.crear_producto import CrearProducto
from aplicacion.casos_de_uso.productos.eliminar_producto import EliminarProducto
from aplicacion.casos_de_uso.productos.listar_productos import ListarProductos
from aplicacion.casos_de_uso.productos.obtener_producto import ObtenerProducto
from dominio.excepciones import EntidadDuplicada, EntidadNoEncontrada, ErrorDeValidacion
from dominio.repositorios.repositorio_compra import RepositorioCompra
from dominio.repositorios.repositorio_producto import RepositorioProducto
from dominio.repositorios.repositorio_venta import RepositorioVenta

router = APIRouter(prefix="/productos", tags=["Productos"])


def _a_respuesta(p) -> ProductoRespuesta:
    return ProductoRespuesta(
        id_producto=p.id_producto,
        nombre=p.nombre,
        precio_venta=p.precio_venta,
        precio_compra=p.precio_compra,
        stock=p.stock,
        codigo_barras=p.codigo_barras,
        id_categoria=p.id_categoria,
    )


DepRepoProducto = Annotated[RepositorioProducto, Depends(obtener_repo_producto)]
DepRepoVenta = Annotated[RepositorioVenta, Depends(obtener_repo_venta)]
DepRepoCompra = Annotated[RepositorioCompra, Depends(obtener_repo_compra)]
DepUsuario = Annotated[dict, Depends(obtener_usuario_actual)]


@router.post("/", response_model=ProductoRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: ProductoCrear, repo: DepRepoProducto, usuario: DepUsuario):
    try:
        caso_de_uso = CrearProducto(repo)
        producto = caso_de_uso.ejecutar(
            nombre=datos.nombre,
            precio_venta=datos.precio_venta,
            precio_compra=datos.precio_compra,
            stock=datos.stock,
            codigo_barras=datos.codigo_barras,
            id_categoria=datos.id_categoria,
        )
        return _a_respuesta(producto)
    except ErrorDeValidacion as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))
    except EntidadDuplicada as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/", response_model=list[ProductoRespuesta])
def listar(repo: DepRepoProducto, usuario: DepUsuario):
    caso_de_uso = ListarProductos(repo)
    productos = caso_de_uso.ejecutar()
    return [_a_respuesta(p) for p in productos]


@router.get("/{id_producto}", response_model=ProductoRespuesta)
def obtener(id_producto: int, repo: DepRepoProducto, usuario: DepUsuario):
    try:
        caso_de_uso = ObtenerProducto(repo)
        producto = caso_de_uso.ejecutar(id_producto)
        return _a_respuesta(producto)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{id_producto}", response_model=ProductoRespuesta)
def actualizar(id_producto: int, datos: ProductoActualizar, repo: DepRepoProducto, usuario: DepUsuario):
    try:
        caso_de_uso = ActualizarProducto(repo)
        producto = caso_de_uso.ejecutar(
            id_producto=id_producto,
            nombre=datos.nombre,
            precio_venta=datos.precio_venta,
            precio_compra=datos.precio_compra,
            codigo_barras=datos.codigo_barras,
            id_categoria=datos.id_categoria,
        )
        return _a_respuesta(producto)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ErrorDeValidacion as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EntidadDuplicada as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{id_producto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    id_producto: int,
    repo: DepRepoProducto,
    repo_venta: DepRepoVenta,
    repo_compra: DepRepoCompra,
    usuario: DepUsuario,
):
    try:
        caso_de_uso = EliminarProducto(repo, repo_venta, repo_compra)
        caso_de_uso.ejecutar(id_producto)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ErrorDeValidacion as e:
        raise HTTPException(status_code=400, detail=str(e))
