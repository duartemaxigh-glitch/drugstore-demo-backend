# Actualización 024 — Integración post-rebase y arranque validado

**Fecha:** 2026-09-23  
**Estado:** arranque validado; faltan pruebas funcionales post-rebase

## Contexto

`rama-maxi` fue rebasada sobre `origin/PostgreSQL_version`, quedando la migración SQLAlchemy aplicada encima de la versión más reciente del proyecto PostgreSQL.

Durante la integración se resolvieron conflictos en:

- `api/dependencias.py`
- `api/rutas/rutas_proveedores.py`
- `aplicacion/casos_de_uso/proveedores/actualizar_proveedor.py`
- `dominio/repositorios/repositorio_usuario.py`
- `infraestructura/repositorios/repositorio_usuario.py`

La composición actual es transitoria:

- Categoría, Usuario, Medio de Pago y Proveedor usan SQLAlchemy.
- Cliente, Producto, Venta y Compra continúan usando repositorios PostgreSQL directos.
- Coexisten temporalmente `psycopg2` y `psycopg` 3.
- Coexisten temporalmente `UnidadDeTrabajoPostgreSQL` y `UnidadDeTrabajoSQLAlchemy`.

## Problemas detectados y corregidos

1. Faltaba `psycopg2` en el entorno virtual.
2. Quedaron marcadores de conflicto de Git dentro de `dominio/repositorios/repositorio_usuario.py`.
3. Se actualizaron las dependencias necesarias para la coexistencia de persistencia directa y SQLAlchemy.

## Resultado

La aplicación vuelve a iniciar con Uvicorn sin errores de importación o sintaxis.

Esto valida el ensamblado básico del proyecto, pero no confirma todavía el comportamiento funcional de los casos de uso.

## Próxima validación

Ejecutar pruebas funcionales post-rebase, especialmente:

1. autenticación/login;
2. recuperación/cambio de contraseña;
3. CRUD de categorías;
4. CRUD de medios de pago;
5. PUT/PATCH/DELETE de proveedores;
6. smoke tests de las áreas todavía basadas en PostgreSQL directo.

No hacer push de la rama reescrita hasta completar estas comprobaciones.
