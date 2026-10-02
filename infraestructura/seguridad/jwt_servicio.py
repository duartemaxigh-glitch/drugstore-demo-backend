# ============================================================
# Servicio JWT (JSON Web Token)
# ============================================================
# JWT es un estándar para crear tokens de autenticación.
# Cuando un usuario hace login, le damos un token.
# Ese token viaja en cada petición para demostrar quién es.
#
# El token tiene 3 partes separadas por puntos:
#   HEADER.PAYLOAD.SIGNATURE
#
# - HEADER: dice qué algoritmo se usó (HS256)
# - PAYLOAD: los datos (id del usuario, rol, expiración)
# - SIGNATURE: firma digital para verificar que no fue alterado
# ============================================================

import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv(override=True)

SECRETO = os.getenv('JWT_SECRETO')
if not SECRETO:
    raise RuntimeError("JWT_SECRETO no está configurado. Verificá el archivo .env")
ALGORITMO = os.getenv('JWT_ALGORITMO', 'HS256')
EXPIRACION_MINUTOS = int(os.getenv('JWT_EXPIRACION_MINUTOS', '60'))


def crear_token(id_usuario: int, email: str, rol: str) -> str:
    """Genera un token JWT con los datos del usuario."""
    ahora = datetime.now(timezone.utc)
    expiracion = ahora + timedelta(minutes=EXPIRACION_MINUTOS)

    payload = {
        'id_usuario': id_usuario,
        'email': email,
        'rol': rol,
        'exp': expiracion,           # Cuándo expira el token
        'iat': ahora,                # Cuándo fue creado (issued at)
    }

    token = jwt.encode(payload, SECRETO, algorithm=ALGORITMO)
    return token


def verificar_token(token: str) -> dict:
    """
    Decodifica y verifica un token JWT.
    Si el token es inválido o expiró, lanza una excepción.
    Devuelve el payload (los datos del usuario).
    """
    payload = jwt.decode(token, SECRETO, algorithms=[ALGORITMO])
    return payload
