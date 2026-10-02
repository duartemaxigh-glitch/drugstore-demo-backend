# ============================================================
# Caso de Uso: Eliminar Proveedor
# ============================================================

from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_proveedor import RepositorioProveedor


class EliminarProveedor:
    def __init__(self, repositorio: RepositorioProveedor):
        self.repositorio = repositorio

    def ejecutar(self, id_proveedor: int) -> None:
        existente = self.repositorio.obtener_por_id(id_proveedor)
        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el proveedor con id {id_proveedor}."
            )
        
        eliminado = self.repositorio.eliminar(id_proveedor)

        if not eliminado:
            raise EntidadNoEncontrada(
                f"No se encontró el proveedor con id {id_proveedor}."
            )
