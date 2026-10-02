from dominio.entidades.cliente import Cliente
from infraestructura.basedatos.modelos.cliente_modelo import ClienteModelo


def a_dominio(modelo: ClienteModelo) -> Cliente:
    return Cliente(
        id_cliente=modelo.id_cliente,
        apellido=modelo.apellido,
        nombre=modelo.nombre,
        dni=modelo.dni,
        cuit=modelo.cuit,
        telefono=modelo.telefono,
        activo=modelo.activo,
    )


def nuevo_modelo(cliente: Cliente) -> ClienteModelo:
    return ClienteModelo(
        apellido=cliente.apellido,
        nombre=cliente.nombre,
        dni=cliente.dni,
        cuit=cliente.cuit,
        telefono=cliente.telefono,
    )
