# ADR-028: Política de concurrencia para modificaciones de stock

**Estado:** Aceptado
**Fecha:** 2026-09-25

## Contexto

PostgreSQL trabaja actualmente con aislamiento `READ COMMITTED`. Antes de esta
decisión, los casos de uso leían cada Producto sin bloqueo, calculaban el nuevo
stock en Python y entregaban el valor resultante al repositorio. SQLAlchemy
terminaba ejecutando un `UPDATE` con ese valor absoluto.

El `UPDATE` adquiría un lock sobre la fila, pero lo hacía después de que el
nuevo stock ya hubiera sido calculado. Dos transacciones podían, por lo tanto,
calcular valores a partir de la misma lectura y sobrescribir posteriormente el
resultado de la otra.

El problema se reprodujo mediante un test de integración con PostgreSQL real:

- el stock inicial era `5`;
- dos ejecuciones concurrentes de CrearVenta intentaban vender `4` unidades
  cada una;
- ambas leían stock `5`;
- ambas calculaban stock `1`;
- una de ellas esperaba durante el `UPDATE` mientras la otra conservaba el
  lock;
- después de la espera, la segunda también escribía el valor absoluto `1`;
- ambas ventas confirmaban y quedaban registrados dos movimientos por un total
  de `8` unidades;
- el stock final era `1`.

Este comportamiento constituye un lost update: una modificación confirmada se
perdía al ser reemplazada por otro valor calculado sobre una lectura obsoleta.

La misma forma de concurrencia podía afectar a:

- dos CrearCompra, perdiendo una de las sumas;
- CrearVenta concurrente con CrearCompra, perdiendo uno de los deltas;
- las restituciones y descuentos efectuados por EliminarVenta y
  EliminarCompra;
- ActualizarProducto, que pretendía conservar stock pero podía volver a
  escribir un valor leído antes de un movimiento concurrente.

## Decisión

Se adopta control de concurrencia pesimista mediante `SELECT ... FOR UPDATE`
para toda modificación de stock existente.

### Modificaciones de stock

Todos los productos involucrados en una operación se bloquean antes de
validar o calcular sus nuevos stocks.

Los identificadores de producto:

- se deduplican únicamente para adquirir locks;
- se ordenan ascendentemente;
- se bloquean en ese orden mediante una única lectura.

La consulta conceptual es:

```sql
SELECT ...
FROM productos
WHERE id_producto IN (...)
ORDER BY id_producto
FOR UPDATE;
```

Después de adquirir los locks, los detalles se procesan en su orden original.
Esto preserva las reglas existentes, incluidos productos repetidos, validación
incremental de stock en Venta, snapshots de precio y cálculos monetarios.

El stock final se persiste una única vez por producto. Los repositorios hacen
`flush()`, pero no confirman ni revierten la transacción.

### Orden global de locks

CrearVenta y CrearCompra respetan el siguiente orden:

```text
productos únicos ascendentes
→ cálculos y validaciones
→ actualización de stocks
→ persistencia del agregado
```

EliminarVenta y EliminarCompra respetan:

```text
cabecera FOR UPDATE
→ carga de detalles
→ productos únicos ascendentes FOR UPDATE
→ modificación de stocks
→ eliminación del agregado
```

Una eliminación nunca bloquea productos antes de intentar bloquear su
cabecera. Mantener un orden global reduce el riesgo de deadlocks entre
operaciones que afectan varios productos o que reciben los mismos productos en
órdenes diferentes.

### Eliminaciones

La cabecera de Venta o Compra se bloquea antes de cargar los detalles que se
utilizarán para revertir stock. La cabecera y los detalles se consultan dentro
de la misma Session y transacción, pero la carga de detalles ocurre sólo
después de obtener el lock de cabecera.

No se agrega un `FOR UPDATE` explícito sobre los detalles porque el sistema no
ofrece mutaciones independientes de detalle. El lock de la cabecera serializa
las operaciones relevantes y la integridad referencial protege la relación
con el agregado.

Si dos transacciones intentan eliminar la misma cabecera:

1. la primera obtiene el lock y continúa;
2. la segunda espera en su `SELECT ... FOR UPDATE` de cabecera;
3. la primera modifica stock, elimina el agregado y confirma;
4. al continuar bajo `READ COMMITTED`, la segunda ya no obtiene la fila;
5. el repositorio devuelve `None` y la segunda operación no bloquea ni modifica
   productos.

`eliminar() -> bool` se conserva como defensa adicional. Un resultado `False`
provoca una excepción y el rollback completo de cualquier cambio previo.

### Separación entre catálogo y stock

`RepositorioProducto` separa tres capacidades:

- `obtener_para_modificar_stock(ids_producto)` obtiene estado vigente y
  bloquea los productos existentes;
- `actualizar_stocks(nuevos_stocks)` modifica exclusivamente stock y verifica
  que todos los IDs esperados hayan sido actualizados;
