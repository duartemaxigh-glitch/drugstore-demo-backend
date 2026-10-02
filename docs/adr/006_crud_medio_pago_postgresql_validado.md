# Actualización 006 — CRUD de MedioPago migrado y validado contra PostgreSQL

**Fecha:** 2026-09-21  
**Estado:** completado

## 1. Alcance

Se completó la migración de `MedioPago` desde el repositorio MySQL basado en PyMySQL hacia SQLAlchemy 2.x con PostgreSQL, manteniendo la separación entre dominio e infraestructura y la política transaccional basada en Unidad de Trabajo.

## 2. Entidad de dominio

La entidad permanece sin dependencia de SQLAlchemy.

## 3. Semántica original del repositorio MySQL

El repositorio MySQL implementaba:

- `crear()` mediante `INSERT`;
- `obtener_por_id()` por PK;
- `obtener_todos()` ordenado por `id_medio_pago`;
- `actualizar()` modificando sólo `nombre`;
- `eliminar()` mediante `DELETE` físico.

No existe baja lógica en `MedioPago`.

Problemas heredados detectados:

- conexión nueva por método;
- autocommit;
- traducción de duplicados inspeccionando texto de excepción;
- `actualizar()` no representaba la posible desaparición concurrente;
- `eliminar()` no informaba si la fila existía.

## 4. Esquema PostgreSQL verificado

La tabla `medios_pago` contiene:

| Columna | Tipo | Longitud | Nullable | Default |
|---|---|---:|---|---|
| `id_medio_pago` | integer | — | NO | secuencia |
| `nombre` | varchar | 50 | NO | — |

Constraints observadas:

```text
medios_pago_id_medio_pago_not_null
medios_pago_nombre_not_null
medios_pago_pkey
medios_pago_nombre_key
```

La constraint relevante para duplicados es `medios_pago_nombre_key`.

## 5. Modelo ORM

```python
class MedioPagoModelo(Base):
    __tablename__ = "medios_pago"

    id_medio_pago: Mapped[int] = mapped_column(
        primary_key=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )
```

## 6. Mapper

```python
def a_dominio(modelo: MedioPagoModelo) -> MedioPago:
    return MedioPago(
        id_medio_pago=modelo.id_medio_pago,
        nombre=modelo.nombre,
    )


def nuevo_modelo(medio_pago: MedioPago) -> MedioPagoModelo:
    return MedioPagoModelo(
        nombre=medio_pago.nombre,
    )
```

## 7. Repository SQLAlchemy

La implementación recibe una `Session` inyectada.

### Crear

Usa `session.add()` y `session.flush()`. Las violaciones de unicidad se distinguen mediante `e.orig.diag.constraint_name` y se traduce específicamente `medios_pago_nombre_key` a `EntidadDuplicada`.

### Obtener por ID

Usa `session.get(MedioPagoModelo, id_medio_pago)` y devuelve `None` si no existe.

### Obtener todos

Usa `select(MedioPagoModelo).order_by(MedioPagoModelo.id_medio_pago)` seguido de `session.scalars(stmt).all()`.

### Actualizar

La firma quedó:

```python
def actualizar(
    self,
    medio_pago: MedioPago,
) -> MedioPago | None:
```

Se obtiene el modelo persistente, se modifica `nombre`, se usa dirty checking y `flush()`, y se devuelve `None` si el registro ya no existe.

### Eliminar

La firma quedó:

```python
def eliminar(
    self,
    id_medio_pago: int,
) -> bool:
```

La eliminación es física mediante:

```python
self.session.delete(modelo)
self.session.flush()
```

Devuelve `True` si existía y `False` si no existía.

## 8. Política transaccional

El repository no realiza `commit`, `rollback` ni `close`. Esas responsabilidades pertenecen a la Unidad de Trabajo. El repository usa `flush()` cuando necesita materializar operaciones dentro de la transacción.

## 9. Pruebas realizadas

Se validaron satisfactoriamente contra PostgreSQL:

1. creación de `Efectivo`;
2. creación de `Tarjeta`;
3. creación duplicada de `Efectivo` → `EntidadDuplicada`;
4. obtención por ID;
5. listado completo;
6. actualización de registro existente;
7. actualización de ID inexistente → `None`;
8. actualización a nombre duplicado → `EntidadDuplicada`;
9. eliminación de registro existente → `True`;
10. segunda eliminación del mismo ID → `False`;
11. consulta posterior a eliminación → `None`.

## 10. Resultado

El CRUD de `MedioPago` queda migrado y validado directamente contra PostgreSQL.

Queda pendiente su integración a través de FastAPI para validar:

```text
HTTP
↓
FastAPI
↓
Caso de uso
↓
RepositorioMedioPagoSQLAlchemy
↓
Session SQLAlchemy
↓
PostgreSQL
↓
UoW
```
