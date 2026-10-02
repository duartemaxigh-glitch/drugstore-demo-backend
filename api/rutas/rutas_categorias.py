# ============================================================
# Rutas: Categorías (CRUD completo)
# ============================================================
# Todos los endpoints requieren autenticación (JWT).
# ============================================================

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencias import obtener_repo_categoria, obtener_usuario_actual
from api.esquemas import CategoriaCrear, CategoriaRespuesta
from aplicacion.casos_de_uso.categorias.actualizar_categoria import ActualizarCategoria
from aplicacion.casos_de_uso.categorias.crear_categoria import CrearCategoria
from aplicacion.casos_de_uso.categorias.eliminar_categoria import EliminarCategoria
from aplicacion.casos_de_uso.categorias.listar_categorias import ListarCategorias
from aplicacion.casos_de_uso.categorias.obtener_categoria import ObtenerCategoria
from dominio.excepciones import EntidadDuplicada, EntidadNoEncontrada, ErrorDeValidacion
from dominio.repositorios.repositorio_categoria import RepositorioCategoria

router = APIRouter(prefix="/categorias", tags=["Categorías"])


DepRepoCategoria = Annotated[RepositorioCategoria, Depends(obtener_repo_categoria)]
DepUsuario = Annotated[dict, Depends(obtener_usuario_actual)]


@router.post("/", response_model=CategoriaRespuesta, status_code=status.HTTP_201_CREATED)
def crear(datos: CategoriaCrear, repo: DepRepoCategoria, usuario: DepUsuario):
    try:
        caso_de_uso = CrearCategoria(repo)
        categoria = caso_de_uso.ejecutar(datos.nombre)
        return CategoriaRespuesta(id_categoria=categoria.id_categoria, nombre=categoria.nombre)
    except ErrorDeValidacion as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EntidadDuplicada as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/", response_model=list[CategoriaRespuesta])
def listar(repo: DepRepoCategoria, usuario: DepUsuario):
    caso_de_uso = ListarCategorias(repo)
    categorias = caso_de_uso.ejecutar()
    return [
        CategoriaRespuesta(id_categoria=c.id_categoria, nombre=c.nombre)
        for c in categorias
    ]


@router.get("/{id_categoria}", response_model=CategoriaRespuesta)
def obtener(id_categoria: int, repo: DepRepoCategoria, usuario: DepUsuario):
    try:
        caso_de_uso = ObtenerCategoria(repo)
        categoria = caso_de_uso.ejecutar(id_categoria)
        return CategoriaRespuesta(id_categoria=categoria.id_categoria, nombre=categoria.nombre)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{id_categoria}", response_model=CategoriaRespuesta)
def actualizar(id_categoria: int, datos: CategoriaCrear, repo: DepRepoCategoria, usuario: DepUsuario):
    try:
        caso_de_uso = ActualizarCategoria(repo)
        categoria = caso_de_uso.ejecutar(id_categoria, datos.nombre)
        return CategoriaRespuesta(id_categoria=categoria.id_categoria, nombre=categoria.nombre)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ErrorDeValidacion as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EntidadDuplicada as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(id_categoria: int, repo: DepRepoCategoria, usuario: DepUsuario):
    try:
        caso_de_uso = EliminarCategoria(repo)
        caso_de_uso.ejecutar(id_categoria)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))
