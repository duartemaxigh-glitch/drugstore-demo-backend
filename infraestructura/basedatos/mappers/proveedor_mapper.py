from dominio.entidades.proveedor import Proveedor
from infraestructura.basedatos.modelos.proveedor_modelo import ProveedorModelo


def a_dominio(modelo: ProveedorModelo) -> Proveedor:
    return Proveedor(
        id_proveedor=modelo.id_proveedor,
        razon_social=modelo.razon_social,
        cuit_cuil=modelo.cuit_cuil,
        contacto_nombre=modelo.contacto_nombre,
        telefono=modelo.telefono,
        email=modelo.email,
        activo=modelo.activo,
    )

def nuevo_modelo(proveedor: Proveedor) -> ProveedorModelo:
    return ProveedorModelo(
        razon_social=proveedor.razon_social,
        cuit_cuil=proveedor.cuit_cuil,
        contacto_nombre=proveedor.contacto_nombre,
        telefono=proveedor.telefono,
        email=proveedor.email,
    )