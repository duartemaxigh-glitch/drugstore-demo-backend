# Refactor de persistencia: PyMySQL/MySQL → SQLAlchemy/PostgreSQL

**Proyecto:** CRUDrugstore  
**Fecha de inicio documentada:** septiembre de 2026  
**Estado:** en progreso

## 1. Objetivo

Migrar la capa de persistencia del proyecto desde PyMySQL/MySQL hacia SQLAlchemy 2.x con PostgreSQL, manteniendo la arquitectura por capas existente y evitando mezclar la migración tecnológica con refactors de dominio no necesarios.

La migración se realiza de forma incremental, verificando cada repositorio y cada flujo antes de continuar.

---

## 2. Estado inicial

La infraestructura original utilizaba:

- PyMySQL.
- MySQL.
- Una conexión nueva por operación de repositorio.
- `autocommit=True`.
- SQL escrito manualmente.
- Manejo de duplicados inspeccionando el texto de excepciones.
- Repositorios concretos MySQL consumidos mediante interfaces del dominio.

Ejemplo de conexión original:

```python
def obtener_conexion():
    conexion = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USUARIO', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NOMBRE', 'drugstore'),
        cursorclass=DictCursor,
        autocommit=True,
    )
    return conexion
```

### Problemas detectados

1. Cada método de repositorio administraba su propia conexión.
2. Las operaciones de un mismo caso de uso no podían compartir fácilmente una transacción.
3. `autocommit=True` impedía modelar la transacción como unidad de negocio.
4. El manejo de errores dependía de mensajes de texto específicos del proveedor.
5. La infraestructura de persistencia quedaba fuertemente acoplada a PyMySQL/MySQL.

---

## 3. Stack elegido

La nueva pila de persistencia es:

```text
Python
  ↓
SQLAlchemy 2.x
  ↓
psycopg
  ↓
PostgreSQL
```

Se decidió usar SQLAlchemy en modo síncrono durante esta migración.

También se incorporará Alembic para evolución de esquema. `Base.metadata.create_all()` no será el mecanismo normal de migración del esquema.

---

## 4. Configuración de SQLAlchemy

### `infraestructura/basedatos/configuracion.py`

```python
import os
from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv(override=True)

db_host = os.getenv("DB_HOST", "localhost")
db_port = int(os.getenv("DB_PORT", "5432"))
db_user = os.getenv("DB_USUARIO", "postgres")
db_password = os.getenv("DB_PASSWORD", "")
db_name = os.getenv("DB_NOMBRE", "drugstore")

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=db_user,
    password=db_password,
    host=db_host,
    port=db_port,
    database=db_name,
)
```

Se usa `URL.create()` para evitar problemas de escape con caracteres especiales en credenciales.

### `infraestructura/basedatos/sesion.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infraestructura.basedatos.configuracion import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)
```

Decisiones:

- `pool_pre_ping=True`: valida conexiones recuperadas del pool.
- `autoflush=False`: el `flush` se vuelve más explícito.
- `expire_on_commit=False`: los atributos ya cargados siguen disponibles después del commit.

### `infraestructura/basedatos/base.py`

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

`Base.metadata` funciona como registro de tablas, columnas y constraints ORM y será relevante para Alembic.

---

## 5. Separación entre dominio y ORM

Se decidió no convertir las entidades del dominio directamente en modelos SQLAlchemy.

Ejemplo:

```text
dominio.entidades.Categoria
             ↕ mapper
infraestructura.CategoriaModelo
```

Responsabilidades:

- Entidad de dominio: reglas y estado del negocio.
- Modelo ORM: representación de persistencia.
- Mapper: conversión entre ambos.

Esto evita que el dominio dependa de SQLAlchemy.

Consecuencia asumida: el dirty checking de SQLAlchemy opera sobre modelos ORM persistentes, no sobre entidades de dominio desacopladas.

La decisión completa está registrada en `docs/adr/002_separacion_entidades_modelos_orm.md`.

---

## 6. Unidad de Trabajo y transacciones

Se reemplazó el modelo de autocommit por una Unidad de Trabajo basada en una `Session` compartida.

Implementación acordada:

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

Responsabilidades:

- Repository: `add`, consultas, asignaciones y `flush`.
- UoW: `commit`, `rollback`, `close`.
- Caso de uso: reglas de aplicación.
- API/composición: construcción de dependencias.

No se creó una interfaz de UoW porque ninguna capa interna depende actualmente de una abstracción de UoW.

La decisión completa está registrada en `docs/adr/001_manejo_transaccional_con_unidad_de_trabajo.md`.

---

## 7. Integración con FastAPI

Patrón acordado:

```python
def obtener_uow():
    with UnidadDeTrabajoSQLAlchemy(SessionLocal) as uow:
        yield uow
