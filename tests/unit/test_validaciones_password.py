import pytest

from dominio.excepciones import ErrorDeValidacion
from dominio.validaciones import validar_password


@pytest.mark.parametrize("password", ["", "a", "12345"])
def test_validar_password_rechaza_menos_de_seis_caracteres(password):
    with pytest.raises(
        ErrorDeValidacion,
        match="La contraseña debe tener al menos 6 caracteres",
    ):
        validar_password(password)


@pytest.mark.parametrize("password", ["123456", "      "])
def test_validar_password_acepta_seis_caracteres_incluidos_espacios(password):
    validar_password(password)
