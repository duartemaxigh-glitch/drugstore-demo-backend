# ============================================================
# Caso de Uso: Crear Venta
# ============================================================
# Una venta se crea con todos sus detalles de una sola vez.
# Además, al vender se DESCUENTA el stock de cada producto.
#
# Todo ocurre dentro de una transacción: si algo falla,
# no se descuenta stock ni se crea la venta.
# ============================================================

from dominio.dinero import CERO_DINERO, normalizar_dinero
from dominio.entidades.venta import Venta, VentaDetalle
from dominio.excepciones import EntidadNoEncontrada, ErrorDeValidacion
from dominio.repositorios.repositorio_producto import RepositorioProducto
from dominio.repositorios.repositorio_venta import RepositorioVenta


class CrearVenta:
    def __init__(
        self,
        repositorio_venta: RepositorioVenta,
        repositorio_producto: RepositorioProducto,
    ):
        self.repositorio_venta = repositorio_venta
        self.repositorio_producto = repositorio_producto

    def ejecutar(
        self,
        id_usuario: int,
        id_medio_pago: int,
        detalles: list[dict],
        id_cliente: int | None = None,
    ) -> Venta:
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

            # Verificamos que haya stock suficiente
            if producto.stock < item['cantidad']:
                raise ErrorDeValidacion(
                    f"Stock insuficiente para '{producto.nombre}'. "
                    f"Disponible: {producto.stock}, solicitado: {item['cantidad']}."
                )

            precio_unitario = normalizar_dinero(
                producto.precio_venta,
                'precio_unitario',
            )
            subtotal = normalizar_dinero(
                precio_unitario * item['cantidad'],
                'subtotal',
            )
            detalle = VentaDetalle(
                id_producto=item['id_producto'],
                cantidad=item['cantidad'],
                precio_unitario=precio_unitario,
                subtotal=subtotal,
            )
            detalle.validar()
            lista_detalles.append(detalle)
            total += subtotal

            # Descontamos el stock
            producto.stock -= item['cantidad']

        self.repositorio_producto.actualizar_stocks(
            {
                id_producto: producto.stock
                for id_producto, producto in productos.items()
            }
        )

        venta = Venta(
            id_usuario=id_usuario,
            id_cliente=id_cliente,
            id_medio_pago=id_medio_pago,
            total=normalizar_dinero(total, 'total'),
            detalles=lista_detalles,
        )
        venta.validar()
        return self.repositorio_venta.crear(venta)
