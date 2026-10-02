from psycopg.errors import ForeignKeyViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from dominio.entidades.compra import Compra
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_compra import RepositorioCompra
from infraestructura.basedatos.mappers.compra_mapper import (
    a_dominio,
    a_dominio_con_detalles,
    nuevo_modelo,
)
from infraestructura.basedatos.modelos.compra_modelo import (
    CompraDetalleModelo,
    CompraModelo,
)


CONSTRAINTS_REFERENCIAS_COMPRA = {
    "compras_id_proveedor_fkey": "proveedor",
    "compras_id_usuario_fkey": "usuario",
    "compra_detalle_id_producto_fkey": "producto",
    "compra_detalle_id_compra_fkey": "compra",
}


class RepositorioCompraSQLAlchemy(RepositorioCompra):
    def __init__(self, session: Session):
        self.session = session

    def crear(self, compra: Compra) -> Compra:
        modelo = nuevo_modelo(compra)
        self.session.add(modelo)

        try:
            self.session.flush()
        except IntegrityError as error:
            self._traducir_referencia_inexistente(error)
            raise

        compra.id_compra = modelo.id_compra
        for detalle, detalle_modelo in zip(compra.detalles, modelo.detalles):
            detalle.id_detalle = detalle_modelo.id_detalle
            detalle.id_compra = modelo.id_compra

        return compra

    def obtener_por_id(self, id_compra: int) -> Compra | None:
        stmt = (
            select(CompraModelo)
            .options(selectinload(CompraModelo.detalles))
            .where(CompraModelo.id_compra == id_compra)
        )
        modelo = self.session.scalar(stmt)

        if modelo is None:
            return None

        return a_dominio(modelo)

    def obtener_para_eliminar(self, id_compra: int) -> Compra | None:
        stmt_cabecera = (
            select(CompraModelo)
            .where(CompraModelo.id_compra == id_compra)
            .with_for_update(of=CompraModelo)
            .execution_options(populate_existing=True)
        )
        modelo = self.session.scalar(stmt_cabecera)

        if modelo is None:
            return None

        stmt_detalles = (
            select(CompraDetalleModelo)
            .where(CompraDetalleModelo.id_compra == id_compra)
            .order_by(CompraDetalleModelo.id_detalle)
            .execution_options(populate_existing=True)
        )
        detalles = self.session.scalars(stmt_detalles).all()

        return a_dominio_con_detalles(modelo, detalles)

    def obtener_todos(self) -> list[Compra]:
        stmt = (
            select(CompraModelo)
            .options(selectinload(CompraModelo.detalles))
            .order_by(CompraModelo.id_compra.desc())
        )
        modelos = self.session.scalars(stmt).all()

        return [a_dominio(modelo) for modelo in modelos]

    def eliminar(self, id_compra: int) -> bool:
        modelo = self.session.get(CompraModelo, id_compra)

        if modelo is None:
            return False

        self.session.delete(modelo)
        self.session.flush()
        return True

    @staticmethod
    def _traducir_referencia_inexistente(error: IntegrityError) -> None:
        if not isinstance(error.orig, ForeignKeyViolation):
            return

        constraint = error.orig.diag.constraint_name
        entidad = CONSTRAINTS_REFERENCIAS_COMPRA.get(constraint)

        if entidad is not None:
            raise EntidadNoEncontrada(
                f"No se encontró el {entidad} referenciado por la compra."
            ) from error
