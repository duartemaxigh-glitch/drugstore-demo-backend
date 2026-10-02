import pytest

from dominio.entidades.cliente import Cliente
from infraestructura.basedatos.modelos.cliente_modelo import ClienteModelo
from infraestructura.repositorios.repositorio_cliente_sqlalchemy import (
    RepositorioClienteSQLAlchemy,
)


pytestmark = pytest.mark.integration


def test_baja_logica_y_lectura_excluye_inactivos(db_session):
    repo = RepositorioClienteSQLAlchemy(db_session)
    cliente = repo.crear(
        Cliente(nombre="Ana", apellido="Pérez", dni="12345678")
    )

    assert repo.eliminar(cliente.id_cliente) is True
    assert repo.obtener_por_id(cliente.id_cliente) is None

    modelo = db_session.get(ClienteModelo, cliente.id_cliente)
    assert modelo is not None
    assert modelo.activo is False
