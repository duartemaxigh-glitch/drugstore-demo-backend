# ============================================================
# Caso de Uso: Actualizar Producto
# ============================================================

from __future__ import annotations

from decimal import Decimal

from dominio.dinero import normalizar_dinero
from dominio.entidades.producto import Producto
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_producto import RepositorioProducto


class ActualizarProducto:
    def __init__(self, repositorio: RepositorioProducto):
        self.repositorio = repositorio

    def ejecutar(
        self,
        id_producto: int,
        nombre: str,
        precio_venta: Decimal,
        precio_compra: Decimal,
        codigo_barras: str | None = None,
        id_categoria: int | None = None,
    ) -> Producto:
        existente = self.repositorio.obtener_por_id(id_producto)
        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el producto con id {id_producto}."
            )

        # Preservar el stock actual — solo se modifica via ventas/compras
        producto = Producto(
            id_producto=id_producto,
            nombre=nombre,
            precio_venta=normalizar_dinero(precio_venta, 'precio_venta'),
            precio_compra=normalizar_dinero(precio_compra, 'precio_compra'),
            stock=existente.stock,
            codigo_barras=codigo_barras,
            id_categoria=id_categoria,
        )
        producto.validar()
        actualizado = self.repositorio.actualizar_datos(producto)

        if actualizado is None:
            raise EntidadNoEncontrada(
                f"No se encontró el producto con id {id_producto}."
            )

        return actualizado
