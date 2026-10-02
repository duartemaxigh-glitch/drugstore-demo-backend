# Actualización 013 — Corrección de actualizar/eliminar en Proveedor

**Fecha:** 2026-09-21  
**Estado:** corrección requerida

## Hallazgo

La primera implementación SQLAlchemy de `actualizar()` y `eliminar()` filtraba por:

```python
ProveedorModelo.activo.is_(True)
```

y `eliminar()` utilizaba:

```python
session.delete(modelo)
```

Esto no es equivalente al repositorio MySQL original.

## Semántica original verificada

### Actualizar

El MySQL original ejecuta:

```sql
UPDATE proveedores
SET razon_social = ?, cuit_cuil = ?, contacto_nombre = ?,
    telefono = ?, email = ?
WHERE id_proveedor = ?
```

No filtra por `activo`.

Por tanto, la implementación SQLAlchemy debe buscar sólo por PK y permitir actualizar una fila inactiva si existe.

### Eliminar

El MySQL original ejecuta una baja lógica:

```sql
UPDATE proveedores
SET activo = FALSE
WHERE id_proveedor = ?
```

No realiza `DELETE` físico y tampoco filtra por `activo`.

Por tanto, la implementación SQLAlchemy debe:

1. buscar por PK;
2. devolver `False` si la fila no existe;
3. asignar `modelo.activo = False`;
4. ejecutar `flush()`;
5. devolver `True`.

## Implementación equivalente

```python
def actualizar(self, proveedor: Proveedor) -> Proveedor | None:
    modelo = self.session.get(
        ProveedorModelo,
        proveedor.id_proveedor,
    )

    if modelo is None:
        return None

    modelo.razon_social = proveedor.razon_social
    modelo.cuit_cuil = proveedor.cuit_cuil
    modelo.contacto_nombre = proveedor.contacto_nombre
    modelo.telefono = proveedor.telefono
    modelo.email = proveedor.email

    try:
        self.session.flush()
    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            constraint = e.orig.diag.constraint_name

            if constraint == "proveedores_cuit_cuil_key":
                raise EntidadDuplicada(
                    f"Ya existe un proveedor con CUIT/CUIL '{proveedor.cuit_cuil}'."
                ) from e

        raise

    return a_dominio(modelo)
```

```python
def eliminar(self, id_proveedor: int) -> bool:
    modelo = self.session.get(
        ProveedorModelo,
        id_proveedor,
    )

    if modelo is None:
        return False

    modelo.activo = False
    self.session.flush()

    return True
```

## Regla consolidada de Proveedor

- lecturas ordinarias (`obtener_por_id`, `obtener_todos`) ocultan filas inactivas;
- actualización busca por ID sin filtrar `activo`;
- eliminación es baja lógica y busca por ID sin filtrar `activo`.
