# CRUDrugstore

Backend REST para la gestión de un drugstore: productos, stock, ventas,
compras, clientes, proveedores, categorías, medios de pago, usuarios,
reportes diarios y tickets térmicos.

La aplicación está construida con FastAPI y una arquitectura por capas. La
persistencia utiliza PostgreSQL mediante SQLAlchemy 2.x y psycopg 3.

## Stack tecnológico

| Área | Tecnología |
|---|---|
| API | FastAPI |
| Validación HTTP | Pydantic |
| Servidor ASGI | Uvicorn |
| Base de datos | PostgreSQL |
| Persistencia | SQLAlchemy 2.x |
| Driver PostgreSQL | psycopg 3 |
| Autenticación | JWT con PyJWT |
| Contraseñas | bcrypt |
| Configuración | python-dotenv |

## Arquitectura actual

```text
CRUDrugstore/
├── dominio/
│   ├── entidades/             # Entidades puras y reglas del dominio
│   ├── repositorios/          # Contratos abstractos de persistencia
│   ├── excepciones.py
│   └── validaciones.py
│
├── aplicacion/
│   └── casos_de_uso/          # Orquestación de reglas y repositorios
│
├── infraestructura/
│   ├── basedatos/
│   │   ├── modelos/           # Modelos ORM de SQLAlchemy
│   │   ├── mappers/           # Conversión dominio ↔ ORM
│   │   ├── configuracion.py   # URL postgresql+psycopg
│   │   ├── sesion.py          # Engine y SessionLocal
│   │   └── unidad_trabajo.py  # UnidadDeTrabajoSQLAlchemy
│   ├── repositorios/          # Implementaciones SQLAlchemy
│   ├── seguridad/             # Creación y validación de JWT
│   └── servicios/             # Reportes y tickets
│
├── api/
│   ├── rutas/                 # Endpoints FastAPI
│   ├── esquemas.py            # Requests y responses Pydantic
│   └── dependencias.py        # Composición y ciclo transaccional
│
└── main.py                    # Punto de entrada ASGI
```

### Separación entre dominio y ORM

- Las entidades de `dominio/entidades` son objetos Python puros y no
  dependen de SQLAlchemy.
- Los modelos ORM viven exclusivamente en
  `infraestructura/basedatos/modelos`.
- Los mappers de `infraestructura/basedatos/mappers` convierten entre ambos
  modelos.
- Los contratos de repositorio están en `dominio/repositorios`.
- Las implementaciones concretas están en `infraestructura/repositorios` y
  usan SQLAlchemy 2.x.
- La infraestructura traduce restricciones conocidas de PostgreSQL a
  excepciones del dominio; los errores desconocidos se propagan.

## Sesiones y transacciones

`api/dependencias.py` crea una `UnidadDeTrabajoSQLAlchemy` por solicitud.
FastAPI reutiliza esa dependencia para construir los repositorios requeridos,
por lo que todos reciben exactamente la misma `Session`.

```text
Solicitud HTTP
└── obtener_uow()
    └── UnidadDeTrabajoSQLAlchemy
        └── Session compartida
            ├── RepositorioVentaSQLAlchemy
            ├── RepositorioCompraSQLAlchemy
            ├── RepositorioProductoSQLAlchemy
            └── demás repositorios de la solicitud
```

La responsabilidad transaccional está distribuida así:

- Los repositorios reciben una `Session`.
- Los repositorios pueden ejecutar `flush()`.
- Los repositorios no hacen `commit()`, `rollback()` ni `close()`.
- `UnidadDeTrabajoSQLAlchemy` confirma la transacción al finalizar
  correctamente.
- Ante una excepción, la UoW revierte la transacción.
- La UoW siempre cierra la Session.
- Los casos de uso dependen de contratos de repositorio, no de la UoW.

### Venta y Compra

Venta y Compra son operaciones atómicas que combinan más de un repositorio:

- Crear una venta descuenta stock y registra cabecera y detalles.
- Eliminar una venta restituye stock y elimina físicamente la venta.
- Crear una compra suma stock y registra cabecera y detalles.
- Eliminar una compra descuenta el stock correspondiente y elimina
  físicamente la compra.

Los repositorios de Venta o Compra y Producto comparten la misma Session. Si
falla cualquier detalle, restricción o actualización intermedia, la
`UnidadDeTrabajoSQLAlchemy` revierte toda la operación.

## Reportes

