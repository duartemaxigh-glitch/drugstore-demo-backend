"""Restricciones HTTP adicionales para la instancia pública de portfolio."""

from fastapi.responses import JSONResponse

from infraestructura.basedatos import configuracion


MUTACIONES_PERMITIDAS = frozenset({
    ("POST", "/api/auth/login"),
    ("POST", "/api/ventas"),
    ("POST", "/api/compras"),
})
MENSAJE_BLOQUEO = "Esta operación no está disponible en la demo pública."


def operacion_bloqueada(metodo: str, path: str) -> bool:
    if not configuracion.PUBLIC_DEMO_MODE:
        return False

    if metodo == "OPTIONS":
        return False

    ruta = path.rstrip("/") or "/"
    if ruta == "/api/usuarios" or ruta.startswith("/api/usuarios/"):
        return True

    if metodo in {"GET", "HEAD"}:
        return False

    return (metodo, ruta) not in MUTACIONES_PERMITIDAS


class PoliticaDemoPublicaMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and operacion_bloqueada(
            scope["method"], scope["path"]
        ):
            respuesta = JSONResponse({"detail": MENSAJE_BLOQUEO}, status_code=403)
            await respuesta(scope, receive, send)
            return
        await self.app(scope, receive, send)
