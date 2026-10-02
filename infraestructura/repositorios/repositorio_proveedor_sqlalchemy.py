from sqlalchemy import select
from sqlalchemy.orm import Session
from dominio.entidades.proveedor import Proveedor
from dominio.excepciones import EntidadDuplicada
from dominio.repositorios.repositorio_proveedor import RepositorioProveedor
from infraestructura.basedatos.mappers.proveedor_mapper import a_dominio, nuevo_modelo
from sqlalchemy.exc import IntegrityError
from psycopg.errors import UniqueViolation

from infraestructura.basedatos.modelos.proveedor_modelo import ProveedorModelo


class RepositorioProveedorSQLAlchemy(RepositorioProveedor):
    def __init__(self, session: Session):
        self.session = session
    
    def crear(self, proveedor: Proveedor) -> Proveedor:
        modelo = nuevo_modelo(proveedor)
        self.session.add(modelo)
        
        try:
            self.session.flush()
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                constraint = e.orig.diag.constraint_name
                if constraint == "proveedores_cuit_cuil_key":
                    raise EntidadDuplicada(
                        f"Ya existe un proveedor con CUIT/CUIL '{proveedor.cuit_cuil}'."
                    ) from e
            raise
        
        return a_dominio(modelo)
    
    def obtener_por_id(self, id_proveedor: int) -> Proveedor | None:
        stmt = select(ProveedorModelo).where(
            ProveedorModelo.id_proveedor == id_proveedor,
            ProveedorModelo.activo.is_(True)
        )
        
        modelo = self.session.scalar(stmt)
        
        if modelo is None:
            return None
        
        return a_dominio(modelo)
    
    def obtener_todos(self) -> list[Proveedor]:
        stmt = (
            select(ProveedorModelo)
            .where(ProveedorModelo.activo.is_(True))
            .order_by(ProveedorModelo.id_proveedor)
        )
        
        modelos = self.session.scalars(stmt).all()
        
        return [
            a_dominio(modelo)
            for modelo in modelos
        ]
        
    def actualizar(self, proveedor: Proveedor) -> Proveedor | None:
        modelo = self.session.get(ProveedorModelo, proveedor.id_proveedor)
        
        if modelo is None:
            return None
        
        modelo.razon_social=proveedor.razon_social
        modelo.cuit_cuil=proveedor.cuit_cuil
        modelo.contacto_nombre=proveedor.contacto_nombre
        modelo.telefono=proveedor.telefono
        modelo.email=proveedor.email
        
        try:
            self.session.flush()
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                constraint = e.orig.diag.constraint_name
                if constraint == "proveedores_cuit_cuil_key":
                    raise EntidadDuplicada(
                        f"Ya existe un proveedor con CUIT/CUIL '{proveedor.cuit_cuil}'."
                    ) from e
            raise
        
        return a_dominio(modelo)
    
    def eliminar(self, id_proveedor: int) -> bool:
        modelo = self.session.get(ProveedorModelo, id_proveedor)
        
        if modelo is None:
            return False
        
        modelo.activo = False
        self.session.flush()
        
        return True