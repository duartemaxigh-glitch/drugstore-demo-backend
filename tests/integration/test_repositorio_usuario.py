import pytest
from sqlalchemy import event

from infraestructura.basedatos.modelos.usuario_modelo import UsuarioModelo
from infraestructura.repositorios.repositorio_usuario_sqlalchemy import (
    RepositorioUsuarioSQLAlchemy,
)


pytestmark = pytest.mark.integration


def _crear_usuario(
    test_session_factory,
    *,
    dni: str,
    email: str,
    activo: bool = True,
    password_hash: str = "hash-anterior",
) -> int:
    with test_session_factory() as session:
        modelo = UsuarioModelo(
            apellido="Perez",
            nombre="Ana",
            dni=dni,
            email=email,
            password_hash=password_hash,
            rol="empleado",
            activo=activo,
        )
        session.add(modelo)
        session.commit()
        return modelo.id_usuario


def test_actualizar_password_de_usuario_activo_devuelve_true_y_persiste(
    test_session_factory,
):
    id_usuario = _crear_usuario(
        test_session_factory,
        dni="81000001",
        email="activo@example.com",
    )

    with test_session_factory() as session:
        repo = RepositorioUsuarioSQLAlchemy(session)
        sentencias: list[str] = []

        def registrar_sentencia(
            _conn,
            _cursor,
            statement,
            _parameters,
            _context,
            _executemany,
        ):
            sentencias.append(statement)

        engine = session.get_bind()
        event.listen(engine, "before_cursor_execute", registrar_sentencia)
        try:
            assert repo.actualizar_password(id_usuario, "hash-nuevo") is True
        finally:
            event.remove(
                engine,
                "before_cursor_execute",
                registrar_sentencia,
            )

        assert len(sentencias) == 1
        sql_emitido = " ".join(sentencias[0].split())
        assert sql_emitido.startswith("UPDATE usuarios SET password_hash=")
        assert "usuarios.id_usuario =" in sql_emitido
        assert "usuarios.activo IS true" in sql_emitido
        assert sql_emitido.endswith("RETURNING usuarios.id_usuario")
        session.commit()

    with test_session_factory() as session:
        modelo = session.get(UsuarioModelo, id_usuario)
        assert modelo is not None
        assert modelo.password_hash == "hash-nuevo"


def test_actualizar_password_de_id_inexistente_devuelve_false(
    test_session_factory,
):
    with test_session_factory() as session:
        repo = RepositorioUsuarioSQLAlchemy(session)
        assert repo.actualizar_password(999999, "hash-nuevo") is False


def test_actualizar_password_de_usuario_inactivo_no_modifica_hash(
    test_session_factory,
):
    id_usuario = _crear_usuario(
        test_session_factory,
        dni="81000002",
        email="inactivo@example.com",
        activo=False,
    )

    with test_session_factory() as session:
        repo = RepositorioUsuarioSQLAlchemy(session)
        assert repo.actualizar_password(id_usuario, "hash-nuevo") is False
        session.commit()

    with test_session_factory() as session:
        modelo = session.get(UsuarioModelo, id_usuario)
        assert modelo is not None
        assert modelo.activo is False
        assert modelo.password_hash == "hash-anterior"


def test_actualizar_password_detecta_baja_logica_concurrente(
    test_session_factory,
):
    id_usuario = _crear_usuario(
        test_session_factory,
        dni="81000003",
        email="carrera@example.com",
    )

    with test_session_factory() as session_a:
        repo_a = RepositorioUsuarioSQLAlchemy(session_a)
        usuario_leido = repo_a.obtener_por_id(id_usuario)
        assert usuario_leido is not None
        assert usuario_leido.activo is True

        with test_session_factory() as session_b:
            repo_b = RepositorioUsuarioSQLAlchemy(session_b)
            assert repo_b.eliminar(id_usuario) is True
            session_b.commit()

        assert repo_a.actualizar_password(id_usuario, "hash-nuevo") is False
        session_a.commit()

    with test_session_factory() as session:
        modelo = session.get(UsuarioModelo, id_usuario)
        assert modelo is not None
        assert modelo.activo is False
        assert modelo.password_hash == "hash-anterior"
