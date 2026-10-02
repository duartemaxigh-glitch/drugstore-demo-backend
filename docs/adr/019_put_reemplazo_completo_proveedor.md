# Actualización 019 — PUT como reemplazo completo de Proveedor

**Fecha:** 2026-09-22  
**Estado:** decisión aplicada

## Decisión

El endpoint:

```http
PUT /proveedores/{id_proveedor}
```

se interpreta como reemplazo completo del estado editable del proveedor.

Para ello se utiliza un esquema específico:

```python
class ProveedorReemplazar(BaseModel):
    razon_social: str
    cuit_cuil: str | None
    contacto_nombre: str | None
    telefono: str | None
    email: str | None
```

En Pydantic v2:

- todos los campos anteriores son obligatorios en el payload;
- los campos declarados como `str | None` pueden recibir explícitamente `null`;
- `razon_social` no admite `null`.

## Caso de uso

El caso de uso puede seguir construyendo una entidad `Proveedor` nueva con el estado completo recibido y enviarla al repository.

Como mejora semántica, los argumentos nullable del caso de uso no deberían tener `= None`, ya que en un reemplazo completo siguen siendo argumentos obligatorios aunque puedan contener `None`.

Firma recomendada:

```python
def ejecutar(
    self,
    id_proveedor: int,
    razon_social: str,
    cuit_cuil: str | None,
    contacto_nombre: str | None,
    telefono: str | None,
    email: str | None,
) -> Proveedor:
```

## Campo `activo`

`activo` no forma parte del reemplazo editable:

- la baja lógica se maneja mediante el caso de uso de eliminación;
- el repository de actualización no modifica `activo`.

Por lo tanto, no es necesario incluirlo en `ProveedorReemplazar`.

## Diferencia con PATCH

- `PUT`: todos los campos editables deben estar presentes.
- `PATCH`: sólo se modifican los campos enviados, usando `model_dump(exclude_unset=True)`.

Esto elimina la ambigüedad detectada previamente entre campo omitido y campo enviado como `null`.
