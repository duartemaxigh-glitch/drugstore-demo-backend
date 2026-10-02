from sqlalchemy.orm import Session
from sqlalchemy import select
from dominio.entidades.medio_pago import MedioPago
from infraestructura.basedatos.modelos.medio_pago_modelo import MedioPagoModelo
from dominio.repositorios.repositorio_medio_pago import RepositorioMedioPago
from infraestructura.basedatos.mappers.medio_pago_mapper import (
    a_dominio,
    nuevo_modelo,
)
from sqlalchemy.exc import IntegrityError
from psycopg.errors import UniqueViolation
from dominio.excepciones import EntidadDuplicada


class RepositorioMedioPagoSQLAlchemy(RepositorioMedioPago):
    def __init__(self, session: Session):
        self.session = session
    
    def crear(self, medio_pago: MedioPago) -> MedioPago:
        modelo = nuevo_modelo(medio_pago)
        
        self.session.add(modelo)
        
        try:
            self.session.flush()
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                constraint = e.orig.diag.constraint_name
                if constraint == "medios_pago_nombre_key":
                    raise EntidadDuplicada(
                        f"Ya existe un medio de pago con nombre '{medio_pago.nombre}'."
                    ) from e
            raise
        
        return a_dominio(modelo)
    
    def obtener_por_id(self, id_medio_pago: int) -> MedioPago | None:
        modelo = self.session.get(MedioPagoModelo, id_medio_pago)
        
        if modelo is None:
            return None
        
        return a_dominio(modelo)
    
    def obtener_todos(self) -> list[MedioPago]:
        stmt = select(MedioPagoModelo).order_by(MedioPagoModelo.id_medio_pago)
        modelos = self.session.scalars(stmt).all()
        
        return [
            a_dominio(modelo)
            for modelo in modelos
        ]
    
    def actualizar(self, medio_pago: MedioPago) -> MedioPago | None:
        modelo = self.session.get(MedioPagoModelo, medio_pago.id_medio_pago)
    
        if modelo is None:
            return None
        
        modelo.nombre = medio_pago.nombre
        
        try:
            self.session.flush()
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                constraint = e.orig.diag.constraint_name
                if constraint == "medios_pago_nombre_key":
                    raise EntidadDuplicada(
                        f"Ya existe un medio de pago con nombre '{medio_pago.nombre}'."
                    ) from e
            raise
        return a_dominio(modelo)
    
    def eliminar(self, id_medio_pago: int) -> bool:
        modelo = self.session.get(MedioPagoModelo, id_medio_pago)
        
        if modelo is None:
            return False
        
        self.session.delete(modelo)
        self.session.flush()
        
        return True