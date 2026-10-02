# ============================================================
# Caso de Uso: Actualizar Medio de Pago
# ============================================================

from dominio.entidades.medio_pago import MedioPago
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_medio_pago import RepositorioMedioPago


class ActualizarMedioPago:
    def __init__(self, repositorio: RepositorioMedioPago):
        self.repositorio = repositorio

    def ejecutar(self, id_medio_pago: int, nombre: str) -> MedioPago:
        existente = self.repositorio.obtener_por_id(id_medio_pago)
        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el medio de pago con id {id_medio_pago}."
            )

        medio_pago = MedioPago(nombre=nombre, id_medio_pago=id_medio_pago)
        medio_pago.validar()
        actualizado = self.repositorio.actualizar(medio_pago)

        if actualizado is None:
            raise EntidadNoEncontrada(
                f"No se encontró el medio de pago con id {id_medio_pago}."
            )

        return actualizado