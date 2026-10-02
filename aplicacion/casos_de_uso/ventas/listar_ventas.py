# ============================================================
# Caso de Uso: Listar todas las Ventas
# ============================================================

from dominio.entidades.venta import Venta
from dominio.repositorios.repositorio_venta import RepositorioVenta


class ListarVentas:
    def __init__(self, repositorio: RepositorioVenta):
        self.repositorio = repositorio

    def ejecutar(self) -> list[Venta]:
        return self.repositorio.obtener_todos()
