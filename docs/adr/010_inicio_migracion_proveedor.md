# Actualización 010 — Inicio de migración de Proveedor

**Fecha:** 2026-09-21  
**Estado:** en progreso

## Código auditado

Se revisaron:

- entidad de dominio `Proveedor`;
- interfaz `RepositorioProveedor`;
- implementación `RepositorioProveedorMySQL`.

## Entidad de dominio

`Proveedor` contiene:

- `id_proveedor`;
- `razon_social`;
- `cuit_cuil`;
- `contacto_nombre`;
- `telefono`;
- `email`;
- `activo`.

Validaciones existentes:

- `razon_social` obligatoria;
- `cuit_cuil`, si existe, sólo numérico;
- `contacto_nombre`, si existe, sólo letras;
- `telefono`, si existe, sólo numérico;
- `email`, si existe, formato válido.

## Semántica actual del repositorio MySQL

### Crear

Inserta:

```text
razon_social
cuit_cuil
contacto_nombre
telefono
email
```

No inserta explícitamente `activo`, por lo que el esquema de base de datos debe aportar su valor por defecto.

### Obtener por ID

Filtra:

```sql
WHERE id_proveedor = ? AND activo = TRUE
```

Por tanto, un proveedor inactivo se considera no disponible para las lecturas ordinarias.

### Obtener todos

Filtra:

```sql
WHERE activo = TRUE
ORDER BY id_proveedor
```

### Actualizar

Actualiza:

```text
razon_social
cuit_cuil
contacto_nombre
telefono
email
```

y busca únicamente por `id_proveedor`.

No actualiza `activo`.

### Eliminar

Implementa baja lógica:

```sql
UPDATE proveedores
SET activo = FALSE
WHERE id_proveedor = ?
```

No existe `DELETE` físico.

## Contrato actual

La interfaz ya fue ajustada al patrón adoptado durante la migración:

```python
actualizar(...) -> Proveedor | None
eliminar(...) -> bool
```

Esto permite representar que el registro no exista al momento efectivo de la operación.

## Duplicados

El repositorio MySQL traduce cualquier error cuyo texto contenga `Duplicate` como:

```text
Ya existe un proveedor con ese CUIT/CUIL.
```

Antes de portar este comportamiento a PostgreSQL es necesario verificar qué columnas tienen realmente restricciones `UNIQUE` y cuáles son sus nombres.

## Próximo paso

Verificar el esquema PostgreSQL real de `proveedores` antes de definir `ProveedorModelo`.

Se necesitan:

- tipos;
- longitudes;
- nullability;
- defaults;
- constraints;
- nombres de constraints `UNIQUE`.
