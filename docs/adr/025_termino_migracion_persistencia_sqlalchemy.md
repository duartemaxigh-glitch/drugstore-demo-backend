# ADR-025: Término de la migración de persistencia a SQLAlchemy

**Estado:** Aceptado  
**Fecha:** 2026-09-23

## Contexto

CRUDrugstore comenzó con una infraestructura de persistencia basada en SQL
directo. Durante su evolución se adoptó PostgreSQL con psycopg2 y repositorios
que administraban conexiones y cursores de forma explícita.

La migración a SQLAlchemy se realizó de manera incremental para mantener la
funcionalidad del sistema durante la transición. Cada agregado y operación fue
auditado contra el esquema PostgreSQL real, preservando restricciones,
nulabilidad, bajas lógicas o físicas y comportamiento transaccional.

Venta y Compra requirieron una migración específica porque modifican stock y
persisten cabeceras y detalles dentro de una única operación. Los reportes
también requirieron una decisión propia porque son proyecciones de lectura y no
repositorios de entidades.

Finalizada la migración, no quedan consumidores ejecutables de la
infraestructura PostgreSQL directa.

## Decisión final

La persistencia del proyecto queda definida por las siguientes decisiones:

- PostgreSQL es la base de datos.
- SQLAlchemy 2.x es la única infraestructura de persistencia.
- psycopg 3 es el driver PostgreSQL.
- Las entidades de dominio permanecen separadas de los modelos ORM.
- Los modelos ORM viven en `infraestructura/basedatos/modelos`.
- Los mappers dominio ↔ ORM viven en
  `infraestructura/basedatos/mappers`.
- Los contratos de repositorio viven en `dominio/repositorios`.
- Los repositorios concretos viven en `infraestructura/repositorios` y
  reciben una `Session`.
- Los repositorios pueden ejecutar `flush()`, pero nunca administran
  `commit()`, `rollback()` ni `close()`.
- `UnidadDeTrabajoSQLAlchemy` administra la Session y la transacción desde
  la composición externa de FastAPI.
- Los casos de uso dependen de contratos de repositorio y no reciben una UoW.
- Una operación puede componer varios repositorios con exactamente la misma
  Session.
- Crear y eliminar Venta o Compra comparten Session con el repositorio de
  Producto para que movimientos, detalles y stock sean atómicos.
- Los errores conocidos de constraints se traducen en infraestructura a
  excepciones del dominio; los errores desconocidos se propagan.
- Reportes continúa siendo un query service. Usa `select()` de proyección,
  columnas ORM, joins explícitos y una Session inyectada; no se introduce un
  repositorio artificial ni se cargan agregados completos.
- psycopg2, la conexión manual, los repositorios PostgreSQL directos y la
  antigua UoW PostgreSQL fueron retirados.

## Límite transaccional

`api/dependencias.py` crea una `UnidadDeTrabajoSQLAlchemy` por solicitud.
Las dependencias de repositorio construidas para esa solicitud reutilizan la
misma instancia y reciben `uow.session`.

Al salir del contexto:

- si la operación terminó correctamente, la UoW ejecuta `commit()`;
- si ocurrió una excepción, ejecuta `rollback()`;
- en todos los casos, cierra la Session.

Este límite permite que los casos de uso coordinen repositorios sin conocer el
mecanismo concreto de transacción.

## Consecuencias positivas

- Existe una sola infraestructura de persistencia.
- Los límites transaccionales son explícitos y uniformes.
- Dominio y aplicación tienen menor acoplamiento con PostgreSQL y SQLAlchemy.
- Las entidades de dominio no quedan sujetas al ciclo de vida ORM.
- La traducción de constraints conocidas está localizada en infraestructura.
- Venta, Compra y stock pueden probarse con rollbacks completos ante fallos
  intermedios.
- Las consultas agregadas pueden evitar N+1 mediante estrategias explícitas.
- Los reportes reutilizan Session sin forzar repositorios o relationships que
  no representan necesidades del dominio.
- La metadata de SQLAlchemy habilita la futura incorporación de Alembic.

## Costos y compromisos

- La composición externa debe garantizar que los repositorios participantes
  reciban la misma Session.
- Los mappers agregan código explícito entre dominio y persistencia.
- Las consultas de proyección mantienen transformación manual hacia las
  respuestas requeridas.
- La semántica histórica se preservó incluso cuando existen alternativas más
  modernas, para evitar cambios funcionales durante la migración.

## Deudas técnicas conocidas

- Los importes monetarios usan `float` en dominio y aplicación en lugar de
  `Decimal`.
- Las actualizaciones de stock mantienen una condición de carrera potencial
  ante operaciones concurrentes.
- `UnidadDeTrabajoSQLAlchemy` ejecuta commit incluso al finalizar solicitudes
  de sólo lectura.
- Los casos de uso de Usuario utilizan bcrypt directamente, sin un contrato
  específico para hashing de contraseñas.
- No existe todavía una suite formal y permanente de pytest que cubra toda la
  persistencia y sus rollbacks.
- Alembic todavía no administra la evolución del esquema.

Estas deudas quedan fuera del alcance del cierre de la migración y deberán
abordarse como cambios separados.

## Validación

La arquitectura final fue validada con:

- CRUD de las entidades migradas;
- pruebas transaccionales de Venta y Compra;
- rollbacks después de modificaciones parciales de stock;
- constraints y cascades de PostgreSQL;
- Session compartida entre repositorios;
- consultas de reportes equivalentes a las consultas heredadas;
- generación de OpenAPI y arranque de Uvicorn;
- ejecución en un entorno limpio con psycopg 3 y sin psycopg2.

## Registro histórico

Los ADR anteriores no se reescriben. Describen decisiones, estados y diseños
transitorios válidos durante la migración, aunque no representen la
arquitectura vigente.
