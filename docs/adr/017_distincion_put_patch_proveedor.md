# Actualización 017 — Distinción entre PUT y PATCH en Proveedor

**Fecha:** 2026-09-21  
**Estado:** decisión de diseño propuesta

## Problema detectado

El endpoint actual de actualización recibe un esquema cuyos campos opcionales pueden quedar en `None` cuando no son enviados.

El caso de uso construye un nuevo `Proveedor` con esos valores y el repository copia todos los campos al modelo ORM.

Como resultado, una request como:

```json
{
  "razon_social": "Nueva razón social"
}
```

puede sobrescribir con `NULL` los campos omitidos:

```text
cuit_cuil
contacto_nombre
telefono
email
```

## Distinción propuesta

Se separan dos operaciones con semánticas diferentes.

### PUT — reemplazo completo

`PUT /proveedores/{id}` representa el estado completo editable del proveedor.

Los campos nullable pueden aceptar `null`, pero deben estar presentes en el payload si forman parte del reemplazo completo.

Ejemplo conceptual:

```python
class ProveedorReemplazar(BaseModel):
    razon_social: str
    cuit_cuil: str | None
    contacto_nombre: str | None
    telefono: str | None
    email: str | None
```

En Pydantic v2, un campo `str | None` sin valor por defecto es obligatorio en el payload, aunque acepte `null`.

### PATCH — actualización parcial

`PATCH /proveedores/{id}` modifica únicamente los campos enviados.

Ejemplo conceptual:

```python
class ProveedorActualizarParcial(BaseModel):
    razon_social: str | None = None
    cuit_cuil: str | None = None
    contacto_nombre: str | None = None
    telefono: str | None = None
    email: str | None = None
```

Para distinguir entre campo omitido y campo enviado explícitamente como `null` se usa:

```python
cambios = datos.model_dump(exclude_unset=True)
```

Ejemplos:

```json
{
  "razon_social": "Nueva razón social"
}
```

significa modificar sólo `razon_social`.

Mientras que:

```json
{
  "telefono": null
}
```

significa borrar explícitamente el teléfono.

## Validación

Después de aplicar los cambios parciales sobre el estado existente, debe validarse la entidad resultante.

Esto evita aceptar estados inválidos, por ejemplo `razon_social = null`.

## Alcance

Esta distinción no es específica de SQLAlchemy. Es una decisión de semántica HTTP y de caso de uso que la migración permitió detectar.

El patrón debería revisarse posteriormente en otras entidades cuyos endpoints de actualización acepten campos opcionales.
