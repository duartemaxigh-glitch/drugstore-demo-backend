from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from infraestructura.basedatos.base import Base

class CategoriaModelo(Base):
    __tablename__ = "categorias"
    __table_args__ = (
        UniqueConstraint("nombre", name="categorias_nombre_key"),
    )

    id_categoria: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
