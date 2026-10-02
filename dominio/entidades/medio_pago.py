# ============================================================
# Entidad: MedioPago
# ============================================================
# Representa una fila de la tabla 'medios_pago'.
# Ejemplo: Efectivo, Tarjeta de Crédito, Transferencia, etc.
# ============================================================

from dominio.validaciones import validar_no_vacio


class MedioPago:
    def __init__(self, nombre: str, id_medio_pago: int = None):
        self.id_medio_pago = id_medio_pago
        self.nombre = nombre

    def validar(self):
        validar_no_vacio(self.nombre, 'nombre')