```

Y los repositorios reciben la misma UoW:

```python
def obtener_repo_categoria(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
) -> RepositorioCategoria:
    return RepositorioCategoriaSQLAlchemy(uow.session)
```

```python
def obtener_repo_usuario(
    uow: UnidadDeTrabajoSQLAlchemy = Depends(obtener_uow),
) -> RepositorioUsuario:
    return RepositorioUsuarioSQLAlchemy(uow.session)
```

El endpoint no realiza `commit()` ni `rollback()`.

Importante: las excepciones deben salir del `with` para que `__exit__` pueda detectar el error y hacer rollback.

---

# 8. Migración de Categoría

## 8.1 Modelo ORM

```python
class CategoriaModelo(Base):
    __tablename__ = "categorias"

    id_categoria: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )
```

## 8.2 Mapper

```python
def a_dominio(modelo: CategoriaModelo) -> Categoria:
    return Categoria(
        id_categoria=modelo.id_categoria,
        nombre=modelo.nombre,
    )

def nuevo_modelo(categoria: Categoria) -> CategoriaModelo:
    return CategoriaModelo(
        nombre=categoria.nombre,
    )
```

## 8.3 Repository

El repositorio SQLAlchemy:

- usa `session.add()` para altas;
- usa `session.flush()` para enviar cambios sin confirmar la transacción;
- usa `session.get()` para búsquedas por PK;
- usa `select()` + `scalars()` para listados;
- utiliza dirty checking para actualización;
- traduce `UniqueViolation` a `EntidadDuplicada`;
- no realiza `commit`, `rollback` ni `close`.

## 8.4 Pruebas realizadas

Se verificaron manualmente:

- creación correcta;
- duplicado de nombre;
- obtención por ID;
- listado;
- actualización;
- actualización a nombre duplicado;
- eliminación;
- eliminación de ID inexistente.

Todos los casos funcionaron contra PostgreSQL.

### Observación sobre secuencias

Durante las pruebas se observaron saltos de IDs después de inserciones fallidas.

Esto es comportamiento normal de PostgreSQL:

> Un rollback revierte el `INSERT`, pero no devuelve valores ya consumidos por una secuencia.

Por lo tanto, una PK autogenerada no debe asumirse contigua.

---

# 9. Migración de Usuario

## 9.1 Modelo ORM

Se creó `UsuarioModelo` con equivalencia al esquema PostgreSQL.

Puntos revisados:

- `password_hash` debe escribirse correctamente.
- `telefono` puede ser nullable.
- `activo` usa un `server_default` SQL válido, no un `bool` Python.
- `rol` mantiene la restricción de valores permitidos.

Se detectó una diferencia de nombre entre la constraint real:

```text
usuarios_rol_check
```

y un nombre utilizado inicialmente en metadata SQLAlchemy.

Debe alinearse antes de depender de Alembic autogenerate.

## 9.2 Mapper

El mapper debe conservar todos los campos relevantes, incluido `activo`.

Un error detectado durante la migración fue omitir `activo`, lo que habría provocado que un usuario inactivo se reconstruyera con el valor por defecto `True` del dominio.

Versión conceptual:

```python
def a_dominio(modelo: UsuarioModelo) -> Usuario:
    return Usuario(
        id_usuario=modelo.id_usuario,
        apellido=modelo.apellido,
        nombre=modelo.nombre,
        dni=modelo.dni,
        telefono=modelo.telefono,
        email=modelo.email,
        password_hash=modelo.password_hash,
        rol=modelo.rol,
        activo=modelo.activo,
    )
```

También se agregó `nuevo_modelo(usuario)` para creación.

---

## 9.3 Restricciones UNIQUE

La tabla PostgreSQL confirmó las constraints:

```text
usuarios_dni_key
usuarios_email_key
```

El repository ya no inspecciona texto de errores. Se utiliza:

```python
e.orig.diag.constraint_name
```

para distinguir qué restricción falló.

Ejemplo:

```python
except IntegrityError as e:
    if isinstance(e.orig, UniqueViolation):
        constraint = e.orig.diag.constraint_name

        if constraint == "usuarios_email_key":
            raise EntidadDuplicada(
                f"Ya existe un usuario con email '{usuario.email}'."
            ) from e

        if constraint == "usuarios_dni_key":
            raise EntidadDuplicada(
                f"Ya existe un usuario con DNI '{usuario.dni}'."
            ) from e

    raise
