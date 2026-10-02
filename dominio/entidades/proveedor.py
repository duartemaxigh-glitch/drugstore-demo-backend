# ============================================================
# Entidad: Proveedor
# ============================================================
# Representa una fila de la tabla 'proveedores'.
# ============================================================

from __future__ import annotations

from dominio.validaciones import (
    validar_email,
    validar_no_vacio,
    validar_solo_letras,
    validar_solo_numeros,
)


class Proveedor:
    def __init__(
        self,
        razon_social: str,
        cuit_cuil: str | None = None,
        contacto_nombre: str | None = None,
        telefono: str | None = None,
        email: str | None = None,
        id_proveedor: int | None = None,
        activo: bool = True,
    ):
        self.id_proveedor = id_proveedor
        self.razon_social = razon_social
        self.cuit_cuil = cuit_cuil
        self.contacto_nombre = contacto_nombre
        self.telefono = telefono
        self.email = email
        self.activo = activo

    def validar(self):
        validar_no_vacio(self.razon_social, 'razon_social')

        if self.cuit_cuil:
            validar_solo_numeros(self.cuit_cuil, 'cuit_cuil')

        if self.contacto_nombre:
            validar_solo_letras(self.contacto_nombre, 'contacto_nombre')

        if self.telefono:
            validar_solo_numeros(self.telefono, 'telefono')

        if self.email:
            validar_email(self.email)
