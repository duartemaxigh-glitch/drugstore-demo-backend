# ============================================================
# Caso de Uso: Actualizar Proveedor
# ============================================================

from __future__ import annotations

from dominio.entidades.proveedor import Proveedor
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_proveedor import RepositorioProveedor


class ActualizarProveedor:
    def __init__(self, repositorio: RepositorioProveedor):
        self.repositorio = repositorio

    def ejecutar(
        self,
        id_proveedor: int,
        razon_social: str,
        cuit_cuil: str | None,
        contacto_nombre: str | None,
        telefono: str | None,
        email: str | None,
    ) -> Proveedor:
        existente = self.repositorio.obtener_por_id(id_proveedor)
        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el proveedor con id {id_proveedor}."
            )

        proveedor = Proveedor(
            id_proveedor=id_proveedor,
            razon_social=razon_social,
            cuit_cuil=cuit_cuil,
            contacto_nombre=contacto_nombre,
            telefono=telefono,
            email=email,
        )
        proveedor.validar()

        actualizado = self.repositorio.actualizar(proveedor)

        if actualizado is None:
            raise EntidadNoEncontrada(
                f"No se encontró el proveedor con id {id_proveedor}."
            )

        return actualizado
