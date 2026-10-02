# ============================================================
# Ruta: Imprimir ticket en impresora térmica
# ============================================================
# Recibe el texto del ticket y lo envía directamente a la
# impresora térmica usando comandos ESC/POS.
# ============================================================

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/imprimir", tags=["Impresora"])

DISPOSITIVO = "/dev/usb/lp2"

# Comandos ESC/POS
INIT = b'\x1b\x40'
ALIGN_LEFT = b'\x1b\x61\x00'
FONT_NORMAL = b'\x1b\x21\x00'
FEED_5 = b'\x1b\x64\x05'
CUT = b'\x1d\x56\x01'


class ImprimirRequest(BaseModel):
    texto: str


@router.post("")
def imprimir(req: ImprimirRequest):
    if not req.texto:
        raise HTTPException(status_code=400, detail="Texto vacío.")

    try:
        datos = INIT + ALIGN_LEFT + FONT_NORMAL + req.texto.encode('ascii', errors='replace') + FEED_5 + CUT
        with open(DISPOSITIVO, 'wb') as printer:
            printer.write(datos)
            printer.flush()
        return JSONResponse(content={"mensaje": "Ticket impreso correctamente."})
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Impresora no encontrada.")
    except PermissionError:
        raise HTTPException(status_code=500, detail="Sin permisos para acceder a la impresora.")
    except UnicodeEncodeError:
        raise HTTPException(status_code=400, detail="El texto contiene caracteres no válidos. Solo se permite ASCII.")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error de E/S en la impresora: {e}")
