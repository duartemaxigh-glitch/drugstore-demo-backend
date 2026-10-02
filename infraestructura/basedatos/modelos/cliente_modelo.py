from sqlalchemy import Boolean, String, UniqueConstraint, true
from sqlalchemy.orm import Mapped, mapped_column

from infraestructura.basedatos.base import Base


class ClienteModelo(Base):
    __tablename__ = "clientes"
    __table_args__ = (
        UniqueConstraint("dni", name="clientes_dni_key"),
        UniqueConstraint("cuit", name="clientes_cuit_key"),
    )

    id_cliente: Mapped[int] = mapped_column(
        primary_key=True,
    )
    apellido: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    nombre: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    dni: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    cuit: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    telefono: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=true(),
    )
