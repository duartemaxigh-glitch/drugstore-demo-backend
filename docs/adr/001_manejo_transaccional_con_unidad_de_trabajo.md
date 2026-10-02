# ADR-001: Manejo transaccional con Unidad de Trabajo

**Estado:** Aceptado  
**Fecha:** septiembre de 2026

## Contexto

La implementación original de persistencia utilizaba PyMySQL con:

- una conexión nueva por método de repositorio;
- `autocommit=True`;
- cierre de conexión dentro de cada método.

Esto hacía que cada llamada al repositorio quedara aislada transaccionalmente.

Un caso de uso que necesitara coordinar dos repositorios no podía garantizar fácilmente que ambas operaciones pertenecieran a la misma transacción.

## Decisión

Se adopta una Unidad de Trabajo basada en una `Session` de SQLAlchemy.

La UoW:

- crea la `Session`;
- mantiene su ciclo de vida;
- realiza `commit` si la operación finaliza correctamente;
- realiza `rollback` si sale una excepción;
- cierra la `Session`.

Los repositorios:

- reciben una `Session`;
- no crean su propia sesión;
- no realizan `commit`;
- no realizan `rollback`;
- no cierran la sesión;
- pueden realizar `flush`.

Los casos de uso:

- trabajan con interfaces de repositorio;
- no controlan directamente la transacción.

La composición externa construye repositorios usando:

```python
RepositorioXSQLAlchemy(uow.session)
```

La UoW no conoce repositorios concretos.

## Implementación base

```python
class UnidadDeTrabajoSQLAlchemy:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                try:
                    self.session.commit()
                except Exception:
                    self.session.rollback()
                    raise
            else:
                self.session.rollback()
        finally:
            self.session.close()
```

## Integración con FastAPI

```python
def obtener_uow():
    with UnidadDeTrabajoSQLAlchemy(SessionLocal) as uow:
        yield uow
```

Los repositorios dependen de esa misma UoW:

```python
def obtener_repo_categoria(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
):
    return RepositorioCategoriaSQLAlchemy(uow.session)
```

## Consecuencias

### Positivas

- Un caso de uso puede utilizar varios repositorios dentro de la misma Session.
- La transacción representa la unidad de negocio y no una llamada aislada de persistencia.
- Los repositorios dejan de controlar la vida de la conexión/transacción.
- Se elimina el patrón de autocommit por método.
- Se facilita el rollback coordinado.

### Costos

- La composición externa debe asegurar que los repositorios de una operación compartan la misma UoW.
- Las excepciones deben salir del contexto de la UoW para que `__exit__` pueda detectarlas.
- La política de commit para operaciones de sólo lectura deberá revisarse más adelante.

## Interfaces descartadas por ahora

No se crean abstracciones como:

- `ISession`;
- `IEngine`;
- `IBase`;
- `IUnitOfWork`.

La razón es que actualmente ninguna capa interna necesita depender de esas capacidades mediante una abstracción.

Se evita introducir interfaces únicamente “por si acaso”.
