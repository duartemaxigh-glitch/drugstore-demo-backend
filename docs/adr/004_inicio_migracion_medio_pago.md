# Actualización 004 — Inicio de migración de MedioPago

**Fecha:** 2026-09-21  
**Estado:** en progreso

## Código auditado

Se revisaron:

- entidad de dominio `MedioPago`;
- interfaz `RepositorioMedioPago`;
- implementación `RepositorioMedioPagoMySQL`.

## Semántica actual

La entidad contiene:

- `id_medio_pago`;
- `nombre`;
- validación de nombre no vacío.

El repositorio MySQL implementa:

- creación física con `INSERT`;
- consulta por ID;
- listado ordenado por `id_medio_pago`;
- actualización de `nombre`;
- eliminación física con `DELETE`.

No existe baja lógica.

## Problemas heredados de la implementación MySQL

- cada método abre y cierra su propia conexión;
- la conexión utiliza el esquema transaccional anterior basado en autocommit;
- los duplicados se detectan inspeccionando el texto de la excepción;
- `actualizar()` devuelve siempre la entidad recibida aunque el registro pudiera haber desaparecido;
- `eliminar()` no informa si realmente existía la fila.

## Criterio de migración

Se mantendrá el mismo patrón ya aplicado a Categoría:

- entidad de dominio separada del modelo ORM;
- mapper en infraestructura;
- repository SQLAlchemy recibiendo una `Session`;
- `flush()` dentro del repository;
- `commit`/`rollback`/`close` a cargo de la UoW;
- traducción estructurada de violaciones `UNIQUE`;
- revisión de `actualizar()` y `eliminar()` para representar ausencia concurrente.

Antes de definir el modelo ORM se requiere verificar el esquema PostgreSQL real de `medios_pago` para no inventar longitudes, defaults o nombres de constraints.
