# Actualización 014 — CRUD de Proveedor validado contra PostgreSQL

**Fecha:** 2026-09-21  
**Estado:** completado a nivel repository

## Objetivo

Validar la migración de `Proveedor` desde PyMySQL/MySQL hacia SQLAlchemy 2.x/PostgreSQL conservando la semántica original, incluida la baja lógica.

## Semántica preservada

### Lecturas

Las operaciones ordinarias ocultan proveedores inactivos:

```text
obtener_por_id() → id + activo = TRUE
obtener_todos()  → activo = TRUE + orden por id
```

### Actualización

`actualizar()` busca por `id_proveedor` sin filtrar `activo`, igual que el SQL MySQL original.

Actualiza únicamente:

```text
razon_social
cuit_cuil
contacto_nombre
telefono
email
```

No modifica `activo`.

### Eliminación

`eliminar()` implementa baja lógica:

```text
activo = FALSE
```

No ejecuta `DELETE` físico.

Busca por PK sin filtrar `activo`, igual que la implementación MySQL original.

Por esta razón, una segunda llamada a `eliminar()` sobre el mismo proveedor puede volver a devolver `True`, ya que la fila continúa existiendo físicamente.

## Default de activo

La creación no envía explícitamente `activo`.

PostgreSQL aplica:

```sql
DEFAULT TRUE
```

y después del `flush()` SQLAlchemy recupera correctamente el valor generado por el servidor.

La prueba confirmó:

```text
Proveedor.activo == True
```

después del alta.

## Restricción UNIQUE

La constraint real utilizada para CUIT/CUIL es:

```text
proveedores_cuit_cuil_key
```

La traducción de errores se realiza mediante:

```python
e.orig.diag.constraint_name
```

y no inspeccionando texto de excepciones.

## NULL + UNIQUE

`cuit_cuil` es nullable y unique.

Se verificó que:

```python
cuit_cuil=None
```

es aceptado correctamente por PostgreSQL.

Esto permite múltiples proveedores sin CUIT/CUIL cargado, mientras que los valores no nulos continúan sujetos a unicidad.

## Pruebas realizadas

Se validaron satisfactoriamente:

1. creación normal;
2. aplicación de `DEFAULT TRUE` para `activo`;
3. CUIT/CUIL duplicado → `EntidadDuplicada`;
4. creación con `cuit_cuil=None`;
5. obtención por ID;
6. listado de activos;
7. actualización válida;
8. actualización de ID inexistente → `None`;
9. actualización a CUIT/CUIL duplicado → `EntidadDuplicada`;
10. baja lógica de proveedor existente → `True`;
11. proveedor dado de baja deja de aparecer en `obtener_por_id()`;
12. proveedor dado de baja deja de aparecer en `obtener_todos()`;
13. segunda baja lógica sobre la misma fila → comportamiento coherente con el MySQL original.

## Resultado

`RepositorioProveedorSQLAlchemy` queda validado directamente contra PostgreSQL.

Queda pendiente la integración HTTP mediante FastAPI para comprobar el flujo completo:

```text
HTTP
↓
FastAPI
↓
Caso de uso
↓
RepositorioProveedorSQLAlchemy
↓
Session SQLAlchemy
↓
PostgreSQL
↓
Unidad de Trabajo
```
