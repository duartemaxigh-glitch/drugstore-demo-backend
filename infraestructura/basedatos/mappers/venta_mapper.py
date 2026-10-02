from collections.abc import Iterable

from dominio.entidades.venta import Venta, VentaDetalle
from infraestructura.basedatos.modelos.venta_modelo import (
    VentaDetalleModelo,
    VentaModelo,
)


def detalle_a_dominio(modelo: VentaDetalleModelo) -> VentaDetalle:
    return VentaDetalle(
        id_detalle=modelo.id_detalle,
        id_venta=modelo.id_venta,
        id_producto=modelo.id_producto,
        cantidad=modelo.cantidad,
        precio_unitario=modelo.precio_unitario,
        subtotal=modelo.subtotal,
    )


def a_dominio_con_detalles(
    modelo: VentaModelo,
    detalles: Iterable[VentaDetalleModelo],
) -> Venta:
    return Venta(
        id_venta=modelo.id_venta,
        fecha=modelo.fecha,
        id_usuario=modelo.id_usuario,
        id_cliente=modelo.id_cliente,
        id_medio_pago=modelo.id_medio_pago,
        total=modelo.total,
        detalles=[detalle_a_dominio(detalle) for detalle in detalles],
    )


def a_dominio(modelo: VentaModelo) -> Venta:
    return a_dominio_con_detalles(modelo, modelo.detalles)


def nuevo_modelo(venta: Venta) -> VentaModelo:
    return VentaModelo(
        id_usuario=venta.id_usuario,
        id_cliente=venta.id_cliente,
        id_medio_pago=venta.id_medio_pago,
        total=venta.total,
        detalles=[
            VentaDetalleModelo(
                id_producto=detalle.id_producto,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario,
                subtotal=detalle.subtotal,
            )
            for detalle in venta.detalles
        ],
    )
