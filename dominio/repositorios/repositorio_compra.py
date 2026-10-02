# ============================================================
# Interfaz: RepositorioCompra
# ============================================================
# Contrato para operaciones CRUD de compras.
# Una compra siempre se crea CON sus detalles (productos).
# ============================================================

from abc import ABC, abstractmethod

from dominio.entidades.compra import Compra


class RepositorioCompra(ABC):

    @abstractmethod
    def crear(self, compra: Compra) -> Compra:
        pass

    @abstractmethod
    def obtener_por_id(self, id_compra: int) -> Compra | None:
        pass

    @abstractmethod
    def obtener_para_eliminar(self, id_compra: int) -> Compra | None:
        pass

    @abstractmethod
    def obtener_todos(self) -> list[Compra]:
        pass

    @abstractmethod
    def eliminar(self, id_compra: int) -> bool:
        pass
