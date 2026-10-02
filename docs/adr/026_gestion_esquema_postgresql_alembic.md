# ADR-026: Gestión del esquema PostgreSQL con Alembic

**Estado:** Aceptado
**Fecha:** 2026-09-25

## Contexto

El proyecto ya utilizaba una base PostgreSQL con tablas, constraints, índices,
secuencias y datos antes de incorporar una herramienta formal de migraciones.
Por lo tanto, introducir Alembic no podía comenzar ejecutando nuevamente el DDL
sobre la base histórica.

Antes de crear la baseline se alineó `Base.metadata` con el esquema PostgreSQL
real y se auditó la equivalencia de tablas, columnas, tipos, nulabilidad,
claves foráneas, cascades, restricciones únicas e índices. Una vez alcanzada
esa equivalencia, se necesitaba registrar el estado existente y disponer de un
historial reproducible para la evolución futura del esquema.

## Decisión

- Alembic es el mecanismo oficial para versionar y aplicar cambios de esquema.
- La revisión `eb66ff3b2e62` es la baseline completa del esquema inicial.
- Las bases nuevas se construyen ejecutando `alembic upgrade head` desde una
  base vacía.
- La base histórica de desarrollo se incorporó al historial mediante
  `alembic stamp eb66ff3b2e62`, después de verificar que su esquema era
  equivalente a la metadata y a la baseline.
- El `stamp` sólo registró la revisión en `alembic_version`: no ejecutó el DDL
  contenido en la baseline ni modificó las tablas de aplicación.
- Las ejecuciones normales de Alembic obtienen su destino exclusivamente de
  `ALEMBIC_DATABASE_URL`. No se utiliza la URL de la aplicación como fallback.
- Toda revisión generada mediante `--autogenerate` debe inspeccionarse
  manualmente antes de aplicarla. Autogenerate ayuda a detectar diferencias,
  pero no reemplaza la revisión del significado, el orden y la seguridad del
  cambio.
- Los tests de integración construyen su schema temporal con
  `alembic upgrade head`; no utilizan `Base.metadata.create_all()`.
- Pytest crea un schema PostgreSQL aleatorio y entrega a Alembic la misma
  `Connection` ya aislada mediante `search_path`. La tabla
  `alembic_version` se configura dentro de ese schema, de modo que las
  ejecuciones no comparten estado ni crean objetos en `public`.

## Operación esperada

Para una base nueva:

1. crear una base PostgreSQL vacía;
2. configurar explícitamente `ALEMBIC_DATABASE_URL` con el dialecto
   `postgresql+psycopg`;
3. ejecutar `alembic upgrade head`.

Para una base existente que todavía no esté versionada, no se debe ejecutar
`stamp` de manera automática. Primero debe compararse el esquema completo con
la revisión que se pretende registrar. Un `stamp` declara equivalencia, pero no
la comprueba ni corrige diferencias.

## Consecuencias positivas

- El esquema posee un historial reproducible y revisable.
- Una base vacía puede construirse desde cero sin scripts externos.
- `alembic check` y autogenerate permiten detectar drift entre los modelos y
  la base.
- Los tests de integración ejercitan el mismo historial de migraciones que se
  utiliza fuera de pytest.
- El aislamiento por schema evita que los tests modifiquen `public` o
  compartan `alembic_version`.

## Costos y riesgos

- Las migraciones y los modelos ORM deben mantenerse sincronizados.
- Una revisión autogenerada puede contener operaciones incompletas,
  destructivas o semánticamente incorrectas si se aplica sin revisión manual.
- Ejecutar Alembic con una URL equivocada puede afectar otra base; por eso la
  URL de migración es explícita y no tiene fallback.
- Aplicar `stamp` a un esquema no equivalente puede ocultar drift y dejar una
  base declarada en una revisión que en realidad no representa.
- Modificar el esquema manualmente deja el historial incompleto y no es un
  flujo normal aceptado. Toda evolución debe expresarse mediante una nueva
  revisión de Alembic.

## Alcance

Esta decisión describe el mecanismo de evolución del esquema y su uso en
tests. No convierte configuraciones accidentales de una máquina, nombres de
bases locales ni rutas particulares en decisiones arquitectónicas.
