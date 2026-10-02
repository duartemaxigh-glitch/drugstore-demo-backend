# Actualización 008 — Ajuste de casos de uso de MedioPago

**Fecha:** 2026-09-21  
**Estado:** decisión aplicada / pendiente de prueba HTTP

## Contexto

El repositorio SQLAlchemy de `MedioPago` cambió sus contratos para poder representar que un registro desaparezca entre una comprobación previa y la operación efectiva:

```python
actualizar(...) -> MedioPago | None
eliminar(...) -> bool
```

Los casos de uso originales sólo comprobaban existencia antes de llamar al repositorio.

## Riesgo detectado

Entre:

```text
obtener_por_id()
```

y:

```text
actualizar() / eliminar()
```

otra transacción podría modificar o eliminar el registro.

Por lo tanto, una comprobación previa no garantiza que la operación posterior vaya a encontrar todavía la fila.

## Decisión

Se conserva temporalmente la comprobación inicial para no mezclar la migración con un refactor mayor, pero además se comprueba el resultado real de la operación.

### ActualizarMedioPago

```python
class ActualizarMedioPago:
    def __init__(self, repositorio: RepositorioMedioPago):
        self.repositorio = repositorio

    def ejecutar(self, id_medio_pago: int, nombre: str) -> MedioPago:
        existente = self.repositorio.obtener_por_id(id_medio_pago)

        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el medio de pago con id {id_medio_pago}."
            )

        medio_pago = MedioPago(
            nombre=nombre,
            id_medio_pago=id_medio_pago,
        )
        medio_pago.validar()

        actualizado = self.repositorio.actualizar(medio_pago)

        if actualizado is None:
            raise EntidadNoEncontrada(
                f"No se encontró el medio de pago con id {id_medio_pago}."
            )

        return actualizado
```

### EliminarMedioPago

```python
class EliminarMedioPago:
    def __init__(self, repositorio: RepositorioMedioPago):
        self.repositorio = repositorio

    def ejecutar(self, id_medio_pago: int) -> None:
        existente = self.repositorio.obtener_por_id(id_medio_pago)

        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el medio de pago con id {id_medio_pago}."
            )

        eliminado = self.repositorio.eliminar(id_medio_pago)

        if not eliminado:
            raise EntidadNoEncontrada(
                f"No se encontró el medio de pago con id {id_medio_pago}."
            )
```

## Nota de diseño

La doble consulta puede revisarse más adelante. Una alternativa futura sería confiar directamente en `actualizar()` y `eliminar()` y convertir `None` / `False` en `EntidadNoEncontrada`, eliminando la comprobación previa.

No se realiza ese refactor ahora para mantener acotada la migración.
