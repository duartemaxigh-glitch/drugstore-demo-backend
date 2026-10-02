# ============================================================
# Caso de Uso: Obtener Cliente por ID
# ============================================================

from dominio.entidades.cliente import Cliente
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_cliente import RepositorioCliente


class ObtenerCliente:
    def __init__(self, repositorio: RepositorioCliente):
        self.repositorio = repositorio

    def ejecutar(self, id_cliente: int) -> Cliente:
        cliente = self.repositorio.obtener_por_id(id_cliente)
        if cliente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el cliente con id {id_cliente}."
            )
        return cliente
