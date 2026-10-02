# Actualización 020 — Proveedor validado de extremo a extremo

**Fecha:** 2026-09-22  
**Estado:** completado

## Objetivo

Cerrar la migración de `Proveedor` validando no sólo el repository SQLAlchemy contra PostgreSQL, sino también su comportamiento completo a través de FastAPI.

## Flujo validado

```text
HTTP
↓
FastAPI
↓
Autenticación
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
↓
commit / rollback / close
```

## Semántica de lectura y baja lógica

Se mantiene la semántica original:

```text
obtener_por_id() → sólo activo = TRUE
obtener_todos()  → sólo activos
eliminar()       → baja lógica con activo = FALSE
```

Un proveedor inactivo deja de estar disponible para las operaciones ordinarias de lectura.

## PUT y PATCH

Durante la migración se detectó que el endpoint de actualización original no distinguía entre:

- reemplazo completo;
- actualización parcial.

Se decidió separar ambas operaciones.

### PUT

```http
PUT /proveedores/{id_proveedor}
```

Usa `ProveedorReemplazar`.

Todos los campos editables deben estar presentes, aunque los nullable pueden enviarse como `null`.

Semántica:

```text
PUT
→ reemplazo completo del estado editable
```

Se verificó que un payload incompleto produce `422`.

### PATCH

```http
PATCH /proveedores/{id_proveedor}
```

Usa `ProveedorActualizarParcial`.

La capa HTTP obtiene sólo los campos realmente enviados:

```python
cambios = datos.model_dump(exclude_unset=True)
```

El caso de uso aplica únicamente esas claves sobre la entidad existente.

Semántica:

```text
PATCH
→ modifica sólo los campos enviados
```

Esto permite distinguir correctamente:

```json
{}
```

de:

```json
{"telefono": null}
```

En el segundo caso se elimina explícitamente el teléfono.

## Validación del estado final

Después de aplicar cambios parciales se ejecuta:

```python
existente.validar()
```

De esta forma, el dominio valida el estado final completo y no sólo los campos recibidos.

Se verificó que:

```json
{"razon_social": null}
```

es rechazado por la validación de dominio.

## Casos HTTP verificados

Se probaron satisfactoriamente:

1. creación;
2. listado;
3. obtención por ID;
4. CUIT/CUIL duplicado;
5. PUT completo;
6. PUT incompleto → `422`;
7. PATCH parcial conservando campos omitidos;
8. PATCH con `null` explícito;
9. PATCH inválido sobre `razon_social`;
10. actualización con CUIT/CUIL duplicado;
11. baja lógica;
12. consulta posterior a baja → `404`;
13. segunda eliminación vía caso de uso → `404`.

## Resultado

`Proveedor` queda migrado y validado de extremo a extremo.

La migración permitió además formalizar una distinción HTTP que antes era ambigua:

```text
PUT   → reemplazo completo
PATCH → actualización parcial
```

Este patrón debe revisarse al migrar otras entidades que tengan campos opcionales.
