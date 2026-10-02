# ============================================================
# Caso de Uso: Crear Compra
# ============================================================
# Una compra se registra con todos sus detalles de una vez.
# Al comprar, se SUMA stock a cada producto (lo opuesto a venta).
#
# Todo ocurre dentro de una transacción: si algo falla,
# no se suma stock ni se crea la compra.
# ============================================================

from dominio.dinero import CERO_DINERO, normalizar_dinero
from dominio.entidades.compra import Compra, CompraDetalle
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_compra import RepositorioCompra
from dominio.repositorios.repositorio_producto import RepositorioProducto


class CrearCompra:
    def __init__(
        self,
        repositorio_compra: RepositorioCompra,
        repositorio_producto: RepositorioProducto,
    ):
        self.repositorio_compra = repositorio_compra
        self.repositorio_producto = repositorio_producto

    def ejecutar(
        self,
        id_proveedor: int,
        id_usuario: int,
        detalles: list[dict],
    ) -> Compra:
        lista_detalles = []
        total = CERO_DINERO
        ids_producto = [item['id_producto'] for item in detalles]
        productos = self.repositorio_producto.obtener_para_modificar_stock(
            ids_producto
        )

        for item in detalles:
            # Verificamos que el producto exista
            producto = productos.get(item['id_producto'])
            if producto is None:
                raise EntidadNoEncontrada(
                    f"No se encontró el producto con id {item['id_producto']}."
                )

            precio_unitario = normalizar_dinero(
                item['precio_unitario'],
                'precio_unitario',
            )
            subtotal = normalizar_dinero(
                precio_unitario * item['cantidad'],
                'subtotal',
            )
            detalle = CompraDetalle(
                id_producto=item['id_producto'],
                cantidad=item['cantidad'],
                precio_unitario=precio_unitario,
                subtotal=subtotal,
            )
            detalle.validar()
            lista_detalles.append(detalle)
            total += subtotal

            # Sumamos el stock (compramos mercadería)
            producto.stock += item['cantidad']

        self.repositorio_producto.actualizar_stocks(
            {
                id_producto: producto.stock
                for id_producto, producto in productos.items()
            }
        )

        compra = Compra(
            id_proveedor=id_proveedor,
            id_usuario=id_usuario,
            total=normalizar_dinero(total, 'total'),
            detalles=lista_detalles,
        )
        compra.validar()
        return self.repositorio_compra.crear(compra)
