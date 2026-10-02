from psycopg.errors import ForeignKeyViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from dominio.entidades.venta import Venta
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_venta import RepositorioVenta
from infraestructura.basedatos.mappers.venta_mapper import (
    a_dominio,
    a_dominio_con_detalles,
    nuevo_modelo,
)
from infraestructura.basedatos.modelos.venta_modelo import (
    VentaDetalleModelo,
    VentaModelo,
)


CONSTRAINTS_REFERENCIAS_VENTA = {
    "ventas_id_usuario_fkey": "usuario",
    "ventas_id_cliente_fkey": "cliente",
    "ventas_id_medio_pago_fkey": "medio de pago",
    "venta_detalle_id_producto_fkey": "producto",
    "venta_detalle_id_venta_fkey": "venta",
}


class RepositorioVentaSQLAlchemy(RepositorioVenta):
    def __init__(self, session: Session):
        self.session = session

    def crear(self, venta: Venta) -> Venta:
        modelo = nuevo_modelo(venta)
        self.session.add(modelo)

        try:
            self.session.flush()
        except IntegrityError as error:
            self._traducir_referencia_inexistente(error)
            raise

        venta.id_venta = modelo.id_venta
        for detalle, detalle_modelo in zip(venta.detalles, modelo.detalles):
            detalle.id_detalle = detalle_modelo.id_detalle
            detalle.id_venta = modelo.id_venta

        return venta

    def obtener_por_id(self, id_venta: int) -> Venta | None:
        stmt = (
            select(VentaModelo)
            .options(selectinload(VentaModelo.detalles))
            .where(VentaModelo.id_venta == id_venta)
        )
        modelo = self.session.scalar(stmt)

        if modelo is None:
            return None

        return a_dominio(modelo)

    def obtener_para_eliminar(self, id_venta: int) -> Venta | None:
        stmt_cabecera = (
            select(VentaModelo)
            .where(VentaModelo.id_venta == id_venta)
            .with_for_update(of=VentaModelo)
            .execution_options(populate_existing=True)
        )
        modelo = self.session.scalar(stmt_cabecera)

        if modelo is None:
            return None

        stmt_detalles = (
            select(VentaDetalleModelo)
            .where(VentaDetalleModelo.id_venta == id_venta)
            .order_by(VentaDetalleModelo.id_detalle)
            .execution_options(populate_existing=True)
        )
        detalles = self.session.scalars(stmt_detalles).all()

        return a_dominio_con_detalles(modelo, detalles)

    def obtener_todos(self) -> list[Venta]:
        stmt = (
            select(VentaModelo)
            .options(selectinload(VentaModelo.detalles))
            .order_by(VentaModelo.id_venta.desc())
        )
        modelos = self.session.scalars(stmt).all()

        return [a_dominio(modelo) for modelo in modelos]

    def eliminar(self, id_venta: int) -> bool:
        modelo = self.session.get(VentaModelo, id_venta)

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
        entidad = CONSTRAINTS_REFERENCIAS_VENTA.get(constraint)

        if entidad is not None:
            raise EntidadNoEncontrada(
                f"No se encontró el {entidad} referenciado por la venta."
            ) from error
