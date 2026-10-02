# ============================================================
# Caso de Uso: Listar todos los Medios de Pago
# ============================================================

from dominio.entidades.medio_pago import MedioPago
from dominio.repositorios.repositorio_medio_pago import RepositorioMedioPago


class ListarMediosPago:
    def __init__(self, repositorio: RepositorioMedioPago):
        self.repositorio = repositorio

    def ejecutar(self) -> list[MedioPago]:
        return self.repositorio.obtener_todos()
