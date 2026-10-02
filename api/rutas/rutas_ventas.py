# ============================================================
# Rutas: Ventas (Crear, Listar, Obtener, Eliminar)
# ============================================================
# El id_usuario se toma del token JWT (quien esté logueado
# es quien registra la venta).
#
# Crear y Eliminar usan Unidad de Trabajo para garantizar
# atomicidad (stock + venta en una sola transacción).
# ============================================================

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse

from api.dependencias import (
    obtener_repo_cliente,
    obtener_repo_medio_pago,
    obtener_repo_producto,
    obtener_repo_usuario,
    obtener_repo_venta,
    obtener_usuario_actual,
)
from api.esquemas import VentaCrear, VentaDetalleRespuesta, VentaRespuesta
from aplicacion.casos_de_uso.ventas.crear_venta import CrearVenta
from aplicacion.casos_de_uso.ventas.eliminar_venta import EliminarVenta
from aplicacion.casos_de_uso.ventas.listar_ventas import ListarVentas
from aplicacion.casos_de_uso.ventas.obtener_venta import ObtenerVenta
from dominio.excepciones import EntidadNoEncontrada, ErrorDeValidacion
from dominio.repositorios.repositorio_cliente import RepositorioCliente
from dominio.repositorios.repositorio_medio_pago import RepositorioMedioPago
from dominio.repositorios.repositorio_producto import RepositorioProducto
from dominio.repositorios.repositorio_usuario import RepositorioUsuario
from dominio.repositorios.repositorio_venta import RepositorioVenta
from infraestructura.servicios.generador_ticket import generar_ticket

router = APIRouter(prefix="/ventas", tags=["Ventas"])


def _a_respuesta(v) -> VentaRespuesta:
    return VentaRespuesta(
        id_venta=v.id_venta,
        fecha=v.fecha,
        id_usuario=v.id_usuario,
        id_cliente=v.id_cliente,
        id_medio_pago=v.id_medio_pago,
        total=v.total,
        detalles=[
            VentaDetalleRespuesta(
                id_detalle=d.id_detalle,
                id_producto=d.id_producto,
                cantidad=d.cantidad,
                precio_unitario=d.precio_unitario,
                subtotal=d.subtotal,
            )
            for d in v.detalles
        ],
    )


DepRepoVenta = Annotated[RepositorioVenta, Depends(obtener_repo_venta)]
DepRepoProducto = Annotated[RepositorioProducto, Depends(obtener_repo_producto)]
DepRepoCliente = Annotated[RepositorioCliente, Depends(obtener_repo_cliente)]
DepRepoUsuario = Annotated[RepositorioUsuario, Depends(obtener_repo_usuario)]
DepRepoMedioPago = Annotated[RepositorioMedioPago, Depends(obtener_repo_medio_pago)]
DepUsuario = Annotated[dict, Depends(obtener_usuario_actual)]


@router.post("/", response_model=VentaRespuesta, status_code=status.HTTP_201_CREATED)
def crear(
    datos: VentaCrear,
    repo_venta: DepRepoVenta,
    repo_producto: DepRepoProducto,
    usuario: DepUsuario,
):
    try:
        caso_de_uso = CrearVenta(repo_venta, repo_producto)

        # Convertimos los detalles de Pydantic a diccionarios
        detalles = [
            {'id_producto': d.id_producto, 'cantidad': d.cantidad}
            for d in datos.detalles
        ]

        venta = caso_de_uso.ejecutar(
            id_usuario=usuario['id_usuario'],  # Del token JWT
            id_medio_pago=datos.id_medio_pago,
            detalles=detalles,
            id_cliente=datos.id_cliente,
        )
        return _a_respuesta(venta)
    except ErrorDeValidacion as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=list[VentaRespuesta])
def listar(repo: DepRepoVenta, usuario: DepUsuario):
    caso_de_uso = ListarVentas(repo)
    ventas = caso_de_uso.ejecutar()
    return [_a_respuesta(v) for v in ventas]


@router.get("/{id_venta}", response_model=VentaRespuesta)
def obtener(id_venta: int, repo: DepRepoVenta, usuario: DepUsuario):
    try:
        caso_de_uso = ObtenerVenta(repo)
        venta = caso_de_uso.ejecutar(id_venta)
        return _a_respuesta(venta)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id_venta}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    id_venta: int,
    repo_venta: DepRepoVenta,
    repo_producto: DepRepoProducto,
    usuario: DepUsuario,
):
    try:
        caso_de_uso = EliminarVenta(repo_venta, repo_producto)
        caso_de_uso.ejecutar(id_venta)
    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================
# Ticket para impresora térmica de 80mm
# ============================================================
# Devuelve texto plano formateado a 48 caracteres de ancho.
# El frontend puede enviar este texto directo a la impresora.
# ============================================================

@router.get("/{id_venta}/ticket", response_class=PlainTextResponse)
def obtener_ticket(
    id_venta: int,
    repo_venta: DepRepoVenta,
    repo_producto: DepRepoProducto,
    repo_cliente: DepRepoCliente,
    repo_usuario: DepRepoUsuario,
    repo_medio_pago: DepRepoMedioPago,
    usuario: DepUsuario,
):
    try:
        # 1. Obtenemos la venta con sus detalles
        caso_de_uso = ObtenerVenta(repo_venta)
        venta = caso_de_uso.ejecutar(id_venta)

        # 2. Buscamos el nombre de cada producto
        detalles_ticket = []
        for d in venta.detalles:
            producto = repo_producto.obtener_por_id(d.id_producto)
            detalles_ticket.append({
                'producto_nombre': producto.nombre if producto else f'Producto #{d.id_producto}',
                'cantidad': d.cantidad,
                'precio_unitario': d.precio_unitario,
                'subtotal': d.subtotal,
            })

        # 3. Nombre del cajero (usuario que hizo la venta)
        cajero = repo_usuario.obtener_por_id(venta.id_usuario)
        usuario_nombre = f'{cajero.nombre} {cajero.apellido}' if cajero else 'Desconocido'

        # 4. Nombre del cliente (si tiene)
        cliente_nombre = None
        if venta.id_cliente:
            cliente = repo_cliente.obtener_por_id(venta.id_cliente)
            if cliente:
                partes = [p for p in [cliente.nombre, cliente.apellido] if p]
                cliente_nombre = ' '.join(partes) if partes else None

        # 5. Medio de pago
        medio = repo_medio_pago.obtener_por_id(venta.id_medio_pago)
        medio_pago_nombre = medio.nombre if medio else 'N/A'

        # 6. Generamos el ticket
        # La venta de la BD siempre tiene id_venta y fecha
        assert venta.id_venta is not None
        assert venta.fecha is not None
        texto = generar_ticket(
            id_venta=venta.id_venta,
            fecha=venta.fecha,
            usuario_nombre=usuario_nombre,
            cliente_nombre=cliente_nombre,
            medio_pago_nombre=medio_pago_nombre,
            detalles=detalles_ticket,
            total=venta.total,
        )

        return PlainTextResponse(content=texto)

    except EntidadNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e))
