# Actualización 007 — Integración FastAPI de MedioPago

**Fecha:** 2026-09-21  
**Estado:** en revisión

## Router auditado

El router de `MedioPago` ya está estructurado de forma compatible con el repositorio SQLAlchemy y la Unidad de Trabajo.

Los endpoints cubren:

- `POST /` → crear medio de pago.
- `GET /` → listar.
- `GET /{id_medio_pago}` → obtener por ID.
- `PUT /{id_medio_pago}` → actualizar.
- `DELETE /{id_medio_pago}` → eliminar.

Todos dependen de:

- `obtener_repo_medio_pago`;
- `obtener_usuario_actual`.

## Integración esperada

La dependencia de repositorio debe quedar compuesta con la UoW:

```python
def obtener_repo_medio_pago(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
) -> RepositorioMedioPago:
    return RepositorioMedioPagoSQLAlchemy(uow.session)
```

## Compatibilidad con los nuevos contratos

El repository SQLAlchemy usa:

```python
actualizar(...) -> MedioPago | None
eliminar(...) -> bool
```

Por lo tanto, los casos de uso `ActualizarMedioPago` y `EliminarMedioPago` deben transformar esos resultados en `EntidadNoEncontrada` cuando corresponda.

El router no necesita conocer `None` ni `False`: ya captura `EntidadNoEncontrada` y la traduce a HTTP `404`.

## DELETE 204

El endpoint de eliminación declara:

```python
status_code=status.HTTP_204_NO_CONTENT
```

y no devuelve cuerpo, lo cual es coherente con `204 No Content`.

## Próximo paso

Revisar los casos de uso `ActualizarMedioPago` y `EliminarMedioPago` antes de ejecutar las pruebas HTTP.
