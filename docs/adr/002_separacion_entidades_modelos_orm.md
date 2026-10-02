# ADR-002: Separación entre entidades de dominio y modelos ORM

**Estado:** Aceptado  
**Fecha:** septiembre de 2026

## Contexto

Durante la migración a SQLAlchemy surgió la posibilidad de convertir directamente las entidades de dominio existentes en modelos declarativos SQLAlchemy.

Ejemplo:

```text
Categoria
Usuario
```

podrían haber heredado o incorporado directamente metadata ORM.

Sin embargo, eso habría introducido una dependencia de SQLAlchemy dentro de la capa de dominio.

## Decisión

Se mantienen separados:

```text
Entidad de dominio
        ↕ mapper
Modelo ORM de infraestructura
```

Ejemplos:

```text
Categoria        ↔ CategoriaModelo
Usuario          ↔ UsuarioModelo
```

Los modelos ORM viven en infraestructura.

Los mappers también viven en infraestructura y son responsables de:

- reconstruir entidades de dominio a partir de modelos ORM;
- construir modelos ORM nuevos a partir de entidades de dominio.

## Motivos

La capa de dominio no necesita conocer:

- SQLAlchemy;
- `Mapped`;
- `mapped_column`;
- `relationship`;
- `Session`;
- detalles del esquema relacional.

De esta manera, las entidades continúan representando conceptos de negocio y no filas ORM.

## Consecuencias

### Positivas

- El dominio permanece desacoplado de SQLAlchemy.
- La infraestructura puede cambiar sin modificar las entidades de negocio.
- Los modelos de persistencia pueden reflejar detalles de PostgreSQL sin contaminar el dominio.
- El límite arquitectónico queda explícito mediante mappers.

### Costos

- Hay duplicación estructural entre entidad y modelo ORM.
- Se necesita código de mapeo explícito.
- Una entidad de dominio reconstruida desde un modelo queda desacoplada de la `Session`.
- El dirty checking de SQLAlchemy no opera directamente sobre la entidad de dominio.

## Dirty checking

La pérdida de dirty checking directo sobre entidades de dominio se acepta como costo del desacoplamiento.

La estrategia elegida para actualizaciones es:

1. el repository recibe la entidad de dominio;
2. obtiene el modelo ORM persistente mediante la `Session`;
3. copia al modelo sólo los campos que corresponden actualizar;
4. SQLAlchemy detecta cambios en el modelo persistente;
5. `flush()` envía el `UPDATE`;
6. el mapper vuelve a construir la entidad de dominio resultante.

Ejemplo conceptual:

```text
Usuario dominio
    ↓
session.get(UsuarioModelo)
    ↓
modelo.email = usuario.email
modelo.rol = usuario.rol
    ↓
dirty checking
    ↓
flush()
    ↓
a_dominio(modelo)
```

## Alcance

Esta decisión aplica a las entidades migradas durante este refactor y sirve como patrón para las siguientes.
