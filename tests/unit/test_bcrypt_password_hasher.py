from infraestructura.seguridad.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)


def test_bcrypt_password_hasher_genera_y_verifica_hash_real():
    password_hasher = BcryptPasswordHasher()

    password_hash = password_hasher.generar_hash("secreto")

    assert isinstance(password_hash, str)
    assert password_hash != "secreto"
    assert password_hasher.verificar("secreto", password_hash) is True
    assert password_hasher.verificar("incorrecta", password_hash) is False
