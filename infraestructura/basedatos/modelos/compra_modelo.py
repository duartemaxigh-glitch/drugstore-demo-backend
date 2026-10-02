from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infraestructura.basedatos.base import Base
from infraestructura.basedatos.modelos.producto_modelo import ProductoModelo
from infraestructura.basedatos.modelos.proveedor_modelo import ProveedorModelo
from infraestructura.basedatos.modelos.usuario_modelo import UsuarioModelo


class CompraModelo(Base):
    __tablename__ = "compras"

    id_compra: Mapped[int] = mapped_column(
        primary_key=True,
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    id_proveedor: Mapped[int] = mapped_column(
        ForeignKey(
            ProveedorModelo.id_proveedor,
            name="compras_id_proveedor_fkey",
        ),
        nullable=False,
    )
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey(
            UsuarioModelo.id_usuario,
            name="compras_id_usuario_fkey",
        ),
        nullable=False,
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    detalles: Mapped[list[CompraDetalleModelo]] = relationship(
        back_populates="compra",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class CompraDetalleModelo(Base):
    __tablename__ = "compra_detalle"

    id_detalle: Mapped[int] = mapped_column(
        primary_key=True,
    )
    id_compra: Mapped[int] = mapped_column(
        ForeignKey(
            CompraModelo.id_compra,
            name="compra_detalle_id_compra_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    id_producto: Mapped[int] = mapped_column(
        ForeignKey(
            ProductoModelo.id_producto,
            name="compra_detalle_id_producto_fkey",
        ),
        nullable=False,
    )
    cantidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    compra: Mapped[CompraModelo] = relationship(
        back_populates="detalles",
    )
