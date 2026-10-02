from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from dominio.excepciones import ErrorDeValidacion


CENTAVO = Decimal("0.01")
CERO_DINERO = Decimal("0.00")


def validar_finitud(valor: Decimal, nombre_campo: str) -> None:
    if not isinstance(valor, Decimal) or not valor.is_finite():
        raise ErrorDeValidacion(
            f"El campo '{nombre_campo}' debe ser un número decimal finito."
        )


def validar_no_negativo(valor: Decimal, nombre_campo: str) -> None:
    if valor < CERO_DINERO:
        raise ErrorDeValidacion(
            f"El campo '{nombre_campo}' no puede ser negativo."
        )


def normalizar_dinero(valor: Decimal, nombre_campo: str) -> Decimal:
    validar_finitud(valor, nombre_campo)
    validar_no_negativo(valor, nombre_campo)
    try:
        return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)
    except InvalidOperation as error:
        raise ErrorDeValidacion(
            f"El campo '{nombre_campo}' no es un importe válido."
        ) from error
