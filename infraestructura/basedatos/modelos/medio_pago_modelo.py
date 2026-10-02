from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from infraestructura.basedatos.base import Base


class MedioPagoModelo(Base):
    __tablename__ = "medios_pago"
    __table_args__ = (
        UniqueConstraint("nombre", name="medios_pago_nombre_key"),
    )

    id_medio_pago: Mapped[int] = mapped_column(
        primary_key=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
