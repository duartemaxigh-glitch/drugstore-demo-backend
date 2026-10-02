# ============================================================
# Interfaz: RepositorioProducto
# ============================================================
# Contrato para operaciones CRUD de productos.
# ============================================================

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

from dominio.entidades.producto import Producto


class RepositorioProducto(ABC):

    @abstractmethod
    def crear(self, producto: Producto) -> Producto:
        pass

    @abstractmethod
    def obtener_por_id(self, id_producto: int) -> Producto | None:
        pass

    @abstractmethod
    def obtener_todos(self) -> list[Producto]:
        pass

    @abstractmethod
    def obtener_para_modificar_stock(
        self,
        ids_producto: Sequence[int],
    ) -> dict[int, Producto]:
        pass

    @abstractmethod
    def actualizar_stocks(
        self,
        nuevos_stocks: Mapping[int, int],
    ) -> None:
        pass

    @abstractmethod
    def actualizar_datos(self, producto: Producto) -> Producto | None:
        pass

    @abstractmethod
    def eliminar(self, id_producto: int) -> bool:
        pass
