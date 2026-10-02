# ============================================================
# Interfaz: RepositorioVenta
# ============================================================
# Contrato para operaciones CRUD de ventas.
# Una venta siempre se crea CON sus detalles (productos).
# ============================================================

from abc import ABC, abstractmethod

from dominio.entidades.venta import Venta


class RepositorioVenta(ABC):

    @abstractmethod
    def crear(self, venta: Venta) -> Venta:
        pass

    @abstractmethod
    def obtener_por_id(self, id_venta: int) -> Venta | None:
        pass

    @abstractmethod
    def obtener_para_eliminar(self, id_venta: int) -> Venta | None:
        pass

    @abstractmethod
    def obtener_todos(self) -> list[Venta]:
        pass

    @abstractmethod
    def eliminar(self, id_venta: int) -> bool:
        pass
