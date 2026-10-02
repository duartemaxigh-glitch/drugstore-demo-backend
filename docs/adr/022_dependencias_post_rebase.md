# Actualización 022 — Dependencias después del rebase sobre PostgreSQL_version

**Fecha:** 2026-09-23  
**Estado:** ajuste requerido

## Hallazgo

Después de rebasar `rama-maxi` sobre `PostgreSQL_version`, `requirements.txt` contiene:

```text
fastapi==0.115.6
uvicorn==0.34.0
psycopg2-binary==2.9.10
pyjwt==2.10.1
bcrypt==4.2.1
python-dotenv==1.0.1
```

La rama base usa PostgreSQL mediante `psycopg2`, pero la migración SQLAlchemy de `rama-maxi` utiliza:

```text
SQLAlchemy 2.x
postgresql+psycopg
```

Por lo tanto, durante la migración incremental deben coexistir temporalmente:

- `psycopg2-binary`: para repositorios PostgreSQL directos todavía no migrados;
- `psycopg` (Psycopg 3): para SQLAlchemy configurado con `postgresql+psycopg`;
- `SQLAlchemy`: ORM y Session;
- `Alembic`: evolución futura del esquema.

## Próximo paso

Antes de editar `requirements.txt`, obtener las versiones instaladas en el entorno virtual:

```powershell
python -m pip freeze | Select-String -Pattern "SQLAlchemy|psycopg|alembic"
```

Luego fijar esas versiones en `requirements.txt` para que el proyecto pueda reproducirse en otro entorno.
