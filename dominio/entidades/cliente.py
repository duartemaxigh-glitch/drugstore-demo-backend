# ============================================================
# Entidad: Cliente
# ============================================================
# Representa una fila de la tabla 'clientes'.
# Todos los campos son opcionales excepto al menos uno
# que identifique al cliente.
# ============================================================

from __future__ import annotations

from dominio.validaciones import (
    validar_solo_letras,
    validar_solo_numeros,
)


class Cliente:
    def __init__(
        self,
        apellido: str | None = None,
        nombre: str | None = None,
        dni: str | None = None,
        cuit: str | None = None,
        telefono: str | None = None,
        id_cliente: int | None = None,
        activo: bool = True,
    ):
        self.id_cliente = id_cliente
        self.apellido = apellido
        self.nombre = nombre
        self.dni = dni
        self.cuit = cuit
        self.telefono = telefono
        self.activo = activo

    def validar(self):
        if self.apellido:
            validar_solo_letras(self.apellido, 'apellido')

        if self.nombre:
            validar_solo_letras(self.nombre, 'nombre')

        if self.dni:
            validar_solo_numeros(self.dni, 'dni')

        if self.cuit:
            validar_solo_numeros(self.cuit, 'cuit')

        if self.telefono:
            validar_solo_numeros(self.telefono, 'telefono')
