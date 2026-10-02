# ============================================================
# Interfaz: RepositorioProveedor
# ============================================================
# Contrato para operaciones CRUD de proveedores.
# ============================================================

from abc import ABC, abstractmethod

from dominio.entidades.proveedor import Proveedor


class RepositorioProveedor(ABC):

    @abstractmethod
    def crear(self, proveedor: Proveedor) -> Proveedor:
        pass

    @abstractmethod
    def obtener_por_id(self, id_proveedor: int) -> Proveedor | None:
        pass

    @abstractmethod
    def obtener_todos(self) -> list[Proveedor]:
        pass

    @abstractmethod
    def actualizar(self, proveedor: Proveedor) -> Proveedor | None:
        pass

    @abstractmethod
    def eliminar(self, id_proveedor: int) -> bool:
        pass
