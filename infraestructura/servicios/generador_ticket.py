# ============================================================
# Generador de Tickets para impresora térmica de 80mm
# ============================================================
# Una impresora de 80mm tiene un ancho de 48 caracteres
# (usando la fuente estándar monoespaciada).
#
# Este módulo genera el texto plano del ticket, formateado
# para que se vea bien al imprimirlo.
#
# ¿Por qué está en Infraestructura?
# Porque el FORMATO de impresión es un detalle técnico.
# Al Dominio no le importa si imprimís en papel de 80mm,
# 58mm o en A4. Solo le importan los datos de la venta.
# ============================================================

from datetime import datetime
from decimal import Decimal

ANCHO = 48  # Caracteres de ancho para impresora de 80mm


def _linea_separadora(caracter: str = '-') -> str:
    """Genera una línea separadora del ancho del ticket."""
    return caracter * ANCHO


def _centrar(texto: str) -> str:
    """Centra un texto en el ancho del ticket."""
    return texto.center(ANCHO)


def _linea_dos_columnas(izquierda: str, derecha: str) -> str:
    """Genera una línea con texto a la izquierda y a la derecha."""
    espacios = max(ANCHO - len(izquierda) - len(derecha), 1)
    return izquierda + ' ' * espacios + derecha


def generar_ticket(
    id_venta: int,
    fecha: datetime,
    usuario_nombre: str,
    cliente_nombre: str | None,
    medio_pago_nombre: str,
    detalles: list[dict],
    total: Decimal,
    nombre_negocio: str = 'DRUGSTORE',
    direccion_negocio: str = '',
    telefono_negocio: str = '',
) -> str:
    """
    Genera el texto completo del ticket de venta.

    Cada detalle debe ser un dict con:
        - producto_nombre: str
        - cantidad: int
        - precio_unitario: Decimal
        - subtotal: Decimal
    """
    lineas = []

    # === ENCABEZADO ===
    lineas.append('')
    lineas.append(_centrar(nombre_negocio))
    if direccion_negocio:
        lineas.append(_centrar(direccion_negocio))
    if telefono_negocio:
        lineas.append(_centrar(f'Tel: {telefono_negocio}'))
    lineas.append(_linea_separadora('='))

    # === DATOS DE LA VENTA ===
    lineas.append(f'Venta #: {id_venta}')
    lineas.append(f'Fecha: {fecha.strftime("%d/%m/%Y %H:%M")}')
    lineas.append(f'Cajero: {usuario_nombre}')
    if cliente_nombre:
        lineas.append(f'Cliente: {cliente_nombre}')
    lineas.append(f'Pago: {medio_pago_nombre}')
    lineas.append(_linea_separadora('-'))

    # === ENCABEZADO DE PRODUCTOS ===
    lineas.append(_linea_dos_columnas('PRODUCTO', 'SUBTOTAL'))
    lineas.append(_linea_separadora('-'))

    # === DETALLE DE PRODUCTOS ===
    for d in detalles:
        nombre = d['producto_nombre']
        # Si el nombre es muy largo, lo cortamos
        if len(nombre) > 30:
            nombre = nombre[:27] + '...'

        # Línea 1: nombre del producto y subtotal
        subtotal_str = f'${d["subtotal"]:.2f}'
        lineas.append(_linea_dos_columnas(nombre, subtotal_str))

        # Línea 2: cantidad x precio unitario (indentado)
        detalle_qty = f'  {d["cantidad"]} x ${d["precio_unitario"]:.2f}'
        lineas.append(detalle_qty)

    # === TOTAL ===
    lineas.append(_linea_separadora('='))
    total_str = f'${total:.2f}'
    lineas.append(_linea_dos_columnas('TOTAL', total_str))
    lineas.append(_linea_separadora('='))

    # === PIE ===
    lineas.append('')
    lineas.append(_centrar('Gracias por su compra!'))
    lineas.append('')

    return '\n'.join(lineas)


