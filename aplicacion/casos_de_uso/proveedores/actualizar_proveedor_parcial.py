from dominio.entidades.proveedor import Proveedor
from dominio.excepciones import EntidadNoEncontrada
from dominio.repositorios.repositorio_proveedor import RepositorioProveedor


class ActualizarProveedorParcial:
    def __init__(self, repositorio: RepositorioProveedor):
        self.repositorio = repositorio

    def ejecutar(
        self,
        id_proveedor: int,
        cambios: dict
    ) -> Proveedor:
        existente = self.repositorio.obtener_por_id(id_proveedor)
        if existente is None:
            raise EntidadNoEncontrada(
                f"No se encontró el proveedor con id {id_proveedor}."
            )
        
        if "razon_social" in cambios:
            existente.razon_social = cambios["razon_social"]
        if "cuit_cuil" in cambios:
            existente.cuit_cuil = cambios["cuit_cuil"]
        if "contacto_nombre" in cambios:
            existente.contacto_nombre = cambios["contacto_nombre"]
        if "telefono" in cambios:
            existente.telefono = cambios["telefono"]
        if "email" in cambios:
            existente.email = cambios["email"]
        
        existente.validar()

        actualizado = self.repositorio.actualizar(existente)

        if actualizado is None:
            raise EntidadNoEncontrada(
                f"No se encontró el proveedor con id {id_proveedor}."
            )

        return actualizado