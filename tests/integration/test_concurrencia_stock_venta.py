"""Regresiones de concurrencia para todos los movimientos de stock."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from decimal import Decimal
from threading import Barrier, Event, Lock, current_thread
from time import monotonic, sleep

import pytest
from sqlalchemy import event, func, select, text

from aplicacion.casos_de_uso.compras.crear_compra import CrearCompra
from aplicacion.casos_de_uso.compras.eliminar_compra import EliminarCompra
from aplicacion.casos_de_uso.productos.actualizar_producto import (
    ActualizarProducto,
)
from aplicacion.casos_de_uso.ventas.crear_venta import CrearVenta
from aplicacion.casos_de_uso.ventas.eliminar_venta import EliminarVenta
from dominio.excepciones import EntidadNoEncontrada, ErrorDeValidacion
from infraestructura.basedatos.modelos.categoria_modelo import CategoriaModelo
from infraestructura.basedatos.modelos.compra_modelo import (
    CompraDetalleModelo,
    CompraModelo,
)
from infraestructura.basedatos.modelos.medio_pago_modelo import MedioPagoModelo
from infraestructura.basedatos.modelos.producto_modelo import ProductoModelo
from infraestructura.basedatos.modelos.proveedor_modelo import ProveedorModelo
from infraestructura.basedatos.modelos.usuario_modelo import UsuarioModelo
from infraestructura.basedatos.modelos.venta_modelo import (
    VentaDetalleModelo,
    VentaModelo,
)
from infraestructura.basedatos.unidad_trabajo import (
    UnidadDeTrabajoSQLAlchemy,
)
from infraestructura.repositorios.repositorio_compra_sqlalchemy import (
    RepositorioCompraSQLAlchemy,
)
from infraestructura.repositorios.repositorio_producto_sqlalchemy import (
    RepositorioProductoSQLAlchemy,
)
from infraestructura.repositorios.repositorio_venta_sqlalchemy import (
    RepositorioVentaSQLAlchemy,
)


pytestmark = pytest.mark.integration
TIMEOUT = 10


@dataclass(frozen=True)
class DatosBase:
    id_usuario: int
    id_medio_pago: int
    id_proveedor: int
    id_categoria: int
    ids_producto: tuple[int, ...]


def _crear_datos_base(session_factory, stocks: tuple[int, ...]) -> DatosBase:
    with session_factory() as session:
        categoria = CategoriaModelo(nombre="Concurrencia")
        usuario = UsuarioModelo(
            apellido="Concurrente",
            nombre="Ana",
            dni="30000001",
            email="concurrencia@example.com",
            password_hash="hash-de-prueba",
            rol="empleado",
        )
        medio = MedioPagoModelo(nombre="Efectivo concurrente")
        proveedor = ProveedorModelo(
            razon_social="Proveedor concurrente",
            cuit_cuil="80000001",
        )
        session.add_all([categoria, usuario, medio, proveedor])
        session.flush()

        productos = [
            ProductoModelo(
                codigo_barras=f"77919999999{indice:02d}",
                nombre=f"Producto concurrente {indice}",
                precio_venta=Decimal("10.00"),
                precio_compra=Decimal("5.00"),
                stock=stock,
                id_categoria=categoria.id_categoria,
            )
            for indice, stock in enumerate(stocks, start=1)
        ]
        session.add_all(productos)
        session.commit()

        return DatosBase(
            id_usuario=usuario.id_usuario,
            id_medio_pago=medio.id_medio_pago,
            id_proveedor=proveedor.id_proveedor,
            id_categoria=categoria.id_categoria,
            ids_producto=tuple(
                producto.id_producto for producto in productos
            ),
        )


def _crear_venta_existente(
    session_factory,
    datos: DatosBase,
    cantidad: int,
) -> int:
    with session_factory() as session:
        venta = VentaModelo(
            id_usuario=datos.id_usuario,
            id_medio_pago=datos.id_medio_pago,
            total=Decimal("10.00") * cantidad,
            detalles=[
                VentaDetalleModelo(
                    id_producto=datos.ids_producto[0],
                    cantidad=cantidad,
                    precio_unitario=Decimal("10.00"),
                    subtotal=Decimal("10.00") * cantidad,
                )
            ],
        )
        session.add(venta)
        session.commit()
        return venta.id_venta


def _crear_compra_existente(
    session_factory,
    datos: DatosBase,
    cantidad: int,
) -> int:
    with session_factory() as session:
        compra = CompraModelo(
            id_proveedor=datos.id_proveedor,
            id_usuario=datos.id_usuario,
            total=Decimal("5.00") * cantidad,
            detalles=[
                CompraDetalleModelo(
                    id_producto=datos.ids_producto[0],
                    cantidad=cantidad,
                    precio_unitario=Decimal("5.00"),
                    subtotal=Decimal("5.00") * cantidad,
                )
            ],
        )
        session.add(compra)
        session.commit()
        return compra.id_compra


def _pid(session) -> int:
    return session.execute(text("SELECT pg_backend_pid()")).scalar_one()


def _esperar_bloqueo(test_engine, pid_bloqueado: int, pid_bloqueador: int):
    limite = monotonic() + TIMEOUT
    ultimo = None
    with test_engine.connect() as observador:
        while monotonic() < limite:
            ultimo = observador.execute(
                text(
                    """
                    SELECT wait_event_type,
                           wait_event,
                           pg_blocking_pids(:pid) AS blocking_pids,
                           state,
                           query
                    FROM pg_stat_activity
                    WHERE pid = :pid
                    """
                ),
                {"pid": pid_bloqueado},
            ).mappings().one()
            if pid_bloqueador in ultimo["blocking_pids"]:
                return ultimo
            sleep(0.02)

    pytest.fail(f"No se observó el bloqueo esperado. Último estado: {ultimo}")


class ProductoRetenidoSQLAlchemy(RepositorioProductoSQLAlchemy):
    def __init__(self, session, bloqueado: Event, continuar: Event):
        super().__init__(session)
        self.bloqueado = bloqueado
        self.continuar = continuar

    def obtener_para_modificar_stock(self, ids_producto):
        productos = super().obtener_para_modificar_stock(ids_producto)
        self.bloqueado.set()
        if not self.continuar.wait(timeout=TIMEOUT):
            raise TimeoutError("No se habilitó la transacción retenida")
        return productos


class VentaRetenidaSQLAlchemy(RepositorioVentaSQLAlchemy):
    def __init__(self, session, bloqueada: Event, continuar: Event):
        super().__init__(session)
        self.bloqueada = bloqueada
        self.continuar = continuar

    def obtener_para_eliminar(self, id_venta):
        venta = super().obtener_para_eliminar(id_venta)
        self.bloqueada.set()
        if not self.continuar.wait(timeout=TIMEOUT):
            raise TimeoutError("No se habilitó la eliminación retenida")
        return venta


class CompraRetenidaSQLAlchemy(RepositorioCompraSQLAlchemy):
    def __init__(self, session, bloqueada: Event, continuar: Event):
        super().__init__(session)
        self.bloqueada = bloqueada
        self.continuar = continuar

    def obtener_para_eliminar(self, id_compra):
        compra = super().obtener_para_eliminar(id_compra)
        self.bloqueada.set()
        if not self.continuar.wait(timeout=TIMEOUT):
            raise TimeoutError("No se habilitó la eliminación retenida")
        return compra


def _iniciar_captura_sql(test_engine, sentencias: list[dict[str, object]]):
    lock = Lock()

    def capturar(
        _conexion,
        _cursor,
        sentencia,
        parametros,
        _contexto,
        _muchos,
    ) -> None:
        sql = " ".join(sentencia.split())
        with lock:
            sentencias.append(
                {
                    "hilo": current_thread().name,
                    "sql": sql,
                    "parametros": dict(parametros)
                    if isinstance(parametros, dict)
                    else parametros,
                }
            )

    event.listen(test_engine, "before_cursor_execute", capturar)
    return capturar


def test_dos_ventas_concurrentes_serializan_stock(
    test_engine,
    test_session_factory,
):
    datos = _crear_datos_base(test_session_factory, (5,))
    producto_bloqueado = Event()
    permitir_a = Event()
    b_iniciada = Event()
    pids: dict[str, int] = {}
    sql: list[dict[str, object]] = []
    listener = _iniciar_captura_sql(test_engine, sql)

    def vender_a():
        current_thread().name = "crear-venta-A"
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            pids["A"] = _pid(uow.session)
            return CrearVenta(
                RepositorioVentaSQLAlchemy(uow.session),
                ProductoRetenidoSQLAlchemy(
                    uow.session,
                    producto_bloqueado,
                    permitir_a,
                ),
            ).ejecutar(
                datos.id_usuario,
                datos.id_medio_pago,
                [{"id_producto": datos.ids_producto[0], "cantidad": 4}],
            )

    def vender_b():
        current_thread().name = "crear-venta-B"
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            pids["B"] = _pid(uow.session)
            b_iniciada.set()
            return CrearVenta(
                RepositorioVentaSQLAlchemy(uow.session),
                RepositorioProductoSQLAlchemy(uow.session),
            ).ejecutar(
                datos.id_usuario,
                datos.id_medio_pago,
                [{"id_producto": datos.ids_producto[0], "cantidad": 4}],
            )

    bloqueo = None
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuro_a = executor.submit(vender_a)
            assert producto_bloqueado.wait(timeout=TIMEOUT)
            futuro_b = executor.submit(vender_b)
            assert b_iniciada.wait(timeout=TIMEOUT)
            bloqueo = _esperar_bloqueo(
                test_engine,
                pids["B"],
                pids["A"],
            )
            permitir_a.set()
            futuro_a.result(timeout=TIMEOUT)
            with pytest.raises(ErrorDeValidacion, match="Stock insuficiente"):
                futuro_b.result(timeout=TIMEOUT)
    finally:
        permitir_a.set()
        event.remove(test_engine, "before_cursor_execute", listener)

    with test_session_factory() as session:
        assert session.get(ProductoModelo, datos.ids_producto[0]).stock == 1
        assert session.scalar(select(func.count()).select_from(VentaModelo)) == 1
        assert session.scalar(
            select(func.count()).select_from(VentaDetalleModelo)
        ) == 1

    locks_producto = [
        item["sql"]
        for item in sql
        if "FROM productos" in str(item["sql"])
        and "FOR UPDATE" in str(item["sql"])
    ]
    assert len(locks_producto) == 2
    assert all(
        "ORDER BY productos.id_producto" in sentencia
        for sentencia in locks_producto
    )
    assert bloqueo["wait_event_type"] == "Lock"
    assert bloqueo["wait_event"] == "transactionid"
    assert "FOR UPDATE" in bloqueo["query"]

    print("\nSQL FOR UPDATE observado:", locks_producto[0])
    print("Bloqueo observado:", dict(bloqueo))


def test_dos_compras_concurrentes_conservan_ambas_sumas(
    test_engine,
    test_session_factory,
):
    datos = _crear_datos_base(test_session_factory, (5,))
    producto_bloqueado = Event()
    permitir_a = Event()
    b_iniciada = Event()
    pids: dict[str, int] = {}

    def comprar(cantidad, retenida=False):
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            nombre = "A" if retenida else "B"
            pids[nombre] = _pid(uow.session)
            if not retenida:
                b_iniciada.set()
            repo_producto = (
                ProductoRetenidoSQLAlchemy(
                    uow.session,
                    producto_bloqueado,
                    permitir_a,
                )
                if retenida
                else RepositorioProductoSQLAlchemy(uow.session)
            )
            return CrearCompra(
                RepositorioCompraSQLAlchemy(uow.session),
                repo_producto,
            ).ejecutar(
                datos.id_proveedor,
                datos.id_usuario,
                [
                    {
                        "id_producto": datos.ids_producto[0],
                        "cantidad": cantidad,
                        "precio_unitario": Decimal("5.00"),
                    }
                ],
            )

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuro_a = executor.submit(comprar, 3, True)
            assert producto_bloqueado.wait(timeout=TIMEOUT)
            futuro_b = executor.submit(comprar, 4)
            assert b_iniciada.wait(timeout=TIMEOUT)
            _esperar_bloqueo(test_engine, pids["B"], pids["A"])
            permitir_a.set()
            futuro_a.result(timeout=TIMEOUT)
            futuro_b.result(timeout=TIMEOUT)
    finally:
        permitir_a.set()

    with test_session_factory() as session:
        assert session.get(ProductoModelo, datos.ids_producto[0]).stock == 12
        assert session.scalar(select(func.count()).select_from(CompraModelo)) == 2


def test_venta_y_compra_concurrentes_no_pierden_deltas(
    test_engine,
    test_session_factory,
):
    datos = _crear_datos_base(test_session_factory, (5,))
    producto_bloqueado = Event()
    permitir_venta = Event()
    compra_iniciada = Event()
    pids: dict[str, int] = {}

    def vender():
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            pids["venta"] = _pid(uow.session)
            return CrearVenta(
                RepositorioVentaSQLAlchemy(uow.session),
                ProductoRetenidoSQLAlchemy(
                    uow.session,
                    producto_bloqueado,
                    permitir_venta,
                ),
            ).ejecutar(
                datos.id_usuario,
                datos.id_medio_pago,
                [{"id_producto": datos.ids_producto[0], "cantidad": 4}],
            )

    def comprar():
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            pids["compra"] = _pid(uow.session)
            compra_iniciada.set()
            return CrearCompra(
                RepositorioCompraSQLAlchemy(uow.session),
                RepositorioProductoSQLAlchemy(uow.session),
            ).ejecutar(
                datos.id_proveedor,
                datos.id_usuario,
                [
                    {
                        "id_producto": datos.ids_producto[0],
                        "cantidad": 3,
                        "precio_unitario": Decimal("5.00"),
                    }
                ],
            )

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuro_venta = executor.submit(vender)
            assert producto_bloqueado.wait(timeout=TIMEOUT)
            futuro_compra = executor.submit(comprar)
            assert compra_iniciada.wait(timeout=TIMEOUT)
            _esperar_bloqueo(
                test_engine,
                pids["compra"],
                pids["venta"],
            )
            permitir_venta.set()
            futuro_venta.result(timeout=TIMEOUT)
            futuro_compra.result(timeout=TIMEOUT)
    finally:
        permitir_venta.set()

    with test_session_factory() as session:
        assert session.get(ProductoModelo, datos.ids_producto[0]).stock == 4
        assert session.scalar(select(func.count()).select_from(VentaModelo)) == 1
        assert session.scalar(select(func.count()).select_from(CompraModelo)) == 1


def test_dos_eliminar_venta_bloquean_cabecera_y_restituyen_una_vez(
    test_engine,
    test_session_factory,
):
    datos = _crear_datos_base(test_session_factory, (1,))
    id_venta = _crear_venta_existente(test_session_factory, datos, 4)
    cabecera_bloqueada = Event()
    permitir_a = Event()
    b_iniciada = Event()
    b_intento_productos = Event()
    pids: dict[str, int] = {}

    class ProductoBObservado(RepositorioProductoSQLAlchemy):
        def obtener_para_modificar_stock(self, ids_producto):
            b_intento_productos.set()
            return super().obtener_para_modificar_stock(ids_producto)

    def eliminar_a():
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            pids["A"] = _pid(uow.session)
            return EliminarVenta(
                VentaRetenidaSQLAlchemy(
                    uow.session,
                    cabecera_bloqueada,
                    permitir_a,
                ),
                RepositorioProductoSQLAlchemy(uow.session),
            ).ejecutar(id_venta)

    def eliminar_b():
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            pids["B"] = _pid(uow.session)
            b_iniciada.set()
            return EliminarVenta(
                RepositorioVentaSQLAlchemy(uow.session),
                ProductoBObservado(uow.session),
            ).ejecutar(id_venta)

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuro_a = executor.submit(eliminar_a)
            assert cabecera_bloqueada.wait(timeout=TIMEOUT)
            futuro_b = executor.submit(eliminar_b)
            assert b_iniciada.wait(timeout=TIMEOUT)
            bloqueo = _esperar_bloqueo(
                test_engine,
                pids["B"],
                pids["A"],
            )
            assert "FROM ventas" in bloqueo["query"]
            assert "FOR UPDATE" in bloqueo["query"]
            assert not b_intento_productos.is_set()
            print("\nLock de cabecera Venta observado:", bloqueo["query"])
            permitir_a.set()
            futuro_a.result(timeout=TIMEOUT)
            with pytest.raises(EntidadNoEncontrada, match="venta"):
                futuro_b.result(timeout=TIMEOUT)
    finally:
        permitir_a.set()

    assert not b_intento_productos.is_set()
    with test_session_factory() as session:
        assert session.get(ProductoModelo, datos.ids_producto[0]).stock == 5
        assert session.get(VentaModelo, id_venta) is None


def test_dos_eliminar_compra_bloquean_cabecera_y_descontabilizan_una_vez(
    test_engine,
    test_session_factory,
):
    datos = _crear_datos_base(test_session_factory, (9,))
    id_compra = _crear_compra_existente(test_session_factory, datos, 4)
    cabecera_bloqueada = Event()
    permitir_a = Event()
    b_iniciada = Event()
    b_intento_productos = Event()
    pids: dict[str, int] = {}

    class ProductoBObservado(RepositorioProductoSQLAlchemy):
        def obtener_para_modificar_stock(self, ids_producto):
            b_intento_productos.set()
            return super().obtener_para_modificar_stock(ids_producto)

    def eliminar_a():
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            pids["A"] = _pid(uow.session)
            return EliminarCompra(
                CompraRetenidaSQLAlchemy(
                    uow.session,
                    cabecera_bloqueada,
                    permitir_a,
                ),
                RepositorioProductoSQLAlchemy(uow.session),
            ).ejecutar(id_compra)

    def eliminar_b():
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            pids["B"] = _pid(uow.session)
            b_iniciada.set()
            return EliminarCompra(
                RepositorioCompraSQLAlchemy(uow.session),
                ProductoBObservado(uow.session),
            ).ejecutar(id_compra)

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuro_a = executor.submit(eliminar_a)
            assert cabecera_bloqueada.wait(timeout=TIMEOUT)
            futuro_b = executor.submit(eliminar_b)
            assert b_iniciada.wait(timeout=TIMEOUT)
            bloqueo = _esperar_bloqueo(
                test_engine,
                pids["B"],
                pids["A"],
            )
            assert "FROM compras" in bloqueo["query"]
            assert "FOR UPDATE" in bloqueo["query"]
            assert not b_intento_productos.is_set()
            print("\nLock de cabecera Compra observado:", bloqueo["query"])
            permitir_a.set()
            futuro_a.result(timeout=TIMEOUT)
            with pytest.raises(EntidadNoEncontrada, match="compra"):
                futuro_b.result(timeout=TIMEOUT)
    finally:
        permitir_a.set()

    assert not b_intento_productos.is_set()
    with test_session_factory() as session:
        assert session.get(ProductoModelo, datos.ids_producto[0]).stock == 5
        assert session.get(CompraModelo, id_compra) is None


def test_actualizar_producto_concurrente_no_restaura_stock_obsoleto(
    test_engine,
    test_session_factory,
):
    datos = _crear_datos_base(test_session_factory, (5,))
    producto_bloqueado = Event()
    permitir_venta = Event()
    update_iniciado = Event()
    pids: dict[str, int] = {}

    class ProductoDatosObservado(RepositorioProductoSQLAlchemy):
        def actualizar_datos(self, producto):
            update_iniciado.set()
            return super().actualizar_datos(producto)

    def vender():
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            pids["venta"] = _pid(uow.session)
            return CrearVenta(
                RepositorioVentaSQLAlchemy(uow.session),
                ProductoRetenidoSQLAlchemy(
                    uow.session,
                    producto_bloqueado,
                    permitir_venta,
                ),
            ).ejecutar(
                datos.id_usuario,
                datos.id_medio_pago,
                [{"id_producto": datos.ids_producto[0], "cantidad": 4}],
            )

    def actualizar():
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            pids["update"] = _pid(uow.session)
            return ActualizarProducto(
                ProductoDatosObservado(uow.session)
            ).ejecutar(
                id_producto=datos.ids_producto[0],
                nombre="Nombre actualizado",
                precio_venta=Decimal("20.00"),
                precio_compra=Decimal("7.00"),
                codigo_barras="7791888888888",
                id_categoria=datos.id_categoria,
            )

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuro_venta = executor.submit(vender)
            assert producto_bloqueado.wait(timeout=TIMEOUT)
            futuro_update = executor.submit(actualizar)
            assert update_iniciado.wait(timeout=TIMEOUT)
            bloqueo = _esperar_bloqueo(
                test_engine,
                pids["update"],
                pids["venta"],
            )
            assert "UPDATE productos" in bloqueo["query"]
            clausula_set = (
                bloqueo["query"].lower()
                .split(" set ", maxsplit=1)[1]
                .split(" where ", maxsplit=1)[0]
            )
            assert "stock" not in clausula_set
            permitir_venta.set()
            futuro_venta.result(timeout=TIMEOUT)
            respuesta = futuro_update.result(timeout=TIMEOUT)
    finally:
        permitir_venta.set()

    assert respuesta.stock == 1
    assert respuesta.nombre == "Nombre actualizado"
    with test_session_factory() as session:
        producto = session.get(ProductoModelo, datos.ids_producto[0])
        assert producto.stock == 1
        assert producto.nombre == "Nombre actualizado"
        assert producto.precio_venta == Decimal("20.00")


def test_operaciones_multiproducto_inversas_bloquean_en_orden_ascendente(
    test_engine,
    test_session_factory,
):
    datos = _crear_datos_base(test_session_factory, (10, 10))
    inicio = Barrier(2)
    sql: list[dict[str, object]] = []
    listener = _iniciar_captura_sql(test_engine, sql)

    class ProductoSincronizado(RepositorioProductoSQLAlchemy):
        def obtener_para_modificar_stock(self, ids_producto):
            inicio.wait(timeout=TIMEOUT)
            return super().obtener_para_modificar_stock(ids_producto)

    def comprar(detalles, nombre):
        current_thread().name = nombre
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            return CrearCompra(
                RepositorioCompraSQLAlchemy(uow.session),
                ProductoSincronizado(uow.session),
            ).ejecutar(
                datos.id_proveedor,
                datos.id_usuario,
                detalles,
            )

    detalles_a = [
        {
            "id_producto": datos.ids_producto[0],
            "cantidad": 1,
            "precio_unitario": Decimal("5.00"),
        },
        {
            "id_producto": datos.ids_producto[1],
            "cantidad": 1,
            "precio_unitario": Decimal("5.00"),
        },
    ]
    detalles_b = list(reversed(detalles_a))

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuro_a = executor.submit(comprar, detalles_a, "multi-A")
            futuro_b = executor.submit(comprar, detalles_b, "multi-B")
            futuro_a.result(timeout=TIMEOUT)
            futuro_b.result(timeout=TIMEOUT)
    finally:
        event.remove(test_engine, "before_cursor_execute", listener)

    with test_session_factory() as session:
        stocks = session.scalars(
            select(ProductoModelo.stock).order_by(
                ProductoModelo.id_producto
            )
        ).all()
        assert stocks == [12, 12]

    locks = [
        item
        for item in sql
        if "FROM productos" in str(item["sql"])
        and "FOR UPDATE" in str(item["sql"])
    ]
    assert len(locks) == 2
    assert all(
        "ORDER BY productos.id_producto" in str(item["sql"])
        for item in locks
    )
    for item in locks:
        ids_enviados = [
            valor
            for clave, valor in item["parametros"].items()
            if str(clave).startswith("id_producto")
        ]
        assert ids_enviados == sorted(datos.ids_producto)


def test_producto_repetido_bloquea_y_actualiza_una_sola_vez(
    test_engine,
    test_session_factory,
):
    datos = _crear_datos_base(test_session_factory, (5,))
    sql: list[dict[str, object]] = []
    listener = _iniciar_captura_sql(test_engine, sql)

    try:
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            venta = CrearVenta(
                RepositorioVentaSQLAlchemy(uow.session),
                RepositorioProductoSQLAlchemy(uow.session),
            ).ejecutar(
                datos.id_usuario,
                datos.id_medio_pago,
                [
                    {"id_producto": datos.ids_producto[0], "cantidad": 2},
                    {"id_producto": datos.ids_producto[0], "cantidad": 2},
                ],
            )
    finally:
        event.remove(test_engine, "before_cursor_execute", listener)

    with test_session_factory() as session:
        assert session.get(ProductoModelo, datos.ids_producto[0]).stock == 1

    locks = [
        item for item in sql
        if "FROM productos" in str(item["sql"])
        and "FOR UPDATE" in str(item["sql"])
    ]
    updates = [
        item for item in sql
        if str(item["sql"]).startswith("UPDATE productos SET stock=")
    ]
    assert len(locks) == 1
    assert len(updates) == 1
    assert [detalle.cantidad for detalle in venta.detalles] == [2, 2]
    assert [detalle.subtotal for detalle in venta.detalles] == [
        Decimal("20.00"),
        Decimal("20.00"),
    ]


def test_rollback_libera_lock_y_transaccion_en_espera_continua(
    test_engine,
    test_session_factory,
):
    datos = _crear_datos_base(test_session_factory, (5,))
    producto_bloqueado = Event()
    permitir_a = Event()
    b_iniciada = Event()
    pids: dict[str, int] = {}

    def venta_que_falla():
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            pids["A"] = _pid(uow.session)
            return CrearVenta(
                RepositorioVentaSQLAlchemy(uow.session),
                ProductoRetenidoSQLAlchemy(
                    uow.session,
                    producto_bloqueado,
                    permitir_a,
                ),
            ).ejecutar(
                datos.id_usuario,
                999999,
                [{"id_producto": datos.ids_producto[0], "cantidad": 4}],
            )

    def venta_valida():
        with UnidadDeTrabajoSQLAlchemy(test_session_factory) as uow:
            pids["B"] = _pid(uow.session)
            b_iniciada.set()
            return CrearVenta(
                RepositorioVentaSQLAlchemy(uow.session),
                RepositorioProductoSQLAlchemy(uow.session),
            ).ejecutar(
                datos.id_usuario,
                datos.id_medio_pago,
                [{"id_producto": datos.ids_producto[0], "cantidad": 4}],
            )

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuro_a = executor.submit(venta_que_falla)
            assert producto_bloqueado.wait(timeout=TIMEOUT)
            futuro_b = executor.submit(venta_valida)
            assert b_iniciada.wait(timeout=TIMEOUT)
            _esperar_bloqueo(test_engine, pids["B"], pids["A"])
            permitir_a.set()
            with pytest.raises(EntidadNoEncontrada, match="medio de pago"):
                futuro_a.result(timeout=TIMEOUT)
            futuro_b.result(timeout=TIMEOUT)
    finally:
        permitir_a.set()

    with test_session_factory() as session:
        assert session.get(ProductoModelo, datos.ids_producto[0]).stock == 1
        assert session.scalar(select(func.count()).select_from(VentaModelo)) == 1
        assert session.scalar(
            select(func.count()).select_from(VentaDetalleModelo)
        ) == 1
