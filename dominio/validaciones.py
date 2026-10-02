# ============================================================
# Validaciones del Dominio
# ============================================================
# Estas funciones verifican que los datos cumplan las reglas
# del negocio ANTES de guardarlos en la base de datos.
#
# Reglas:
#   - Nombres y apellidos: solo letras y espacios
#   - DNI, teléfono, CUIT: solo números
#   - Email: debe contener @
#   - Precios: solo números y punto decimal
#   - Cantidades: solo números enteros positivos
# ============================================================

import re
from decimal import Decimal

from dominio.dinero import validar_finitud, validar_no_negativo
from dominio.excepciones import ErrorDeValidacion


def validar_solo_letras(valor: str, nombre_campo: str):
    """Valida que el valor contenga solo letras y espacios."""
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$', valor):
        raise ErrorDeValidacion(
            f"El campo '{nombre_campo}' solo puede contener letras y espacios."
        )


def validar_solo_numeros(valor: str, nombre_campo: str):
    """Valida que el valor contenga solo dígitos (0-9)."""
    if not re.match(r'^\d+$', valor):
        raise ErrorDeValidacion(
            f"El campo '{nombre_campo}' solo puede contener números."
        )


def validar_email(valor: str):
    """Valida que el email contenga @."""
    if '@' not in valor:
        raise ErrorDeValidacion("El email debe contener '@'.")


def validar_password(password: str) -> None:
    """Valida la longitud mínima de una contraseña."""
    if len(password) < 6:
        raise ErrorDeValidacion(
            "La contraseña debe tener al menos 6 caracteres."
        )


def validar_precio(valor: Decimal, nombre_campo: str):
    """Valida que el precio sea decimal, finito y no negativo."""
    validar_finitud(valor, nombre_campo)
    validar_no_negativo(valor, nombre_campo)


def validar_cantidad(valor, nombre_campo: str):
    """Valida que la cantidad sea un número entero positivo."""
    if not isinstance(valor, int):
        raise ErrorDeValidacion(
            f"El campo '{nombre_campo}' debe ser un número entero."
        )
    if valor < 0:
        raise ErrorDeValidacion(
            f"El campo '{nombre_campo}' no puede ser negativo."
        )


def validar_no_vacio(valor: str, nombre_campo: str):
    """Valida que el valor no esté vacío."""
    if valor is None or str(valor).strip() == '':
        raise ErrorDeValidacion(
            f"El campo '{nombre_campo}' es obligatorio."
        )
