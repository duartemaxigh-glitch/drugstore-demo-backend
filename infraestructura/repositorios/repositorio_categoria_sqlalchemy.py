from sqlalchemy.orm import Session
from sqlalchemy import select
from dominio.entidades.categoria import Categoria
from infraestructura.basedatos.modelos.categoria_modelo import CategoriaModelo
from dominio.repositorios.repositorio_categoria import RepositorioCategoria
from infraestructura.basedatos.mappers.categoria_mapper import (
    a_dominio,
    nuevo_modelo,
)
from sqlalchemy.exc import IntegrityError
from psycopg.errors import UniqueViolation
from dominio.excepciones import EntidadDuplicada

class RepositorioCategoriaSQLAlchemy(RepositorioCategoria):
    def __init__(self, session: Session):
        self.session = session
    
    def crear(self, categoria: Categoria) -> Categoria:
        modelo = nuevo_modelo(categoria)
        
        self.session.add(modelo)
        
        try:
            self.session.flush()
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                constraint = e.orig.diag.constraint_name
                if constraint == "categorias_nombre_key":
                    raise EntidadDuplicada(
                        f"Ya existe una categoría con nombre '{categoria.nombre}'."
                    ) from e
            raise
        
        return a_dominio(modelo)
    
    def obtener_por_id(self, id_categoria: int) -> Categoria | None:
        modelo = self.session.get(CategoriaModelo, id_categoria)
        
        if modelo is None:
            return None
        
        return a_dominio(modelo)
    
    def obtener_todos(self) -> list[Categoria]:
        stmt = select(CategoriaModelo).order_by(CategoriaModelo.id_categoria)
        modelos = self.session.scalars(stmt).all()
        
        return [
            a_dominio(modelo)
            for modelo in modelos
        ]
    
    def actualizar(self, categoria: Categoria) -> Categoria | None:
        modelo = self.session.get(CategoriaModelo, categoria.id_categoria)
        
        if modelo is None:
            return None
        
        modelo.nombre = categoria.nombre
        
        try:
            self.session.flush()
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                raise EntidadDuplicada(
                    f"Ya existe una categoría con nombre '{categoria.nombre}'."
                ) from e
            raise
        
        return a_dominio(modelo)
    
    def eliminar(self, id_categoria: int) -> bool:
        modelo = self.session.get(CategoriaModelo, id_categoria)
        
        if modelo is None:
            return False
        
        self.session.delete(modelo)
        self.session.flush()
        
        return True