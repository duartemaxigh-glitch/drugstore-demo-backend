# ============================================================
# Caso de Uso: Listar todos los Proveedores
# ============================================================

from dominio.entidades.proveedor import Proveedor
from dominio.repositorios.repositorio_proveedor import RepositorioProveedor


class ListarProveedores:
    def __init__(self, repositorio: RepositorioProveedor):
        self.repositorio = repositorio

    def ejecutar(self) -> list[Proveedor]:
        return self.repositorio.obtener_todos()
