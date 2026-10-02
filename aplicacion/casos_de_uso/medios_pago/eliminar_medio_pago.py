# ============================================================
# Caso de Uso: Eliminar Medio de Pago
# ============================================================

from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_medio_pago import RepositorioMedioPago


class EliminarMedioPago:
    def __init__(self, repositorio: RepositorioMedioPago):
        self.repositorio = repositorio

    def ejecutar(self, id_medio_pago: int) -> None:
        existente = self.repositorio.obtener_por_id(id_medio_pago)
        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el medio de pago con id {id_medio_pago}."
            )
        eliminado = self.repositorio.eliminar(id_medio_pago)

        if not eliminado:
            raise EntidadNoEncontrada(
                f"No se encontró el medio de pago con id {id_medio_pago}."
            )