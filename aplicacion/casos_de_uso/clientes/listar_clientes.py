# ============================================================
# Caso de Uso: Listar todos los Clientes
# ============================================================

from dominio.entidades.cliente import Cliente
from dominio.repositorios.repositorio_cliente import RepositorioCliente


class ListarClientes:
    def __init__(self, repositorio: RepositorioCliente):
        self.repositorio = repositorio

    def ejecutar(self) -> list[Cliente]:
        return self.repositorio.obtener_todos()
