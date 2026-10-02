# ============================================================
# Esquemas (Schemas) de la API
# ============================================================
# Los esquemas son clases de Pydantic que definen la FORMA
# del JSON que llega (Request) y el que sale (Response).
#
# FastAPI usa estos esquemas para:
#   1. Validar automáticamente los datos que llegan
#   2. Generar documentación automática (Swagger)
#   3. Serializar las respuestas a JSON
#
# No son entidades del dominio. Son "traductores" entre
# el mundo HTTP (JSON) y nuestras entidades de negocio.
# ============================================================

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

# ======================== AUTH ========================

class LoginEsquema(BaseModel):
    email: str
    password: str


class TokenEsquema(BaseModel):
    token: str
    rol: str


class RecuperarPasswordEsquema(BaseModel):
    dni: str
    email: str
    nueva_password: str
    repetir_password: str


# ======================== CATEGORIAS ========================

class CategoriaCrear(BaseModel):
    nombre: str


class CategoriaRespuesta(BaseModel):
    id_categoria: int
    nombre: str


# ======================== USUARIOS ========================

class UsuarioCrear(BaseModel):
    apellido: str
    nombre: str
    dni: str
    email: str
    password: str
    rol: str = 'empleado'
    telefono: str | None = None


class UsuarioActualizar(BaseModel):
    apellido: str
    nombre: str
    dni: str
    email: str
    rol: str = 'empleado'
    telefono: str | None = None


class UsuarioRespuesta(BaseModel):
    id_usuario: int
    apellido: str
    nombre: str
    dni: str
    email: str
    rol: str
    telefono: str | None = None
    activo: bool


# ======================== CLIENTES ========================

class ClienteCrear(BaseModel):
    apellido: str | None = None
    nombre: str | None = None
    dni: str | None = None
    cuit: str | None = None
    telefono: str | None = None


class ClienteRespuesta(BaseModel):
    id_cliente: int
    apellido: str | None = None
    nombre: str | None = None
    dni: str | None = None
    cuit: str | None = None
    telefono: str | None = None
    activo: bool


# ======================== PROVEEDORES ========================

class ProveedorCrear(BaseModel):
    razon_social: str
    cuit_cuil: str | None = None
    contacto_nombre: str | None = None
    telefono: str | None = None
    email: str | None = None

class ProveedorReemplazar(BaseModel):
    razon_social: str
    cuit_cuil: str | None
    contacto_nombre: str | None
    telefono: str | None
    email: str | None

class ProveedorActualizarParcial(BaseModel):
    razon_social: str | None = None
    cuit_cuil: str | None = None
    contacto_nombre: str | None = None
    telefono: str | None = None
    email: str | None = None

class ProveedorRespuesta(BaseModel):
    id_proveedor: int
    razon_social: str
    cuit_cuil: str | None = None
    contacto_nombre: str | None = None
    telefono: str | None = None
    email: str | None = None
    activo: bool


# ======================== MEDIOS DE PAGO ========================

class MedioPagoCrear(BaseModel):
    nombre: str


class MedioPagoRespuesta(BaseModel):
    id_medio_pago: int
    nombre: str


# ======================== PRODUCTOS ========================

class ProductoCrear(BaseModel):
    nombre: str
    precio_venta: Decimal
    precio_compra: Decimal
    stock: int = 0
    codigo_barras: str | None = None
    id_categoria: int | None = None


class ProductoActualizar(BaseModel):
    nombre: str
    precio_venta: Decimal
    precio_compra: Decimal
    codigo_barras: str | None = None
    id_categoria: int | None = None


class ProductoRespuesta(BaseModel):
    id_producto: int
    nombre: str
    precio_venta: float
    precio_compra: float
    stock: int
    codigo_barras: str | None = None
    id_categoria: int | None = None


# ======================== VENTAS ========================

class VentaDetalleCrear(BaseModel):
    id_producto: int
    cantidad: int


class VentaCrear(BaseModel):
    id_medio_pago: int
    id_cliente: int | None = None
    detalles: list[VentaDetalleCrear]


class VentaDetalleRespuesta(BaseModel):
    id_detalle: int | None = None
    id_producto: int
    cantidad: int
    precio_unitario: float
    subtotal: float


class VentaRespuesta(BaseModel):
    id_venta: int
    fecha: datetime | None = None
    id_usuario: int
    id_cliente: int | None = None
    id_medio_pago: int
    total: float
    detalles: list[VentaDetalleRespuesta]


# ======================== COMPRAS ========================

class CompraDetalleCrear(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: Decimal


class CompraCrear(BaseModel):
    id_proveedor: int
    detalles: list[CompraDetalleCrear]


class CompraDetalleRespuesta(BaseModel):
    id_detalle: int | None = None
    id_producto: int
    cantidad: int
    precio_unitario: float
    subtotal: float


class CompraRespuesta(BaseModel):
    id_compra: int
    fecha: datetime | None = None
    id_proveedor: int
    id_usuario: int
    total: float
    detalles: list[CompraDetalleRespuesta]


# ======================== REPORTES DIARIOS ========================

class ReporteVentaItem(BaseModel):
    """Una venta individual dentro del reporte diario."""
    id_venta: int
    hora: str
    cajero: str
    cliente: str | None = None
    medio_pago: str
    total: float


class ReporteVentasDia(BaseModel):
    """Reporte de todas las ventas de un día."""
    fecha: str
    cantidad_ventas: int
    total_dia: float
    ventas: list[ReporteVentaItem]


class ReporteCompraItem(BaseModel):
    """Una compra individual dentro del reporte diario."""
    id_compra: int
    hora: str
    usuario: str
    proveedor: str
    total: float


class ReporteComprasDia(BaseModel):
    """Reporte de todas las compras de un día."""
    fecha: str
    cantidad_compras: int
    total_dia: float
    compras: list[ReporteCompraItem]