- `actualizar_datos(producto)` modifica exclusivamente código de barras,
  nombre, precios y categoría.

`actualizar_datos()` nunca escribe stock. El antiguo `actualizar(producto)`
actualizaba todas las columnas y podía restaurar un stock obsoleto cuando una
edición de catálogo competía con Venta o Compra.

### Estado fresco e identity map

Una lectura bloqueada debe representar el estado vigente de PostgreSQL después
de cualquier espera. No puede reutilizar silenciosamente atributos obsoletos de
una instancia que ya estuviera presente en el identity map de la Session.

La implementación utiliza `populate_existing` en las lecturas exclusivas y
refresca el modelo cuando corresponde antes de mapearlo al dominio. La
actualización de catálogo utiliza el estado persistido devuelto por PostgreSQL
y vuelve a cargar el modelo antes de construir la respuesta.

### Unidad de trabajo

Los locks pertenecen a la transacción de la Session y permanecen activos hasta
que `UnidadDeTrabajoSQLAlchemy` ejecuta `commit()` o `rollback()`.

Los repositorios:

- no hacen `commit()`;
- no hacen `rollback()`;
- no cierran la Session;
- pueden ejecutar `flush()`.

La UoW continúa siendo la frontera transaccional y garantiza que una excepción
revierta stocks, cabeceras y detalles, además de liberar automáticamente los
locks adquiridos.

## Alternativas consideradas

### UPDATE atómico condicional

Una alternativa válida para el descuento de stock es:

```sql
UPDATE productos
SET stock = stock - :cantidad
WHERE id_producto = :id
  AND stock >= :cantidad;
```

Este enfoque puede ser más corto para una operación simple, pero no se adoptó
en esta etapa porque:

- los casos de uso actuales necesitan leer el Producto completo;
- Venta necesita simultáneamente precio y stock;
- Compra, restituciones y eliminaciones tienen semánticas diferentes;
- los productos repetidos complicarían el contrato y la interpretación de
  resultados parciales;
- serían necesarias varias operaciones especializadas para suma, descuento
  condicional y resta con piso cero;
- los propios `UPDATE` también adquieren locks;
- las operaciones multiproducto seguirían necesitando un orden consistente de
  adquisición para reducir deadlocks.

El uso de `SELECT ... FOR UPDATE` mantiene una política uniforme y se adapta a
los contratos y reglas actuales.

### Optimistic locking o versionado

El versionado de Producto también sería una alternativa válida. Requeriría:

- agregar y mantener una columna de versión;
- detectar actualizaciones que no coincidan con la versión leída;
- definir una política explícita de retry o de error visible;
- adaptar casos de uso, contratos, persistencia y tests.

No fue necesario para el modelo de concurrencia actual.

### Mantener el comportamiento previo

Se descartó porque el lost update fue reproducido de forma determinista contra
PostgreSQL real. No era un riesgo únicamente teórico.

## Consecuencias positivas

- Las decisiones de stock se calculan sobre estado protegido y vigente.
- No se observan lost updates en los escenarios cubiertos.
- Dos ventas incompatibles ya no pueden confirmar ambas.
- Las compras concurrentes preservan todas las sumas.
- Venta y Compra concurrentes conservan ambos deltas.
- Las eliminaciones de una misma cabecera restituyen o descuentan stock una
  sola vez.
- Catálogo y stock ya no sobrescriben mutuamente sus columnas.
- Un rollback revierte cambios y libera locks para las transacciones en espera.
- Los productos repetidos mantienen su semántica secuencial y se persisten una
  sola vez.

## Costos y riesgos

- Las operaciones concurrentes sobre las mismas filas pueden esperar.
- Los locks se conservan hasta el `commit()` o `rollback()` de la UoW.
- Una transacción larga incrementa la contención.
- Todo nuevo flujo que modifique stock debe utilizar los contratos exclusivos y
  respetar el orden global.
- Adquirir las mismas filas en un orden diferente puede reintroducir
  deadlocks.
- La corrección depende de mantener en una misma UoW los repositorios que
  participan en la operación.

## Evidencia de verificación

El comportamiento anterior fue caracterizado primero mediante un integration
test que reprodujo el lost update real. Después de implementar la política, se
verificaron con PostgreSQL real:

- dos CrearVenta concurrentes;
- dos CrearCompra concurrentes;
- CrearVenta concurrente con CrearCompra;
- doble EliminarVenta sobre la misma cabecera;
- doble EliminarCompra sobre la misma cabecera;
- ActualizarProducto concurrente con CrearVenta;
- operaciones multiproducto recibidas en orden inverso;
- productos repetidos;
- rollback mientras otra transacción esperaba un lock;
- refresco de una instancia ya presente en el identity map.

Los tests concurrentes se repitieron para verificar estabilidad. El estado
validado fue:

- `50` tests aprobados;
- cero lost updates observados;
- cero deadlocks inesperados;
- cero schemas temporales de pytest residuales;
- sin cambios de esquema ni nuevas revisiones de Alembic.
