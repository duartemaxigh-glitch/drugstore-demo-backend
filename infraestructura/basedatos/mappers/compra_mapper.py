from collections.abc import Iterable

from dominio.entidades.compra import Compra, CompraDetalle
from infraestructura.basedatos.modelos.compra_modelo import (
    CompraDetalleModelo,
    CompraModelo,
)


def detalle_a_dominio(modelo: CompraDetalleModelo) -> CompraDetalle:
    return CompraDetalle(
        id_detalle=modelo.id_detalle,
        id_compra=modelo.id_compra,
        id_producto=modelo.id_producto,
        cantidad=modelo.cantidad,
        precio_unitario=modelo.precio_unitario,
        subtotal=modelo.subtotal,
    )


def a_dominio_con_detalles(
    modelo: CompraModelo,
    detalles: Iterable[CompraDetalleModelo],
) -> Compra:
    return Compra(
        id_compra=modelo.id_compra,
        fecha=modelo.fecha,
        id_proveedor=modelo.id_proveedor,
        id_usuario=modelo.id_usuario,
        total=modelo.total,
        detalles=[detalle_a_dominio(detalle) for detalle in detalles],
    )


def a_dominio(modelo: CompraModelo) -> Compra:
    return a_dominio_con_detalles(modelo, modelo.detalles)


def nuevo_modelo(compra: Compra) -> CompraModelo:
    return CompraModelo(
        id_proveedor=compra.id_proveedor,
        id_usuario=compra.id_usuario,
        total=compra.total,
        detalles=[
            CompraDetalleModelo(
                id_producto=detalle.id_producto,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario,
                subtotal=detalle.subtotal,
            )
            for detalle in compra.detalles
        ],
    )
