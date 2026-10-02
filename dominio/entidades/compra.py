# ============================================================
# Entidades: Compra y CompraDetalle
# ============================================================
# Una Compra tiene muchos CompraDetalle (relación 1 a muchos).
# Cada detalle es un producto comprado al proveedor.
# ============================================================

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from dominio.validaciones import validar_cantidad, validar_precio


class CompraDetalle:
    def __init__(
        self,
        id_producto: int,
        cantidad: int,
        precio_unitario: Decimal,
        subtotal: Decimal,
        id_detalle: int | None = None,
        id_compra: int | None = None,
    ):
        self.id_detalle = id_detalle
        self.id_compra = id_compra
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = subtotal

    def validar(self):
        validar_cantidad(self.cantidad, 'cantidad')
        validar_precio(self.precio_unitario, 'precio_unitario')
        validar_precio(self.subtotal, 'subtotal')


class Compra:
    def __init__(
        self,
        id_proveedor: int,
        id_usuario: int,
        total: Decimal,
        detalles: list[CompraDetalle],
        fecha: datetime | None = None,
        id_compra: int | None = None,
    ):
        self.id_compra = id_compra
        self.fecha = fecha
        self.id_proveedor = id_proveedor
        self.id_usuario = id_usuario
        self.total = total
        self.detalles = detalles

    def validar(self):
        validar_precio(self.total, 'total')
        for detalle in self.detalles:
            detalle.validar()
