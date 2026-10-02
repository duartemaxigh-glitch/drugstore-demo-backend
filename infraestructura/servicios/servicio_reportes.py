# ============================================================
# Servicio de Reportes Diarios
# ============================================================
# Consulta la base de datos para armar reportes de ventas
# y compras filtrados por fecha.
#
# ¿Por qué está en Infraestructura y no como Caso de Uso?
# Porque los reportes son CONSULTAS de lectura que hacen
# JOINs específicos de SQL. No modifican datos ni aplican
# reglas de negocio. Son un detalle de infraestructura.
# ============================================================

from datetime import date

from sqlalchemy import case, func, literal, select
from sqlalchemy.orm import Session

from infraestructura.basedatos.modelos.cliente_modelo import ClienteModelo
from infraestructura.basedatos.modelos.compra_modelo import CompraModelo
from infraestructura.basedatos.modelos.medio_pago_modelo import MedioPagoModelo
from infraestructura.basedatos.modelos.proveedor_modelo import ProveedorModelo
from infraestructura.basedatos.modelos.usuario_modelo import UsuarioModelo
from infraestructura.basedatos.modelos.venta_modelo import VentaModelo


def obtener_reporte_ventas_por_dia(
    session: Session,
    fecha: date,
) -> dict:
    """
    Devuelve un dict con la estructura:
    {
        'fecha': '15/06/2025',
        'cantidad_ventas': 5,
        'total_dia': 12500.00,
        'ventas': [
            {
                'id_venta': 1,
                'hora': '14:30',
                'cajero': 'Juan Pérez',
                'cliente': 'María López' o None,
                'medio_pago': 'Efectivo',
                'total': 2500.00,
            },
            ...
        ]
    }
    """
    nombre_cliente = (
        func.coalesce(ClienteModelo.nombre, '')
        + literal(' ')
        + func.coalesce(ClienteModelo.apellido, '')
    )
    stmt = (
        select(
            VentaModelo.id_venta,
            VentaModelo.fecha,
            VentaModelo.total,
            (
                UsuarioModelo.nombre
                + literal(' ')
                + UsuarioModelo.apellido
            ).label('cajero'),
            case(
                (
                    ClienteModelo.id_cliente.is_not(None),
                    nombre_cliente,
                ),
                else_=None,
            ).label('cliente'),
            MedioPagoModelo.nombre.label('medio_pago'),
        )
        .join(
            UsuarioModelo,
            VentaModelo.id_usuario == UsuarioModelo.id_usuario,
        )
        .outerjoin(
            ClienteModelo,
            VentaModelo.id_cliente == ClienteModelo.id_cliente,
        )
        .join(
            MedioPagoModelo,
            VentaModelo.id_medio_pago == MedioPagoModelo.id_medio_pago,
        )
        .where(func.date(VentaModelo.fecha) == fecha)
        .order_by(VentaModelo.fecha.asc())
    )
    filas = session.execute(stmt).mappings().all()

    ventas = []
    total_dia = 0.0

    for f in filas:
        total_venta = float(f['total'])
        total_dia += total_venta

        cliente = f['cliente']
        if cliente:
            cliente = cliente.strip()
            if not cliente:
                cliente = None

        ventas.append({
            'id_venta': f['id_venta'],
            'hora': f['fecha'].strftime('%H:%M') if f['fecha'] else '',
            'cajero': f['cajero'],
            'cliente': cliente,
            'medio_pago': f['medio_pago'],
            'total': total_venta,
        })

    return {
        'fecha': fecha.strftime('%d/%m/%Y'),
        'cantidad_ventas': len(ventas),
        'total_dia': total_dia,
        'ventas': ventas,
    }


def obtener_reporte_compras_por_dia(
    session: Session,
    fecha: date,
) -> dict:
    """
    Devuelve un dict con la estructura:
    {
        'fecha': '15/06/2025',
        'cantidad_compras': 3,
        'total_dia': 8500.00,
        'compras': [
            {
                'id_compra': 1,
                'hora': '10:00',
                'usuario': 'Juan Pérez',
                'proveedor': 'Distribuidora Norte',
                'total': 3000.00,
            },
            ...
        ]
    }
    """
    stmt = (
        select(
            CompraModelo.id_compra,
            CompraModelo.fecha,
            CompraModelo.total,
            (
                UsuarioModelo.nombre
                + literal(' ')
                + UsuarioModelo.apellido
            ).label('usuario'),
            ProveedorModelo.razon_social.label('proveedor'),
        )
        .join(
            UsuarioModelo,
            CompraModelo.id_usuario == UsuarioModelo.id_usuario,
        )
        .join(
            ProveedorModelo,
            CompraModelo.id_proveedor == ProveedorModelo.id_proveedor,
        )
        .where(func.date(CompraModelo.fecha) == fecha)
        .order_by(CompraModelo.fecha.asc())
    )
    filas = session.execute(stmt).mappings().all()

    compras = []
    total_dia = 0.0

    for f in filas:
        total_compra = float(f['total'])
        total_dia += total_compra

        compras.append({
            'id_compra': f['id_compra'],
            'hora': f['fecha'].strftime('%H:%M') if f['fecha'] else '',
            'usuario': f['usuario'],
            'proveedor': f['proveedor'],
            'total': total_compra,
        })

    return {
        'fecha': fecha.strftime('%d/%m/%Y'),
        'cantidad_compras': len(compras),
        'total_dia': total_dia,
        'compras': compras,
    }
