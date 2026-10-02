# ADR-027: Política monetaria con Decimal

**Estado:** Aceptado
**Fecha:** 2026-09-25

## Contexto

PostgreSQL ya almacenaba los importes mediante `NUMERIC(10,2)` y SQLAlchemy
los entregaba como `Decimal`. Sin embargo, el dominio, los casos de uso y los
contratos HTTP utilizaban `float`, y los mappers convertían explícitamente los
valores de la base de `Decimal` a `float`.

Los tests de caracterización mostraron que ese recorrido introducía
comportamientos dependientes de la representación binaria. Por ejemplo,
`round(2.675, 2)` sobre un `float` de Python produce `2.67`, en lugar del
resultado decimal esperado `2.68`.

También se identificó una inconsistencia histórica en Compra. Un
`precio_unitario` recibido como `1.005` podía participar en el cálculo antes
de ser ajustado a la escala de la columna. Con cantidad `3`, el subtotal se
calculaba a partir del valor original mientras PostgreSQL persistía el precio
con dos decimales. Como consecuencia, el precio unitario almacenado
multiplicado por la cantidad podía no coincidir con el subtotal almacenado.

## Decisión

- Todo valor monetario del núcleo de dominio y aplicación utiliza `Decimal`.
- La escala monetaria se expresa mediante
  `CENTAVO = Decimal("0.01")`.
- El cero monetario se expresa mediante
  `CERO_DINERO = Decimal("0.00")`.
- La política de redondeo explícita es `ROUND_HALF_UP`.
- Todo importe de entrada se valida y normaliza a dos decimales antes de
  participar en multiplicaciones o sumas.
- Los importes deben ser finitos y no negativos. Cero continúa siendo válido;
  valores negativos, `NaN` e infinitos se rechazan.
- No se construye `Decimal` desde `float`. Los valores se reciben como
  `Decimal` o se crean desde representaciones decimales exactas.
- Stock y cantidad permanecen como `int`; no son magnitudes monetarias.
- Los schemas HTTP de request para importes utilizan `Decimal`.
- Los modelos ORM y PostgreSQL conservan `Numeric(10,2)` y `NUMERIC(10,2)`.
- Los schemas HTTP de response conservan temporalmente campos `float` para
  mantener el contrato público de JSON numbers.
- Reportes conserva temporalmente su conversión por movimiento a `float` y su
  acumulación en Python para preservar el comportamiento observable ya
  caracterizado.

## Aplicación de la política

En Venta, el precio proviene de `Producto.precio_venta`, se normaliza antes de
calcular el detalle y se utiliza con una cantidad entera. Cada subtotal y el
total se normalizan explícitamente.

En Compra, el precio continúa proviniendo del request y no de
`Producto.precio_compra`. El mismo precio normalizado se utiliza para
`CompraDetalle.precio_unitario` y para calcular el subtotal. La compra no
modifica `Producto.precio_compra`.

Así, un precio recibido como `1.005` se normaliza a `1.01` antes del cálculo y,
para cantidad `3`, produce un subtotal de `3.03`. El precio persistido por la
cantidad vuelve a coincidir con el subtotal.

## Elección de ROUND_HALF_UP

Mantener `float` fue descartado porque no representa exactamente la mayoría de
las fracciones decimales y hace que el resultado de casos límite dependa de la
aproximación binaria. La base ya usa aritmética decimal, por lo que convertir a
`float` en los mappers perdía precisión sin aportar una ventaja al núcleo.

`ROUND_HALF_EVEN` también fue descartado como política de negocio. Aunque
reduce sesgo estadístico en ciertos conjuntos, redondea los empates hacia el
dígito par. Por ejemplo, `Decimal("2.685")` se convertiría en `2.68`.
`ROUND_HALF_UP` expresa la regla elegida para importes: un empate exacto se
redondea alejándose de cero, por lo que `2.675` produce `2.68` y `2.685`
produce `2.69`.

No se modifica el contexto global de `Decimal`; la estrategia se indica en
cada normalización monetaria.

## Consecuencias positivas

- Los cálculos monetarios son decimales, explícitos y deterministas.
- Los mappers preservan `Decimal` entre ORM y dominio sin conversiones
  intermedias a `float`.
- El precio normalizado, la cantidad y el subtotal mantienen una relación
  consistente.
- Las reglas para escala, redondeo, finitud y signo quedan centralizadas.
- Los casos límite quedan cubiertos por tests unitarios y de integración.

## Cambios deliberados de comportamiento

- `2.675` se normaliza a `2.68` y `2.685` a `2.69`.
- Compra normaliza el precio antes del cálculo, corrigiendo la divergencia
  histórica entre precio persistido por cantidad y subtotal.
- `NaN`, infinitos e importes negativos dejan de aceptarse en el núcleo
  monetario.

Estos cambios son correcciones deliberadas de comportamientos legacy y no una
consecuencia accidental de cambiar anotaciones de tipos.

## Persistencia y migraciones

La decisión no requiere una revisión de Alembic. Las columnas físicas ya eran
`NUMERIC(10,2)` y los modelos ORM ya utilizaban `Numeric(10,2)`; sólo cambia la
representación y aritmética en Python.

## Deudas pendientes

- Decidir si los responses monetarios deben adoptar explícitamente un contrato
  decimal y cómo se representaría en JSON.
- Evaluar y ejecutar, si corresponde, la migración de la aritmética interna de
  Reportes sin romper su contrato observable.
- Revisar si el dominio llega a necesitar una abstracción `Money` más rica que
  el helper actual, por ejemplo para incorporar moneda o reglas adicionales.