Los reportes diarios son un servicio de consultas de infraestructura, no un
repositorio de entidades.

`infraestructura/servicios/servicio_reportes.py` recibe una `Session` y
ejecuta proyecciones con `select()`, columnas ORM y joins explícitos. El
servicio devuelve la estructura requerida por los schemas HTTP y por el
generador de tickets sin cargar agregados completos ni agregar relaciones ORM
específicas para reportes.

Los endpoints disponibles son:

| Método | Endpoint | Resultado |
|---|---|---|
| GET | `/api/reportes/ventas?fecha=YYYY-MM-DD` | Reporte JSON de ventas |
| GET | `/api/reportes/ventas/ticket?fecha=YYYY-MM-DD` | Ticket de ventas |
| GET | `/api/reportes/compras?fecha=YYYY-MM-DD` | Reporte JSON de compras |
| GET | `/api/reportes/compras/ticket?fecha=YYYY-MM-DD` | Ticket de compras |

Si no se envía `fecha`, se utiliza la fecha actual.

## Autenticación y autorización

- El login busca usuarios activos por email y valida la contraseña mediante el puerto `PasswordHasher`.
- La creación y recuperación de contraseñas utilizan el mismo puerto para generar hashes.
- La implementación concreta `BcryptPasswordHasher` vive en infraestructura y utiliza bcrypt.
- La implementación se inyecta en los casos de uso desde la composición de FastAPI.
- Las contraseñas nuevas deben tener al menos 6 caracteres.
- La API genera tokens JWT con PyJWT.
- Los tokens incluyen identificador de usuario, email, rol y vencimiento.
- Los roles actuales son `jefe` y `empleado`.
- La gestión de usuarios y los reportes requieren rol `jefe`.

## Módulos

| Módulo | Responsabilidad |
|---|---|
| Productos | Catálogo, precios, código de barras y stock |
| Ventas | Ventas, detalles, descuento de stock y tickets |
| Compras | Compras, detalles y aumento de stock |
| Clientes | Gestión de clientes y baja lógica |
| Proveedores | Gestión de proveedores y baja lógica |
| Categorías | Clasificación de productos |
| Medios de pago | Medios disponibles para ventas |
| Usuarios | Usuarios, roles, login y recuperación de contraseña |
| Reportes | Consultas diarias de ventas y compras |

## Requisitos

- Python 3.10 o superior
- PostgreSQL 14 o superior
- pip

La evolución del esquema se administra con Alembic. Para crear una base nueva,
configurá `ALEMBIC_DATABASE_URL` y ejecutá `alembic upgrade head`.

## Instalación

```bash
git clone <url-del-repo>
cd CRUDrugstore

python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Configuración

Crear un archivo `.env` en la raíz:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USUARIO=postgres
DB_PASSWORD=tu_password
DB_NOMBRE=drugstore

JWT_SECRETO=un_secreto_largo_y_seguro
JWT_ALGORITMO=HS256
JWT_EXPIRACION_MINUTOS=60
```

La conexión SQLAlchemy utiliza el dialecto `postgresql+psycopg`.

## Ejecución

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

También puede iniciarse con:

```bash
python main.py
```

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`

## Endpoints principales

| Área | Endpoint base |
|---|---|
| Autenticación | `/api/auth` |
| Categorías | `/api/categorias` |
| Usuarios | `/api/usuarios` |
| Clientes | `/api/clientes` |
| Proveedores | `/api/proveedores` |
| Medios de pago | `/api/medios-pago` |
| Productos | `/api/productos` |
| Ventas | `/api/ventas` |
| Compras | `/api/compras` |
| Reportes | `/api/reportes` |

La especificación completa y vigente está disponible en Swagger UI.

## Decisiones arquitectónicas

Las decisiones y el historial de la migración se encuentran en
`docs/adr/`. Los ADR anteriores se conservan como registro histórico,
incluidos los diseños transitorios que ya no representan el estado actual.

## Licencia

Este software es propiedad privada. Todos los derechos reservados.

### Dependencias directas principales

| Biblioteca | Uso |
|---|---|
| FastAPI | API REST e inyección de dependencias |
| Uvicorn | Servidor ASGI |
| SQLAlchemy | ORM, consultas y manejo de Session |
| psycopg | Driver PostgreSQL |
| PyJWT | Tokens JWT |
| bcrypt | Hash y validación de contraseñas |
| python-dotenv | Variables de entorno |
