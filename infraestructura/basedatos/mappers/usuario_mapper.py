from dominio.entidades.usuario import Usuario
from infraestructura.basedatos.modelos.usuario_modelo import UsuarioModelo


def a_dominio(modelo: UsuarioModelo) -> Usuario:
    return Usuario(
        id_usuario=modelo.id_usuario,
        apellido=modelo.apellido,
        nombre=modelo.nombre,
        dni=modelo.dni,
        email=modelo.email,
        password_hash=modelo.password_hash,
        rol=modelo.rol,
        telefono=modelo.telefono,
        activo=modelo.activo
    )

def nuevo_modelo(usuario: Usuario) -> UsuarioModelo:
    return UsuarioModelo(
        apellido=usuario.apellido,
        nombre=usuario.nombre,
        dni=usuario.dni,
        telefono=usuario.telefono,
        email=usuario.email,
        password_hash=usuario.password_hash,
        rol=usuario.rol,
        activo=usuario.activo,
    )