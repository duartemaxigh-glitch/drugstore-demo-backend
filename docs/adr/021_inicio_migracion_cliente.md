# Actualización 021 — Inicio de migración de Cliente

**Fecha:** 2026-09-22  
**Estado:** en progreso

## Código auditado

Se revisaron:

- entidad de dominio `Cliente`;
- interfaz `RepositorioCliente`;
- implementación `RepositorioClienteMySQL`.

## Entidad de dominio

`Cliente` contiene:

- `id_cliente`;
- `apellido`;
- `nombre`;
- `dni`;
- `cuit`;
- `telefono`;
- `activo`.

Todos los datos personales, salvo `activo`, son opcionales en el constructor actual.

Validaciones existentes:

- `apellido`, si existe, sólo letras;
- `nombre`, si existe, sólo letras;
- `dni`, si existe, sólo números;
- `cuit`, si existe, sólo números;
- `telefono`, si existe, sólo números.

## Semántica actual del repositorio MySQL

### Crear

Inserta:

```text
apellido
nombre
dni
cuit
telefono
```

No inserta explícitamente `activo`, por lo que la base de datos debe aportar su valor por defecto.

### Obtener por ID

Filtra:

```sql
WHERE id_cliente = ? AND activo = TRUE
```

### Obtener todos

Filtra:

```sql
WHERE activo = TRUE
ORDER BY id_cliente
```

### Actualizar

Actualiza:

```text
apellido
nombre
dni
cuit
telefono
```

y busca únicamente por `id_cliente`.

No actualiza `activo`.

### Eliminar

Implementa baja lógica:

```sql
UPDATE clientes
SET activo = FALSE
WHERE id_cliente = ?
```

No existe `DELETE` físico.

## Duplicados

La implementación MySQL traduce cualquier error cuyo texto contenga `Duplicate` como:

```text
Ya existe un cliente con ese DNI o CUIT.
```

Antes de portar este comportamiento a PostgreSQL se debe verificar:

- si `dni` es realmente `UNIQUE`;
- si `cuit` es realmente `UNIQUE`;
- los nombres exactos de ambas constraints.

## Ajuste de contrato recomendado

Para mantener el patrón adoptado durante la migración:

```python
actualizar(...) -> Cliente | None
eliminar(...) -> bool
```

Esto permite representar correctamente que una fila no exista al momento efectivo de la operación.

## PUT / PATCH

Como `Cliente` tiene varios campos opcionales, debe conservarse la distinción ya adoptada para `Proveedor`:

```text
PUT   → reemplazo completo del estado editable
PATCH → actualización parcial
```

La semántica exacta se revisará al integrar el router.

## Próximo paso

Verificar el esquema PostgreSQL real de `clientes` antes de definir `ClienteModelo`.

Se necesitan:

- tipos;
- longitudes;
- nullability;
- defaults;
- constraints;
- nombres de constraints `UNIQUE`.
