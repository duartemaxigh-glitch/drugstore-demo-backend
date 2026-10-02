from datetime import datetime
from decimal import Decimal

from infraestructura.servicios.generador_ticket import (
    generar_ticket,
    generar_ticket_reporte_compras,
    generar_ticket_reporte_ventas,
)


def test_ticket_venta_preserva_formato_exacto_y_salto_final():
    ticket = generar_ticket(
        id_venta=1,
        fecha=datetime(2025, 6, 15, 14, 30),
        usuario_nombre="Ana Perez",
        cliente_nombre="Maria Lopez",
        medio_pago_nombre="Efectivo",
        detalles=[
            {
                "producto_nombre": "Agua",
                "cantidad": 2,
                "precio_unitario": Decimal("1.20"),
                "subtotal": Decimal("2.40"),
            }
        ],
        total=Decimal("2.40"),
    )

    esperado = "\n".join(
        [
            "",
            "                   DRUGSTORE                    ",
            "================================================",
            "Venta #: 1",
            "Fecha: 15/06/2025 14:30",
            "Cajero: Ana Perez",
            "Cliente: Maria Lopez",
            "Pago: Efectivo",
            "------------------------------------------------",
            "PRODUCTO                                SUBTOTAL",
            "------------------------------------------------",
            "Agua                                       $2.40",
            "  2 x $1.20",
            "================================================",
            "TOTAL                                      $2.40",
            "================================================",
            "",
            "             Gracias por su compra!             ",
            "",
        ]
    )
    assert ticket == esperado
    assert ticket.endswith("\n")


def test_ticket_reporte_ventas_preserva_formato_exacto_y_salto_final():
    ticket = generar_ticket_reporte_ventas(
        {
            "fecha": "15/06/2025",
            "cantidad_ventas": 1,
            "total_dia": 2.4,
            "ventas": [
                {
                    "id_venta": 1,
                    "hora": "14:30",
                    "cajero": "Ana Perez",
                    "cliente": None,
                    "medio_pago": "Efectivo",
                    "total": 2.4,
                }
            ],
        }
    )

    esperado = "\n".join(
        [
            "",
            "                   DRUGSTORE                    ",
            "               REPORTE DE VENTAS                ",
            "================================================",
            "Fecha: 15/06/2025",
            "Cantidad de ventas: 1",
            "------------------------------------------------",
            "#VENTA  HORA                               TOTAL",
            "------------------------------------------------",
            "#1      14:30                              $2.40",
            "  Ana Perez | Efectivo",
            "================================================",
            "TOTAL DEL DIA                              $2.40",
            "================================================",
            "",
        ]
    )
    assert ticket == esperado
    assert ticket.endswith("\n")


def test_ticket_reporte_compras_preserva_formato_exacto_y_salto_final():
    ticket = generar_ticket_reporte_compras(
        {
            "fecha": "15/06/2025",
            "cantidad_compras": 1,
            "total_dia": 3.5,
            "compras": [
                {
                    "id_compra": 2,
                    "hora": "10:00",
                    "usuario": "Ana Perez",
                    "proveedor": "Proveedor SA",
                    "total": 3.5,
                }
            ],
        }
    )

    esperado = "\n".join(
        [
            "",
            "                   DRUGSTORE                    ",
            "               REPORTE DE COMPRAS               ",
            "================================================",
            "Fecha: 15/06/2025",
            "Cantidad de compras: 1",
            "------------------------------------------------",
            "#COMPRA HORA                               TOTAL",
            "------------------------------------------------",
            "#2      10:00                              $3.50",
            "  Ana Perez | Proveedor SA",
            "================================================",
            "TOTAL DEL DIA                              $3.50",
            "================================================",
            "",
        ]
    )
    assert ticket == esperado
    assert ticket.endswith("\n")
