# Actualización 012 — Revisión inicial de RepositorioProveedorSQLAlchemy

**Fecha:** 2026-09-21  
**Estado:** correcciones detectadas

## Implementación revisada

Se revisaron los métodos:

- `crear()`
- `obtener_por_id()`
- `obtener_todos()`

## Correcciones necesarias

### 1. Nombre de la clase

Se detectó:

```python
class RepositorioProveedorWSQLAlchemy(RepositorioProveedor):
```

Debe revisarse si la `W` es un typo. El nombre esperado es:

```python
class RepositorioProveedorSQLAlchemy(RepositorioProveedor):
```

### 2. `crear()`

El manejo de `IntegrityError` debe volver a propagar cualquier error que no sea la constraint conocida.

Además, al traducir la excepción a `EntidadDuplicada`, se debe conservar la causa mediante `raise ... from e`.

Patrón correcto:

```python
except IntegrityError as e:
    if isinstance(e.orig, UniqueViolation):
        constraint = e.orig.diag.constraint_name

        if constraint == "proveedores_cuit_cuil_key":
            raise EntidadDuplicada(
                f"Ya existe un proveedor con CUIT/CUIL '{proveedor.cuit_cuil}'."
            ) from e

    raise
```

Sin el `raise` final, un `IntegrityError` no reconocido podría quedar oculto y la `Session` permanecería en estado fallido.

### 3. `obtener_por_id()`

`select(...)` construye una sentencia SQLAlchemy, pero no la ejecuta.

Se debe ejecutar mediante la `Session`:

```python
stmt = (
    select(ProveedorModelo)
    .where(
        ProveedorModelo.id_proveedor == id_proveedor,
        ProveedorModelo.activo.is_(True),
    )
)

modelo = self.session.scalar(stmt)
```

Luego se comprueba `modelo is None`.

### 4. `obtener_todos()`

De igual forma, `select(...)` no devuelve modelos ORM.

Se debe ejecutar:

```python
stmt = (
    select(ProveedorModelo)
    .where(ProveedorModelo.activo.is_(True))
    .order_by(ProveedorModelo.id_proveedor)
)

modelos = self.session.scalars(stmt).all()
```

y después mapear cada modelo a dominio.

## Semántica preservada

Las lecturas continúan filtrando:

```text
activo = TRUE
```

como hacía el repositorio MySQL original.

El manejo de duplicados se basa en la constraint PostgreSQL:

```text
proveedores_cuit_cuil_key
```
