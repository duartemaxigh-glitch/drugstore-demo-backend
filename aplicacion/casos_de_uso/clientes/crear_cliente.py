# ============================================================
# Caso de Uso: Crear Cliente
# ============================================================

from __future__ import annotations

from dominio.entidades.cliente import Cliente
from dominio.repositorios.repositorio_cliente import RepositorioCliente


class CrearCliente:
    def __init__(self, repositorio: RepositorioCliente):
        self.repositorio = repositorio

    def ejecutar(
        self,
        apellido: str | None = None,
        nombre: str | None = None,
        dni: str | None = None,
        cuit: str | None = None,
        telefono: str | None = None,
    ) -> Cliente:
        cliente = Cliente(
            apellido=apellido,
            nombre=nombre,
            dni=dni,
            cuit=cuit,
            telefono=telefono,
        )
        cliente.validar()
        return self.repositorio.crear(cliente)
