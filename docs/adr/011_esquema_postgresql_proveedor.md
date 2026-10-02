# Actualización 011 — Esquema PostgreSQL de Proveedor

**Fecha:** 2026-09-21  
**Estado:** verificado

## Esquema observado

| Columna | Tipo | Longitud | Nullable | Default |
|---|---|---:|---|---|
| `id_proveedor` | integer | — | NO | secuencia |
| `razon_social` | varchar | 120 | NO | — |
| `cuit_cuil` | varchar | 20 | SÍ | — |
| `contacto_nombre` | varchar | 100 | SÍ | — |
| `telefono` | varchar | 30 | SÍ | — |
| `email` | varchar | 100 | SÍ | — |
| `activo` | boolean | — | NO | `true` |

## Constraints observadas

```text
proveedores_id_proveedor_not_null
proveedores_razon_social_not_null
proveedores_activo_not_null
proveedores_pkey
proveedores_cuit_cuil_key
```

## Implicaciones para SQLAlchemy

- `id_proveedor` es una PK entera autogenerada.
- `razon_social` es obligatoria y tiene longitud máxima 120.
- `cuit_cuil`, `contacto_nombre`, `telefono` y `email` admiten `NULL`.
- `cuit_cuil` tiene restricción `UNIQUE`.
- `activo` es obligatorio y tiene `DEFAULT TRUE` en PostgreSQL.
- Para traducir duplicados debe utilizarse la constraint `proveedores_cuit_cuil_key`.
- La creación original MySQL no enviaba `activo`; para preservar esa semántica, el mapper de alta debe omitirlo y permitir que PostgreSQL aplique su default.
- Como `cuit_cuil` es nullable, PostgreSQL permite múltiples filas con `NULL`; la unicidad se aplica a los valores no nulos.