# ============================================================
# Ticket de Reporte Diario de Ventas
# ============================================================

def generar_ticket_reporte_ventas(reporte: dict, nombre_negocio: str = 'DRUGSTORE') -> str:
    """
    Genera un ticket con el resumen de ventas del día.

    reporte debe tener la estructura que devuelve
    servicio_reportes.obtener_reporte_ventas_por_dia()
    """
    lineas = []

    # === ENCABEZADO ===
    lineas.append('')
    lineas.append(_centrar(nombre_negocio))
    lineas.append(_centrar('REPORTE DE VENTAS'))
    lineas.append(_linea_separadora('='))

    # === DATOS DEL REPORTE ===
    lineas.append(f'Fecha: {reporte["fecha"]}')
    lineas.append(f'Cantidad de ventas: {reporte["cantidad_ventas"]}')
    lineas.append(_linea_separadora('-'))

    # === ENCABEZADO DE TABLA ===
    lineas.append(_linea_dos_columnas('#VENTA  HORA', 'TOTAL'))
    lineas.append(_linea_separadora('-'))

    # === DETALLE DE VENTAS ===
    for v in reporte['ventas']:
        izq = f'#{v["id_venta"]:<6} {v["hora"]}'
        der = f'${v["total"]:.2f}'
        lineas.append(_linea_dos_columnas(izq, der))

        # Segunda línea: cajero y medio de pago
        info = f'  {v["cajero"]} | {v["medio_pago"]}'
        if len(info) > ANCHO:
            info = info[:ANCHO]
        lineas.append(info)

        # Tercera línea: cliente (si tiene)
        if v['cliente']:
            lineas.append(f'  Cliente: {v["cliente"]}')

    # === TOTAL DEL DÍA ===
    lineas.append(_linea_separadora('='))
    total_str = f'${reporte["total_dia"]:.2f}'
    lineas.append(_linea_dos_columnas('TOTAL DEL DIA', total_str))
    lineas.append(_linea_separadora('='))
    lineas.append('')

    return '\n'.join(lineas)


# ============================================================
# Ticket de Reporte Diario de Compras
# ============================================================

def generar_ticket_reporte_compras(reporte: dict, nombre_negocio: str = 'DRUGSTORE') -> str:
    """
    Genera un ticket con el resumen de compras del día.

    reporte debe tener la estructura que devuelve
    servicio_reportes.obtener_reporte_compras_por_dia()
    """
    lineas = []

    # === ENCABEZADO ===
    lineas.append('')
    lineas.append(_centrar(nombre_negocio))
    lineas.append(_centrar('REPORTE DE COMPRAS'))
    lineas.append(_linea_separadora('='))

    # === DATOS DEL REPORTE ===
    lineas.append(f'Fecha: {reporte["fecha"]}')
    lineas.append(f'Cantidad de compras: {reporte["cantidad_compras"]}')
    lineas.append(_linea_separadora('-'))

    # === ENCABEZADO DE TABLA ===
    lineas.append(_linea_dos_columnas('#COMPRA HORA', 'TOTAL'))
    lineas.append(_linea_separadora('-'))

    # === DETALLE DE COMPRAS ===
    for c in reporte['compras']:
        izq = f'#{c["id_compra"]:<6} {c["hora"]}'
        der = f'${c["total"]:.2f}'
        lineas.append(_linea_dos_columnas(izq, der))

        # Segunda línea: usuario y proveedor
        info = f'  {c["usuario"]} | {c["proveedor"]}'
        if len(info) > ANCHO:
            info = info[:ANCHO]
        lineas.append(info)

    # === TOTAL DEL DÍA ===
    lineas.append(_linea_separadora('='))
    total_str = f'${reporte["total_dia"]:.2f}'
    lineas.append(_linea_dos_columnas('TOTAL DEL DIA', total_str))
    lineas.append(_linea_separadora('='))
    lineas.append('')

    return '\n'.join(lineas)
