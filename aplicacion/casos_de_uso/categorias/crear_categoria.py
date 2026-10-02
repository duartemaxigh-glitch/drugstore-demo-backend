# ============================================================
# Caso de Uso: Crear Categoría
# ============================================================
# Recibe los datos, crea la entidad, la valida y la guarda.
#
# Fijate que recibe RepositorioCategoria (la INTERFAZ, no la
# implementación). Esto es INVERSIÓN DE DEPENDENCIAS:
# Aplicación depende de una abstracción, no de PostgreSQL.
# ============================================================

from dominio.entidades.categoria import Categoria
from dominio.repositorios.repositorio_categoria import RepositorioCategoria


class CrearCategoria:
    def __init__(self, repositorio: RepositorioCategoria):
        self.repositorio = repositorio

    def ejecutar(self, nombre: str) -> Categoria:
        categoria = Categoria(nombre=nombre)
        categoria.validar()
        return self.repositorio.crear(categoria)
