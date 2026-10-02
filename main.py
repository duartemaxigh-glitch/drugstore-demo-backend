# ============================================================
# main.py — Punto de entrada de la aplicación
# ============================================================
# Aquí se crea la app de FastAPI, se registran todas las rutas
# y se configura CORS para que el frontend (Next.js) pueda
# comunicarse con la API.
#
# Para arrancar el servidor:
#   python main.py
#   (o: uvicorn main:app --reload)
#
# Documentación automática (Swagger):
#   http://localhost:8000/docs
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos todas las rutas
from api.rutas.rutas_auth import router as router_auth
from api.rutas.rutas_categorias import router as router_categorias
from api.rutas.rutas_clientes import router as router_clientes
from api.rutas.rutas_compras import router as router_compras
from api.rutas.rutas_imprimir import router as router_imprimir
from api.rutas.rutas_medios_pago import router as router_medios_pago
from api.rutas.rutas_productos import router as router_productos
from api.rutas.rutas_proveedores import router as router_proveedores
from api.rutas.rutas_reportes import router as router_reportes
from api.rutas.rutas_usuarios import router as router_usuarios
from api.rutas.rutas_ventas import router as router_ventas

# Creamos la aplicación FastAPI
app = FastAPI(
    title="CRUDrugstore API",
    description="API REST para gestión de un drugstore. Clean Architecture con Python.",
    version="1.0.0",
)

# Configuramos CORS para que Next.js pueda hacer peticiones
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5165"],  # URL del frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],     # Permitir todos los métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"],     # Permitir todos los headers (incluido Authorization)
)

# Registramos todas las rutas con prefijo /api
app.include_router(router_auth, prefix="/api")
app.include_router(router_categorias, prefix="/api")
app.include_router(router_usuarios, prefix="/api")
app.include_router(router_clientes, prefix="/api")
app.include_router(router_proveedores, prefix="/api")
app.include_router(router_medios_pago, prefix="/api")
app.include_router(router_productos, prefix="/api")
app.include_router(router_ventas, prefix="/api")
app.include_router(router_compras, prefix="/api")
app.include_router(router_reportes, prefix="/api")
app.include_router(router_imprimir, prefix="/api")


@app.get("/")
def raiz():
    return {"mensaje": "CRUDrugstore API funcionando correctamente"}


# Si ejecutás este archivo directamente, arranca el servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
