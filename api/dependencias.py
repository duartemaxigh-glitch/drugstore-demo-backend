# ============================================================
# Dependencias de la API
# ============================================================

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from aplicacion.puertos.password_hasher import PasswordHasher

# ============================================================
# Base de datos / Unidades de Trabajo
# ============================================================

from infraestructura.basedatos.sesion import SessionLocal
from infraestructura.basedatos.unidad_trabajo import (
    UnidadDeTrabajoSQLAlchemy,
)

# ============================================================
# Repositorios SQLAlchemy ya migrados
# ============================================================

from infraestructura.repositorios.repositorio_categoria_sqlalchemy import (
    RepositorioCategoriaSQLAlchemy,
)
from infraestructura.repositorios.repositorio_cliente_sqlalchemy import (
    RepositorioClienteSQLAlchemy,
)
from infraestructura.repositorios.repositorio_compra_sqlalchemy import (
    RepositorioCompraSQLAlchemy,
)
from infraestructura.repositorios.repositorio_medio_pago_sqlalchemy import (
    RepositorioMedioPagoSQLAlchemy,
)
from infraestructura.repositorios.repositorio_proveedor_sqlalchemy import (
    RepositorioProveedorSQLAlchemy,
)
from infraestructura.repositorios.repositorio_producto_sqlalchemy import (
    RepositorioProductoSQLAlchemy,
)
from infraestructura.repositorios.repositorio_usuario_sqlalchemy import (
    RepositorioUsuarioSQLAlchemy,
)
from infraestructura.repositorios.repositorio_venta_sqlalchemy import (
    RepositorioVentaSQLAlchemy,
)
from infraestructura.seguridad.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)

# ============================================================
from infraestructura.seguridad.jwt_servicio import verificar_token


_password_hasher = BcryptPasswordHasher()


# ============================================================
# Unidad de Trabajo SQLAlchemy
# ============================================================

def obtener_uow():
    with UnidadDeTrabajoSQLAlchemy(SessionLocal) as uow:
        yield uow


def obtener_session(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
) -> Session:
    return uow.session


def obtener_password_hasher() -> PasswordHasher:
    return _password_hasher


# ============================================================
# Repositorios SQLAlchemy
# ============================================================

def obtener_repo_categoria(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
):
    return RepositorioCategoriaSQLAlchemy(uow.session)


def obtener_repo_usuario(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
):
    return RepositorioUsuarioSQLAlchemy(uow.session)


def obtener_repo_proveedor(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
):
    return RepositorioProveedorSQLAlchemy(uow.session)


def obtener_repo_medio_pago(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
):
    return RepositorioMedioPagoSQLAlchemy(uow.session)


def obtener_repo_cliente(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
):
    return RepositorioClienteSQLAlchemy(uow.session)


def obtener_repo_producto(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
):
    return RepositorioProductoSQLAlchemy(uow.session)


def obtener_repo_venta(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
):
    return RepositorioVentaSQLAlchemy(uow.session)


def obtener_repo_compra(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
):
    return RepositorioCompraSQLAlchemy(uow.session)


# ============================================================
# Autenticación JWT
# ============================================================

esquema_seguridad = HTTPBearer()


def obtener_usuario_actual(
    credenciales: Annotated[
        HTTPAuthorizationCredentials,
        Depends(esquema_seguridad),
    ],
) -> dict:
    try:
        payload = verificar_token(credenciales.credentials)
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado.",
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        )


def requiere_rol_jefe(
    usuario: Annotated[
        dict,
        Depends(obtener_usuario_actual),
    ],
) -> dict:
    if usuario.get("rol") != "jefe":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se necesita rol de jefe para esta operación.",
        )

    return usuario
