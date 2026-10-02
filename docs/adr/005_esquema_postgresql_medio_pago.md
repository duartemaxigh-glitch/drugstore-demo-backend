# Actualización 005 — Esquema PostgreSQL de MedioPago

**Fecha:** 2026-09-21  
**Estado:** verificado

## Esquema observado

La tabla `medios_pago` contiene:

| Columna | Tipo | Longitud | Nullable | Default |
|---|---|---:|---|---|
| `id_medio_pago` | integer | — | NO | `nextval('medios_pago_id_medio_pago_seq'::regclass)` |
| `nombre` | character varying | 50 | NO | — |

## Constraints observadas

- `medios_pago_id_medio_pago_not_null`
- `medios_pago_nombre_not_null`
- `medios_pago_pkey`
- `medios_pago_nombre_key`

## Implicaciones para SQLAlchemy

- `id_medio_pago` es PK entera autogenerada.
- `nombre` debe mapearse como `String(50)`, `nullable=False`.
- `nombre` tiene restricción UNIQUE.
- Para traducción de duplicados se utilizará `medios_pago_nombre_key`.
- No hace falta modelar manualmente la secuencia para el uso normal del ORM: una PK entera autoincremental permite a SQLAlchemy/PostgreSQL recuperar el ID generado.
