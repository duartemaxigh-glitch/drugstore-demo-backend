from collections.abc import Mapping, Sequence

from psycopg.errors import ForeignKeyViolation, UniqueViolation
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dominio.entidades.producto import Producto
from dominio.excepciones import (
    EntidadDuplicada,
    EntidadNoEncontrada,
    ErrorDeValidacion,
)
from dominio.repositorios.repositorio_producto import RepositorioProducto
from infraestructura.basedatos.mappers.producto_mapper import (
    a_dominio,
    nuevo_modelo,
)
from infraestructura.basedatos.modelos.producto_modelo import ProductoModelo


CONSTRAINT_CODIGO_BARRAS_UNICO = "productos_codigo_barras_key"
CONSTRAINT_CATEGORIA = "productos_id_categoria_fkey"
CONSTRAINTS_DETALLES = {
    "venta_detalle_id_producto_fkey",
    "compra_detalle_id_producto_fkey",
}


class RepositorioProductoSQLAlchemy(RepositorioProducto):
    def __init__(self, session: Session):
        self.session = session

    def crear(self, producto: Producto) -> Producto:
        modelo = nuevo_modelo(producto)
        self.session.add(modelo)

        try:
            self.session.flush()
        except IntegrityError as error:
            self._traducir_error_guardado(error, producto)
            raise

        return a_dominio(modelo)

    def obtener_por_id(self, id_producto: int) -> Producto | None:
        modelo = self.session.get(ProductoModelo, id_producto)

        if modelo is None:
            return None

        return a_dominio(modelo)

    def obtener_todos(self) -> list[Producto]:
        stmt = select(ProductoModelo).order_by(ProductoModelo.id_producto)
        modelos = self.session.scalars(stmt).all()

        return [a_dominio(modelo) for modelo in modelos]

    def obtener_para_modificar_stock(
        self,
        ids_producto: Sequence[int],
    ) -> dict[int, Producto]:
        ids_ordenados = sorted(set(ids_producto))
        if not ids_ordenados:
            return {}

        stmt = (
            select(ProductoModelo)
            .where(ProductoModelo.id_producto.in_(ids_ordenados))
            .order_by(ProductoModelo.id_producto)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        modelos = self.session.scalars(stmt).all()

        return {
            modelo.id_producto: a_dominio(modelo)
            for modelo in modelos
        }

    def actualizar_stocks(
        self,
        nuevos_stocks: Mapping[int, int],
    ) -> None:
        for id_producto in sorted(nuevos_stocks):
            stmt = (
                update(ProductoModelo)
                .where(ProductoModelo.id_producto == id_producto)
                .values(stock=nuevos_stocks[id_producto])
                .execution_options(synchronize_session="fetch")
            )
            resultado = self.session.execute(stmt)
            if resultado.rowcount != 1:
                raise EntidadNoEncontrada(
                    f"No se encontró el producto con id {id_producto}."
                )

        self.session.flush()

    def actualizar_datos(self, producto: Producto) -> Producto | None:
        stmt = (
            update(ProductoModelo)
            .where(ProductoModelo.id_producto == producto.id_producto)
            .values(
                codigo_barras=producto.codigo_barras,
                nombre=producto.nombre,
                precio_venta=producto.precio_venta,
                precio_compra=producto.precio_compra,
                id_categoria=producto.id_categoria,
            )
            .returning(ProductoModelo)
            .execution_options(populate_existing=True)
        )

        try:
            modelo = self.session.scalars(stmt).one_or_none()
            if modelo is None:
                return None
            self.session.flush()
        except IntegrityError as error:
            self._traducir_error_guardado(error, producto)
            raise

        self.session.refresh(modelo)
        return a_dominio(modelo)

    def eliminar(self, id_producto: int) -> bool:
        modelo = self.session.get(ProductoModelo, id_producto)

        if modelo is None:
            return False

        self.session.delete(modelo)

        try:
            self.session.flush()
        except IntegrityError as error:
            if isinstance(error.orig, ForeignKeyViolation):
                constraint = error.orig.diag.constraint_name
                if constraint in CONSTRAINTS_DETALLES:
                    raise ErrorDeValidacion(
                        "No se puede eliminar el producto porque tiene ventas "
                        "o compras asociadas."
                    ) from error
            raise

        return True

    @staticmethod
    def _traducir_error_guardado(
        error: IntegrityError,
        producto: Producto,
    ) -> None:
        if isinstance(error.orig, UniqueViolation):
            constraint = error.orig.diag.constraint_name
            if constraint != CONSTRAINT_CODIGO_BARRAS_UNICO:
                return
            raise EntidadDuplicada(
                "Ya existe un producto con ese código de barras."
            ) from error

        if isinstance(error.orig, ForeignKeyViolation):
            constraint = error.orig.diag.constraint_name
            if constraint != CONSTRAINT_CATEGORIA:
                return
            raise EntidadNoEncontrada(
                f"No se encontró la categoría con id {producto.id_categoria}."
            ) from error
