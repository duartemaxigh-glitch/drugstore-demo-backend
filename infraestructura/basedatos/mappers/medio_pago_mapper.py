from dominio.entidades.medio_pago import MedioPago
from infraestructura.basedatos.modelos.medio_pago_modelo import MedioPagoModelo

def a_dominio(modelo: MedioPagoModelo) -> MedioPago:
    return MedioPago(
        id_medio_pago=modelo.id_medio_pago,
        nombre=modelo.nombre,
    )

def nuevo_modelo(medio_pago: MedioPago) -> MedioPagoModelo:
    return MedioPagoModelo(
        nombre=medio_pago.nombre,
    )