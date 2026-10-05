import os
from dotenv import load_dotenv
from sqlalchemy import URL, make_url

# Las variables explícitas del deployment prevalecen sobre el archivo .env.
_public_demo_mode_entorno = os.getenv("PUBLIC_DEMO_MODE")
_cors_origins_entorno = os.getenv("CORS_ORIGINS")
_database_url_entorno = os.getenv("DATABASE_URL")
load_dotenv(override=True)


_database_url_configurada = _database_url_entorno or os.getenv("DATABASE_URL")
if _database_url_configurada:
    DATABASE_URL = make_url(_database_url_configurada)
else:
    DATABASE_URL = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USUARIO", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NOMBRE", "drugstore"),
    )


# Restricciones adicionales para la instancia pública del portfolio.
_modo_demo = (
    _public_demo_mode_entorno
    if _public_demo_mode_entorno is not None
    else os.getenv("PUBLIC_DEMO_MODE", "false")
).strip().lower()
if _modo_demo not in {"true", "false"}:
    raise ValueError("PUBLIC_DEMO_MODE debe ser true o false.")
PUBLIC_DEMO_MODE = _modo_demo == "true"

DEFAULT_CORS_ORIGINS = ("http://localhost:3000", "http://localhost:5165")


def obtener_cors_origins() -> list[str]:
    configurados = (
        _cors_origins_entorno
        if _cors_origins_entorno is not None
        else os.getenv("CORS_ORIGINS")
    )
    if configurados is None:
        return list(DEFAULT_CORS_ORIGINS)
    return [origin.strip() for origin in configurados.split(",") if origin.strip()]
