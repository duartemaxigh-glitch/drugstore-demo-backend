# Actualización 018 — Revisión de PATCH parcial de Proveedor

**Fecha:** 2026-09-22  
**Estado:** solución aceptada con mejoras opcionales

## Implementación revisada

El endpoint `PATCH /proveedores/{id_proveedor}` utiliza:

```python
cambios = datos.model_dump(exclude_unset=True)
```

para conservar únicamente los campos realmente enviados por el cliente.

El caso de uso:

1. obtiene el proveedor activo existente;
2. aplica sólo las claves presentes en `cambios`;
3. valida el estado final de la entidad;
4. envía la entidad completa resultante al repository;
5. comprueba que la actualización efectiva no haya devuelto `None`.

## Evaluación

La solución es adecuada para la arquitectura actual porque:

- Pydantic permanece en la capa HTTP;
- aplicación recibe tipos Python normales;
- dominio sigue trabajando con `Proveedor`;
- repository continúa recibiendo una entidad completa;
- se distingue correctamente entre campo omitido y campo enviado explícitamente como `null`.

Ejemplo:

```json
{"telefono": null}
```

produce:

```python
{"telefono": None}
```

con `exclude_unset=True`, mientras que omitir `telefono` hace que esa clave no aparezca en `cambios`.

## Mejoras opcionales

### PATCH vacío

Actualmente `{}` es válido y produce una operación sin cambios. Puede aceptarse como no-op o rechazarse explícitamente según la semántica deseada.

### Tipado

`dict` es suficiente para esta etapa, aunque más adelante podría reemplazarse por un DTO/command de aplicación si se desea mayor tipado y evitar claves string dispersas.

No se recomienda introducir ese DTO ahora si no aporta una necesidad concreta.

## Conclusión

Para el proyecto actual, la estrategia `model_dump(exclude_unset=True)` + aplicación de cambios sobre la entidad recuperada es una solución limpia y coherente con la separación por capas.
