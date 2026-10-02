# ============================================================
# Caso de Uso: Obtener Proveedor por ID
# ============================================================

from dominio.entidades.proveedor import Proveedor
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_proveedor import RepositorioProveedor


class ObtenerProveedor:
    def __init__(self, repositorio: RepositorioProveedor):
        self.repositorio = repositorio

    def ejecutar(self, id_proveedor: int) -> Proveedor:
        proveedor = self.repositorio.obtener_por_id(id_proveedor)
        if proveedor is None:
            raise EntidadNoEncontrada(
                f"No se encontró el proveedor con id {id_proveedor}."
            )
        return proveedor
