from decimal import Decimal

import pytest

from dominio.entidades.categoria import Categoria
from dominio.entidades.producto import Producto
from dominio.excepciones import EntidadDuplicada, EntidadNoEncontrada
from infraestructura.repositorios.repositorio_categoria_sqlalchemy import (
    RepositorioCategoriaSQLAlchemy,
)
from infraestructura.repositorios.repositorio_producto_sqlalchemy import (
    RepositorioProductoSQLAlchemy,
)
from infraestructura.basedatos.modelos.producto_modelo import ProductoModelo


pytestmark = pytest.mark.integration


def _producto(codigo: str, id_categoria: int | None = None) -> Producto:
    return Producto(
        nombre="Agua mineral",
        precio_venta=Decimal("1800.50"),
        precio_compra=Decimal("1100.25"),
        stock=7,
        codigo_barras=codigo,
        id_categoria=id_categoria,
    )


def test_crear_y_leer_producto(db_session):
    repo_categoria = RepositorioCategoriaSQLAlchemy(db_session)
    categoria = repo_categoria.crear(Categoria(nombre="Bebidas"))
    repo = RepositorioProductoSQLAlchemy(db_session)

    creado = repo.crear(_producto("7790000000001", categoria.id_categoria))
    obtenido = repo.obtener_por_id(creado.id_producto)

    assert creado.id_producto is not None
    assert obtenido is not None
    assert obtenido.nombre == "Agua mineral"
    assert obtenido.codigo_barras == "7790000000001"
    assert obtenido.id_categoria == categoria.id_categoria
    assert obtenido.stock == 7


def test_codigo_barras_es_unico(db_session):
    repo = RepositorioProductoSQLAlchemy(db_session)
    repo.crear(_producto("7790000000002"))

    with pytest.raises(EntidadDuplicada, match="código de barras"):
        repo.crear(_producto("7790000000002"))


def test_categoria_debe_existir(db_session):
    repo = RepositorioProductoSQLAlchemy(db_session)

    with pytest.raises(EntidadNoEncontrada, match="categoría con id 999999"):
        repo.crear(_producto("7790000000003", id_categoria=999999))


def test_lectura_bloqueada_refresca_instancia_del_identity_map(
    test_session_factory,
):
    with test_session_factory() as session:
        repo = RepositorioProductoSQLAlchemy(session)
        creado = repo.crear(_producto("7790000000004"))
        session.commit()
        id_producto = creado.id_producto

    with test_session_factory() as session_obsoleta:
        modelo_obsoleto = session_obsoleta.get(ProductoModelo, id_producto)
        assert modelo_obsoleto.stock == 7

        with test_session_factory() as session_actualizadora:
            repo_actualizador = RepositorioProductoSQLAlchemy(
                session_actualizadora
            )
            repo_actualizador.obtener_para_modificar_stock([id_producto])
            repo_actualizador.actualizar_stocks({id_producto: 2})
            session_actualizadora.commit()

        repo_obsoleto = RepositorioProductoSQLAlchemy(session_obsoleta)
        bloqueados = repo_obsoleto.obtener_para_modificar_stock([id_producto])

        assert bloqueados[id_producto].stock == 2
        assert modelo_obsoleto.stock == 2