```

Pruebas realizadas:

- creación válida;
- email duplicado;
- DNI duplicado.

Los tres casos funcionaron correctamente.

---

## 9.4 Semántica de baja lógica

El repositorio MySQL original ya utilizaba baja lógica:

```sql
UPDATE usuarios
SET activo = FALSE
WHERE id_usuario = %s
```

Durante la migración se confirmó que:

- `obtener_por_id()` filtra `activo = TRUE`;
- `obtener_por_email()` filtra `activo = TRUE`;
- `obtener_todos()` filtra `activo = TRUE`;
- `actualizar()` no agregaba filtro por `activo`;
- `eliminar()` tampoco agregaba filtro por `activo`, sino que ejecutaba la baja lógica por ID.

La implementación SQLAlchemy mantiene esta semántica para no cambiar comportamiento durante la migración.

### Nota

El nombre `eliminar()` representa en realidad una desactivación. Se conserva por ahora para no mezclar la migración de persistencia con un refactor de API de dominio.

---

## 9.5 Actualización de Usuario

Se detectó que el `UPDATE` MySQL original modificaba únicamente:

```text
apellido
nombre
dni
telefono
email
rol
```

No modificaba:

```text
password_hash
activo
```

La implementación SQLAlchemy conserva exactamente ese comportamiento.

También reutiliza el mismo mecanismo de `constraint_name` para diferenciar duplicados de email y DNI.

---

## 9.6 Repository completo

`RepositorioUsuarioSQLAlchemy` ya implementa completamente el contrato de `RepositorioUsuario`.

Métodos migrados:

- `crear()`
- `obtener_por_id()`
- `obtener_por_email()`
- `obtener_todos()`
- `actualizar()`
- `eliminar()`

La clase volvió a heredar de:

```python
RepositorioUsuario
```

y puede instanciarse correctamente, lo que confirma que cumple el contrato abstracto.

---

# 10. Migración del flujo mínimo de autenticación

El flujo de login fue probado contra PostgreSQL:

```text
POST /auth/login
    ↓
FastAPI
    ↓
RepositorioUsuarioSQLAlchemy
    ↓
SQLAlchemy Session
    ↓
psycopg
    ↓
PostgreSQL
```

`LoginUsuario` obtiene el usuario mediante `obtener_por_email()` y verifica la contraseña usando bcrypt.

Se probaron satisfactoriamente:

1. credenciales correctas;
2. contraseña incorrecta;
3. email inexistente;
4. usuario inactivo.

Los casos inválidos mantienen la respuesta:

```text
Email o contraseña incorrectos.
```

con `401 Unauthorized`.

Con esto quedó validado el camino mínimo de autenticación necesario para continuar probando endpoints protegidos.

---

# 11. Decisiones pendientes / deuda detectada

Estas cuestiones fueron detectadas pero deliberadamente no se mezclaron todavía con la migración:

1. Evaluar si las invariantes de entidades deben ejecutarse desde el constructor en lugar de depender de llamadas explícitas a `validar()`.
2. Revisar si `eliminar()` debería llamarse conceptualmente `desactivar()` para Usuario.
3. Revisar en el futuro la política de commit de UoW para operaciones puramente de lectura.
4. Incorporar Alembic y alinear nombres de constraints entre metadata y PostgreSQL.
5. Evaluar abstracción de hashing/verificación de contraseñas para evitar que los casos de uso dependan directamente de bcrypt.
6. Revisar posibles consultas dobles en casos de uso de actualización/eliminación y su tratamiento frente a condiciones de carrera.

---

# 12. Próximo paso

Probar el CRUD de Categoría a través de FastAPI usando autenticación real y la nueva composición de UoW + repositories SQLAlchemy.

Esto validará el recorrido completo:

```text
HTTP
↓
FastAPI
↓
Caso de uso
↓
Repository
↓
Session SQLAlchemy
↓
PostgreSQL
↓
UoW commit / rollback
```

---

# 13. Prueba de integración HTTP de Categoría

Se inició la validación del CRUD de Categoría a través de FastAPI usando autenticación real y la nueva composición de SQLAlchemy + UoW.

## 13.1 Creación autenticada

Se ejecutó:

```http
POST /categorias
```

con un token válido y el cuerpo:

```json
{
  "nombre": "Perfumería"
}
```

Resultado:

```http
201 Created
```

```json
{
  "id_categoria": 5,
  "nombre": "Perfumería"
}
```

Esta prueba confirma el recorrido completo:

```text
HTTP autenticado
↓
FastAPI
↓
obtener_usuario_actual
↓
RepositorioUsuarioSQLAlchemy
↓
PostgreSQL
↓
CrearCategoria
↓
RepositorioCategoriaSQLAlchemy
↓
Session SQLAlchemy
↓
flush()
↓
UoW
↓
commit()
```

Con esto queda validada la creación de Categoría desde la capa HTTP usando PostgreSQL y SQLAlchemy.

El siguiente caso a verificar es un nombre duplicado para comprobar la traducción a `EntidadDuplicada`, la respuesta HTTP `409 Conflict` y el rollback de la UoW dentro de una request real.

