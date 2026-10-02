# Actualización 015 — Revisión del router FastAPI de Proveedor

**Fecha:** 2026-09-21  
**Estado:** router compatible / casos de uso pendientes de revisión

## Router revisado

El router de `Proveedor` expone:

- `POST /` → crear proveedor;
- `GET /` → listar proveedores;
- `GET /{id_proveedor}` → obtener por ID;
- `PUT /{id_proveedor}` → actualizar;
- `DELETE /{id_proveedor}` → baja lógica.

Todos los endpoints usan:

```text
obtener_repo_proveedor
obtener_usuario_actual
```

## Integración esperada con SQLAlchemy

La dependencia debe estar compuesta con la Unidad de Trabajo:

```python
def obtener_repo_proveedor(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
) -> RepositorioProveedor:
    return RepositorioProveedorSQLAlchemy(uow.session)
```

## Traducción HTTP

El router ya traduce correctamente:

- `ErrorDeValidacion` → `400 Bad Request`;
- `EntidadDuplicada` → `409 Conflict`;
- `EntidadNoEncontrada` → `404 Not Found`.

El endpoint `DELETE` usa:

```python
status_code=status.HTTP_204_NO_CONTENT
```

y no devuelve cuerpo.

## Punto pendiente

El repositorio SQLAlchemy usa:

```python
actualizar(...) -> Proveedor | None
eliminar(...) -> bool
```

Por eso, antes de ejecutar las pruebas HTTP completas, deben revisarse `ActualizarProveedor` y `EliminarProveedor` para confirmar que convierten `None` / `False` en `EntidadNoEncontrada`.

## Nota

La baja lógica de Proveedor permanece encapsulada en el repositorio. El router no necesita conocer el campo `activo`.
