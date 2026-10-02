# ============================================================
# Caso de Uso: Crear Medio de Pago
# ============================================================

from dominio.entidades.medio_pago import MedioPago
from dominio.repositorios.repositorio_medio_pago import RepositorioMedioPago


class CrearMedioPago:
    def __init__(self, repositorio: RepositorioMedioPago):
        self.repositorio = repositorio

    def ejecutar(self, nombre: str) -> MedioPago:
        medio_pago = MedioPago(nombre=nombre)
        medio_pago.validar()
        return self.repositorio.crear(medio_pago)
