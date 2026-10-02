from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from infraestructura.basedatos.base import Base
from infraestructura.basedatos.modelos.categoria_modelo import CategoriaModelo


class ProductoModelo(Base):
    __tablename__ = "productos"
    __table_args__ = (
        UniqueConstraint(
            "codigo_barras",
            name="productos_codigo_barras_key",
        ),
        Index("idx_productos_nombre", "nombre"),
    )

    id_producto: Mapped[int] = mapped_column(
        primary_key=True,
    )
    codigo_barras: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    nombre: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )
    precio_venta: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    precio_compra: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    id_categoria: Mapped[int | None] = mapped_column(
        ForeignKey(
            CategoriaModelo.id_categoria,
            name="productos_id_categoria_fkey",
        ),
        nullable=True,
    )
