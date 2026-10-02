# ============================================================
# Caso de Uso: Obtener Venta por ID
# ============================================================

from dominio.entidades.venta import Venta
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_venta import RepositorioVenta


class ObtenerVenta:
    def __init__(self, repositorio: RepositorioVenta):
        self.repositorio = repositorio

    def ejecutar(self, id_venta: int) -> Venta:
        venta = self.repositorio.obtener_por_id(id_venta)
        if venta is None:
            raise EntidadNoEncontrada(
                f"No se encontró la venta con id {id_venta}."
            )
        return venta
