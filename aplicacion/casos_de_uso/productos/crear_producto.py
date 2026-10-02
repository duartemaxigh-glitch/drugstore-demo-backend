# ============================================================
# Caso de Uso: Crear Producto
# ============================================================

from __future__ import annotations

from decimal import Decimal

from dominio.dinero import normalizar_dinero
from dominio.entidades.producto import Producto
from dominio.repositorios.repositorio_producto import RepositorioProducto


class CrearProducto:
    def __init__(self, repositorio: RepositorioProducto):
        self.repositorio = repositorio

    def ejecutar(
        self,
        nombre: str,
        precio_venta: Decimal,
        precio_compra: Decimal,
        stock: int = 0,
        codigo_barras: str | None = None,
        id_categoria: int | None = None,
    ) -> Producto:
        producto = Producto(
            nombre=nombre,
            precio_venta=normalizar_dinero(precio_venta, 'precio_venta'),
            precio_compra=normalizar_dinero(precio_compra, 'precio_compra'),
            stock=stock,
            codigo_barras=codigo_barras,
            id_categoria=id_categoria,
        )
        producto.validar()
        return self.repositorio.crear(producto)
