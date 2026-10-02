from sqlalchemy import Boolean, CheckConstraint, String, UniqueConstraint, true
from sqlalchemy.orm import Mapped, mapped_column
from infraestructura.basedatos.base import Base

class UsuarioModelo(Base):
    __tablename__ = "usuarios"
    
    id_usuario: Mapped[int] = mapped_column(primary_key=True)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    dni: Mapped[str] = mapped_column(String(15), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False, server_default='empleado')
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())
    
    __table_args__ = (
        UniqueConstraint("dni", name="usuarios_dni_key"),
        UniqueConstraint("email", name="usuarios_email_key"),
        CheckConstraint(rol.in_(['jefe', 'empleado']), name='usuarios_rol_check'),
    )
