# Actualización 016 — Ajuste de casos de uso de Proveedor

**Fecha:** 2026-09-21  
**Estado:** corrección recomendada antes de prueba HTTP

## Contexto

`RepositorioProveedorSQLAlchemy` expone:

```python
actualizar(...) -> Proveedor | None
eliminar(...) -> bool
```

Los casos de uso originales verificaban existencia antes de ejecutar la operación, pero no comprobaban el resultado efectivo del repository.

## ActualizarProveedor

La comprobación inicial:

```python
existente = self.repositorio.obtener_por_id(id_proveedor)
```

sólo confirma que el proveedor existía en ese momento.

Entre esa lectura y el `UPDATE`, otra transacción podría eliminar físicamente la fila. Por ello, también debe comprobarse el resultado de `actualizar()`.

Versión recomendada:

```python
class ActualizarProveedor:
    def __init__(self, repositorio: RepositorioProveedor):
        self.repositorio = repositorio

    def ejecutar(
        self,
        id_proveedor: int,
        razon_social: str,
        cuit_cuil: str = None,
        contacto_nombre: str = None,
        telefono: str = None,
        email: str = None,
    ) -> Proveedor:
        existente = self.repositorio.obtener_por_id(id_proveedor)

        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el proveedor con id {id_proveedor}."
            )

        proveedor = Proveedor(
            id_proveedor=id_proveedor,
            razon_social=razon_social,
            cuit_cuil=cuit_cuil,
            contacto_nombre=contacto_nombre,
            telefono=telefono,
            email=email,
        )

        proveedor.validar()

        actualizado = self.repositorio.actualizar(proveedor)

        if actualizado is None:
            raise EntidadNoEncontrada(
                f"No se encontró el proveedor con id {id_proveedor}."
            )

        return actualizado
```

## EliminarProveedor

También debe comprobarse el `bool` devuelto por el repository:

```python
class EliminarProveedor:
    def __init__(self, repositorio: RepositorioProveedor):
        self.repositorio = repositorio

    def ejecutar(self, id_proveedor: int) -> None:
        existente = self.repositorio.obtener_por_id(id_proveedor)

        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el proveedor con id {id_proveedor}."
            )

        eliminado = self.repositorio.eliminar(id_proveedor)

        if not eliminado:
            raise EntidadNoEncontrada(
                f"No se encontró el proveedor con id {id_proveedor}."
            )
```

## Semántica de segunda eliminación

Hay una diferencia entre probar el repository directamente y hacerlo a través del caso de uso:

- el repository busca por PK sin filtrar `activo`, por lo que una segunda baja lógica puede devolver `True`;
- `EliminarProveedor` primero llama a `obtener_por_id()`, que sólo devuelve proveedores activos;
- por lo tanto, después de la primera baja lógica, una segunda eliminación a través del caso de uso produce `EntidadNoEncontrada`.

Esto preserva la semántica observable de la aplicación: un proveedor inactivo se considera no disponible.

## Nota

La consulta inicial y la comprobación posterior generan una doble verificación. Se conserva por ahora para no mezclar esta migración con un refactor mayor. Más adelante podría simplificarse confiando directamente en los resultados `None` / `False` del repository.
