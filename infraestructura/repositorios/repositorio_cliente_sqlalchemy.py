from psycopg.errors import UniqueViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dominio.entidades.cliente import Cliente
from dominio.excepciones import EntidadDuplicada
from dominio.repositorios.repositorio_cliente import RepositorioCliente
from infraestructura.basedatos.mappers.cliente_mapper import a_dominio, nuevo_modelo
from infraestructura.basedatos.modelos.cliente_modelo import ClienteModelo


CONSTRAINTS_IDENTIFICACION_UNICA = {
    "clientes_dni_key",
    "clientes_cuit_key",
}


class RepositorioClienteSQLAlchemy(RepositorioCliente):
    def __init__(self, session: Session):
        self.session = session

    def crear(self, cliente: Cliente) -> Cliente:
        modelo = nuevo_modelo(cliente)
        self.session.add(modelo)

        try:
            self.session.flush()
        except IntegrityError as error:
            self._traducir_duplicado(error)
            raise

        return a_dominio(modelo)

    def obtener_por_id(self, id_cliente: int) -> Cliente | None:
        stmt = select(ClienteModelo).where(
            ClienteModelo.id_cliente == id_cliente,
            ClienteModelo.activo.is_(True),
        )
        modelo = self.session.scalar(stmt)

        if modelo is None:
            return None

        return a_dominio(modelo)

    def obtener_todos(self) -> list[Cliente]:
        stmt = (
            select(ClienteModelo)
            .where(ClienteModelo.activo.is_(True))
            .order_by(ClienteModelo.id_cliente)
        )
        modelos = self.session.scalars(stmt).all()

        return [a_dominio(modelo) for modelo in modelos]

    def actualizar(self, cliente: Cliente) -> Cliente | None:
        modelo = self.session.get(ClienteModelo, cliente.id_cliente)

        if modelo is None:
            return None

        modelo.apellido = cliente.apellido
        modelo.nombre = cliente.nombre
        modelo.dni = cliente.dni
        modelo.cuit = cliente.cuit
        modelo.telefono = cliente.telefono

        try:
            self.session.flush()
        except IntegrityError as error:
            self._traducir_duplicado(error)
            raise

        return a_dominio(modelo)

    def eliminar(self, id_cliente: int) -> bool:
        modelo = self.session.get(ClienteModelo, id_cliente)

        if modelo is None:
            return False

        modelo.activo = False
        self.session.flush()
        return True

    @staticmethod
    def _traducir_duplicado(error: IntegrityError) -> None:
        if isinstance(error.orig, UniqueViolation):
            constraint = error.orig.diag.constraint_name
            if constraint in CONSTRAINTS_IDENTIFICACION_UNICA:
                raise EntidadDuplicada(
                    "Ya existe un cliente con ese DNI o CUIT."
                ) from error
