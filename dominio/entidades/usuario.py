# ============================================================
# Entidad: Usuario
# ============================================================
# Representa una fila de la tabla 'usuarios'.
# Un usuario puede ser 'jefe' o 'empleado'.
# ============================================================

from __future__ import annotations

from dominio.validaciones import (
    validar_email,
    validar_no_vacio,
    validar_solo_letras,
    validar_solo_numeros,
)


class Usuario:
    def __init__(
        self,
        apellido: str,
        nombre: str,
        dni: str,
        email: str,
        password_hash: str,
        rol: str = 'empleado',
        telefono: str | None = None,
        id_usuario: int | None = None,
        activo: bool = True,
    ):
        self.id_usuario = id_usuario
        self.apellido = apellido
        self.nombre = nombre
        self.dni = dni
        self.telefono = telefono
        self.email = email
        self.password_hash = password_hash
        self.rol = rol
        self.activo = activo

    def validar(self):
        validar_no_vacio(self.apellido, 'apellido')
        validar_solo_letras(self.apellido, 'apellido')

        validar_no_vacio(self.nombre, 'nombre')
        validar_solo_letras(self.nombre, 'nombre')

        validar_no_vacio(self.dni, 'dni')
        validar_solo_numeros(self.dni, 'dni')

        if self.telefono:
            validar_solo_numeros(self.telefono, 'telefono')

        validar_no_vacio(self.email, 'email')
        validar_email(self.email)

        validar_no_vacio(self.password_hash, 'password_hash')

        if self.rol not in ('jefe', 'empleado'):
            from dominio.excepciones import ErrorDeValidacion
            raise ErrorDeValidacion("El rol debe ser 'jefe' o 'empleado'.")
