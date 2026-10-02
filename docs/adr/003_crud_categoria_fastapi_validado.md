# Actualización 003 — CRUD de Categoría validado vía FastAPI

**Estado:** completado  
**Fecha:** 2026-09-21

## Objetivo

Validar el repositorio SQLAlchemy de Categoría a través del flujo HTTP real, usando autenticación contra PostgreSQL y la Unidad de Trabajo configurada para la request.

## Casos verificados

Se validaron satisfactoriamente los siguientes casos:

- `POST /categorias` con datos válidos → `201 Created`.
- `POST /categorias` con nombre duplicado → `409 Conflict`.
- `GET /categorias` → listado correcto.
- `GET /categorias/{id}` → obtención correcta.
- actualización de categoría → persistencia correcta.
- actualización a nombre duplicado → conflicto correctamente traducido.
- eliminación de categoría → correcta.
- consulta posterior a la eliminación → comportamiento esperado de no encontrado.

## Flujo validado

```text
HTTP
↓
FastAPI
↓
Autenticación
↓
RepositorioUsuarioSQLAlchemy
↓
Caso de uso de Categoría
↓
RepositorioCategoriaSQLAlchemy
↓
Session SQLAlchemy compartida
↓
PostgreSQL
↓
UoW
↓
commit / rollback / close
```

## Manejo de duplicados

Una violación `UNIQUE` de PostgreSQL se traduce de la siguiente forma:

```text
PostgreSQL UniqueViolation
↓
SQLAlchemy IntegrityError
↓
RepositorioCategoriaSQLAlchemy
↓
EntidadDuplicada
↓
FastAPI
↓
409 Conflict
```

La prueba real de duplicado confirmó que la excepción sale del contexto de la UoW y activa el rollback correspondiente.

## Observación sobre OpenAPI

Swagger UI mostró el `409` como `Undocumented`.

Esto no representa un fallo funcional. Significa únicamente que la respuesta existe en ejecución pero todavía no fue declarada explícitamente en la metadata OpenAPI del endpoint.

La documentación detallada de respuestas HTTP se deja como mejora posterior para no mezclarla con la migración de persistencia.

## Conclusión

La migración de Categoría queda validada de extremo a extremo.

Ya no está probado únicamente el repository de forma aislada: quedó verificada la integración completa entre API, casos de uso, repositorios SQLAlchemy, PostgreSQL y Unidad de Trabajo.
