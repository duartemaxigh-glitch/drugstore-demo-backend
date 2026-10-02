# ============================================================
# Caso de Uso: Eliminar Cliente
# ============================================================

from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_cliente import RepositorioCliente


class EliminarCliente:
    def __init__(self, repositorio: RepositorioCliente):
        self.repositorio = repositorio

    def ejecutar(self, id_cliente: int) -> None:
        existente = self.repositorio.obtener_por_id(id_cliente)
        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el cliente con id {id_cliente}."
            )
        eliminado = self.repositorio.eliminar(id_cliente)

        if not eliminado:
            raise EntidadNoEncontrada(
                f"No se encontró el cliente con id {id_cliente}."
            )
