# ============================================================
# Interfaz: RepositorioCliente
# ============================================================
# Contrato para operaciones CRUD de clientes.
# ============================================================

from abc import ABC, abstractmethod

from dominio.entidades.cliente import Cliente


class RepositorioCliente(ABC):

    @abstractmethod
    def crear(self, cliente: Cliente) -> Cliente:
        pass

    @abstractmethod
    def obtener_por_id(self, id_cliente: int) -> Cliente | None:
        pass

    @abstractmethod
    def obtener_todos(self) -> list[Cliente]:
        pass

    @abstractmethod
    def actualizar(self, cliente: Cliente) -> Cliente | None:
        pass

    @abstractmethod
    def eliminar(self, id_cliente: int) -> bool:
        pass
