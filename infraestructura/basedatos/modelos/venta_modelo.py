from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infraestructura.basedatos.base import Base
from infraestructura.basedatos.modelos.cliente_modelo import ClienteModelo
from infraestructura.basedatos.modelos.medio_pago_modelo import MedioPagoModelo
from infraestructura.basedatos.modelos.producto_modelo import ProductoModelo
from infraestructura.basedatos.modelos.usuario_modelo import UsuarioModelo


class VentaModelo(Base):
    __tablename__ = "ventas"

    id_venta: Mapped[int] = mapped_column(
        primary_key=True,
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey(
            UsuarioModelo.id_usuario,
            name="ventas_id_usuario_fkey",
        ),
        nullable=False,
    )
    id_cliente: Mapped[int | None] = mapped_column(
        ForeignKey(
            ClienteModelo.id_cliente,
            name="ventas_id_cliente_fkey",
        ),
        nullable=True,
    )
    id_medio_pago: Mapped[int] = mapped_column(
        ForeignKey(
            MedioPagoModelo.id_medio_pago,
            name="ventas_id_medio_pago_fkey",
        ),
        nullable=False,
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    detalles: Mapped[list[VentaDetalleModelo]] = relationship(
        back_populates="venta",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class VentaDetalleModelo(Base):
    __tablename__ = "venta_detalle"

    id_detalle: Mapped[int] = mapped_column(
        primary_key=True,
    )
    id_venta: Mapped[int] = mapped_column(
        ForeignKey(
            VentaModelo.id_venta,
            name="venta_detalle_id_venta_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    id_producto: Mapped[int] = mapped_column(
        ForeignKey(
            ProductoModelo.id_producto,
            name="venta_detalle_id_producto_fkey",
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
    venta: Mapped[VentaModelo] = relationship(
        back_populates="detalles",
    )
