# ============================================================
# Caso de Uso: Obtener Compra por ID
# ============================================================

from dominio.entidades.compra import Compra
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_compra import RepositorioCompra


class ObtenerCompra:
    def __init__(self, repositorio: RepositorioCompra):
        self.repositorio = repositorio

    def ejecutar(self, id_compra: int) -> Compra:
        compra = self.repositorio.obtener_por_id(id_compra)
        if compra is None:
            raise EntidadNoEncontrada(
                f"No se encontró la compra con id {id_compra}."
            )
        return compra
