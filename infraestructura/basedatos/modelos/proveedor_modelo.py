from sqlalchemy import Boolean, String, UniqueConstraint, true
from sqlalchemy.orm import Mapped, mapped_column

from infraestructura.basedatos.base import Base


class ProveedorModelo(Base):
    __tablename__ = "proveedores"
    __table_args__ = (
        UniqueConstraint("cuit_cuil", name="proveedores_cuit_cuil_key"),
    )

    id_proveedor: Mapped[int] = mapped_column(
        primary_key=True,
    )
    razon_social: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )
    cuit_cuil: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    contacto_nombre: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    telefono: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )
    email: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=true(),
    )
