from sqlalchemy.exc import IntegrityError
from psycopg.errors import UniqueViolation
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from dominio.entidades.usuario import Usuario
from dominio.excepciones import EntidadDuplicada
from dominio.repositorios.repositorio_usuario import RepositorioUsuario
from infraestructura.basedatos.modelos.usuario_modelo import UsuarioModelo
from infraestructura.basedatos.mappers.usuario_mapper import a_dominio, nuevo_modelo

class RepositorioUsuarioSQLAlchemy(RepositorioUsuario):
    def __init__(self, session: Session):
        self.session = session
    
    def obtener_por_id(self, id_usuario: int) -> Usuario | None:
        stmt = (
            select(UsuarioModelo)
            .where(
                UsuarioModelo.id_usuario == id_usuario,
                UsuarioModelo.activo.is_(True),
            )
        )

        modelo = self.session.scalar(stmt)

        if modelo is None:
            return None

        return a_dominio(modelo)
    
    def obtener_por_email(self, email: str) -> Usuario | None:
        stmt = (
            select(UsuarioModelo)
            .where(
                UsuarioModelo.email == email,
                UsuarioModelo.activo.is_(True),
            )
        )

        modelo = self.session.scalar(stmt)

        if modelo is None:
            return None

        return a_dominio(modelo)
    
    def obtener_todos(self) -> list[Usuario]:
        stmt = (
            select(UsuarioModelo)
            .where(UsuarioModelo.activo.is_(True))
            .order_by(UsuarioModelo.id_usuario)
        )
        modelos = self.session.scalars(stmt).all()
        
        return [
            a_dominio(modelo)
            for modelo in modelos
        ]
    
    def crear(self, usuario: Usuario) -> Usuario:
        modelo = nuevo_modelo(usuario)
        self.session.add(modelo)
        
        try:
            self.session.flush()
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                constraint = e.orig.diag.constraint_name
                if constraint == "usuarios_email_key":
                    raise EntidadDuplicada(
                        f"Ya existe un usuario con email '{usuario.email}'."
                    ) from e
                if constraint == "usuarios_dni_key":
                    raise EntidadDuplicada(
                        f"Ya existe un usuario con DNI '{usuario.dni}'."
                    ) from e
            raise
        
        return a_dominio(modelo)
    
    def actualizar(self, usuario: Usuario) -> Usuario | None:
        modelo = self.session.get(
            UsuarioModelo,
            usuario.id_usuario,
        )

        if modelo is None:
            return None

        modelo.apellido = usuario.apellido
        modelo.nombre = usuario.nombre
        modelo.dni = usuario.dni
        modelo.telefono = usuario.telefono
        modelo.email = usuario.email
        modelo.rol = usuario.rol

        try:
            self.session.flush()

        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                constraint = e.orig.diag.constraint_name

                if constraint == "usuarios_email_key":
                    raise EntidadDuplicada(
                        f"Ya existe un usuario con email '{usuario.email}'."
                    ) from e

                if constraint == "usuarios_dni_key":
                    raise EntidadDuplicada(
                        f"Ya existe un usuario con DNI '{usuario.dni}'."
                    ) from e

            raise

        return a_dominio(modelo)    
    
    def eliminar(self, id_usuario: int) -> bool:
        modelo = self.session.get(
            UsuarioModelo,
            id_usuario,
        )
        
        if modelo is None:
            return False
        
        modelo.activo = False
        
        self.session.flush()
        
        return True
    
    def actualizar_password(
        self,
        id_usuario: int,
        password_hash: str,
    ) -> bool:
        stmt = (
            update(UsuarioModelo)
            .where(
                UsuarioModelo.id_usuario == id_usuario,
                UsuarioModelo.activo.is_(True),
            )
            .values(password_hash=password_hash)
            .returning(UsuarioModelo.id_usuario)
        )

        id_actualizado = self.session.execute(stmt).scalar_one_or_none()
        return id_actualizado is not None
