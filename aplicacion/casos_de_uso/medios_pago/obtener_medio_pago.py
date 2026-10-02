# ============================================================
# Caso de Uso: Obtener Medio de Pago por ID
# ============================================================

from dominio.entidades.medio_pago import MedioPago
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_medio_pago import RepositorioMedioPago


class ObtenerMedioPago:
    def __init__(self, repositorio: RepositorioMedioPago):
        self.repositorio = repositorio

    def ejecutar(self, id_medio_pago: int) -> MedioPago:
        medio_pago = self.repositorio.obtener_por_id(id_medio_pago)
        if medio_pago is None:
            raise EntidadNoEncontrada(
                f"No se encontró el medio de pago con id {id_medio_pago}."
            )
        return medio_pago
