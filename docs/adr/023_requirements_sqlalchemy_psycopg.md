# Actualización 023 — Requirements para migración incremental

**Fecha:** 2026-09-23  
**Estado:** ajuste definido

## Versiones verificadas en el entorno

```text
psycopg==3.3.6
SQLAlchemy==2.0.54
```

## Requirements durante la migración

Mientras convivan repositorios PostgreSQL directos y repositorios SQLAlchemy, deben mantenerse ambos drivers:

```text
fastapi==0.115.6
uvicorn==0.34.0
psycopg2-binary==2.9.10
psycopg==3.3.6
SQLAlchemy==2.0.54
pyjwt==2.10.1
bcrypt==4.2.1
python-dotenv==1.0.1
```

`psycopg2-binary` se conserva temporalmente porque las entidades todavía no migradas continúan usando los repositorios PostgreSQL directos.

`psycopg` se requiere porque la configuración SQLAlchemy utiliza:

```text
postgresql+psycopg
```

## Alembic

Alembic sigue siendo parte del plan de migración, pero no se agrega aún con una versión inventada. Debe instalarse y luego fijarse la versión exacta utilizada por el proyecto.
