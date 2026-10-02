from dominio.entidades.proveedor import Proveedor
from dominio.excepciones import EntidadDuplicada

from infraestructura.basedatos.sesion import SessionLocal
from infraestructura.basedatos.unidad_trabajo import UnidadDeTrabajoSQLAlchemy
from infraestructura.repositorios.repositorio_proveedor_sqlalchemy import (
    RepositorioProveedorSQLAlchemy,
)

with UnidadDeTrabajoSQLAlchemy(SessionLocal) as uow:
    repo = RepositorioProveedorSQLAlchemy(uow.session)

    eliminado = repo.eliminar(1)
    print("Eliminado:", eliminado)