# ============================================================
# Interfaz: RepositorioMedioPago
# ============================================================
# Contrato para operaciones CRUD de medios de pago.
# ============================================================

from abc import ABC, abstractmethod

from dominio.entidades.medio_pago import MedioPago


class RepositorioMedioPago(ABC):

    @abstractmethod
    def crear(self, medio_pago: MedioPago) -> MedioPago:
        pass

    @abstractmethod
    def obtener_por_id(self, id_medio_pago: int) -> MedioPago | None:
        pass

    @abstractmethod
    def obtener_todos(self) -> list[MedioPago]:
        pass

    @abstractmethod
    def actualizar(self, medio_pago: MedioPago) -> MedioPago | None:
        pass

    @abstractmethod
    def eliminar(self, id_medio_pago: int) -> bool:
        pass
