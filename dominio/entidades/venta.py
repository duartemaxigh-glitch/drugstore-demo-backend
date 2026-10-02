# ============================================================
# Entidades: Venta y VentaDetalle
# ============================================================
# Una Venta tiene muchos VentaDetalle (relación 1 a muchos).
# Cada detalle es un producto vendido con su cantidad y precio.
# ============================================================

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from dominio.validaciones import validar_cantidad, validar_precio


class VentaDetalle:
    def __init__(
        self,
        id_producto: int,
        cantidad: int,
        precio_unitario: Decimal,
        subtotal: Decimal,
        id_detalle: int | None = None,
        id_venta: int | None = None,
    ):
        self.id_detalle = id_detalle
        self.id_venta = id_venta
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = subtotal

    def validar(self):
        validar_cantidad(self.cantidad, 'cantidad')
        validar_precio(self.precio_unitario, 'precio_unitario')
        validar_precio(self.subtotal, 'subtotal')


class Venta:
    def __init__(
        self,
        id_usuario: int,
        id_medio_pago: int,
        total: Decimal,
        detalles: list[VentaDetalle],
        id_cliente: int | None = None,
        fecha: datetime | None = None,
        id_venta: int | None = None,
    ):
        self.id_venta = id_venta
        self.fecha = fecha
        self.id_usuario = id_usuario
        self.id_cliente = id_cliente
        self.id_medio_pago = id_medio_pago
        self.total = total
        self.detalles = detalles

    def validar(self):
        validar_precio(self.total, 'total')
        for detalle in self.detalles:
            detalle.validar()
