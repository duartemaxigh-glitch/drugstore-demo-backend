# Actualización 009 — CRUD de MedioPago validado vía FastAPI

**Fecha:** 2026-09-21  
**Estado:** completado

## Objetivo

Validar de extremo a extremo la migración de `MedioPago` usando FastAPI, autenticación, casos de uso, repositorio SQLAlchemy, PostgreSQL y Unidad de Trabajo.

## Componentes involucrados

```text
HTTP
↓
FastAPI
↓
Autenticación
↓
Caso de uso de MedioPago
↓
RepositorioMedioPagoSQLAlchemy
↓
Session SQLAlchemy
↓
PostgreSQL
↓
Unidad de Trabajo
↓
commit / rollback / close
```

## Casos validados

Se probaron satisfactoriamente mediante FastAPI:

- creación de medio de pago;
- rechazo de nombre duplicado;
- listado completo;
- obtención por ID;
- actualización de registro existente;
- actualización de ID inexistente;
- actualización a nombre duplicado;
- eliminación;
- eliminación/consulta posterior de un registro inexistente.

## Manejo de duplicados

La restricción PostgreSQL utilizada para distinguir duplicados es:

```text
medios_pago_nombre_key
```

El flujo de error queda:

```text
PostgreSQL UniqueViolation
↓
SQLAlchemy IntegrityError
↓
RepositorioMedioPagoSQLAlchemy
↓
EntidadDuplicada
↓
FastAPI
↓
409 Conflict
```

## Ausencia de registros

El repositorio utiliza:

```python
actualizar(...) -> MedioPago | None
eliminar(...) -> bool
```

Los casos de uso convierten esos resultados en `EntidadNoEncontrada`, y la capa HTTP los traduce a `404 Not Found`.

## Política transaccional

El repository no ejecuta:

```text
commit
rollback
close
```

Estas responsabilidades continúan centralizadas en la Unidad de Trabajo.

El repository sí usa `flush()` para materializar operaciones dentro de la transacción y detectar errores de persistencia antes del commit.

## Resultado

La migración de `MedioPago` queda completada y validada de extremo a extremo.

`MedioPago` se considera cerrado dentro de esta etapa de migración.
