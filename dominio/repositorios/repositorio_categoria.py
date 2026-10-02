# ============================================================
# Interfaz: RepositorioCategoria
# ============================================================
# Este es un CONTRATO. Define qué operaciones se pueden hacer
# con categorías, pero NO dice cómo se hacen.
#
# ABC = Abstract Base Class (Clase Base Abstracta)
# @abstractmethod = "este método DEBE ser implementado por
#                    quien herede de esta clase"
#
# ¿Por qué? Porque mañana podés cambiar PostgreSQL por otro motor
# y solo tenés que crear otra clase que implemente este
# contrato. El resto del código NO se toca.
# ============================================================

from abc import ABC, abstractmethod

from dominio.entidades.categoria import Categoria


class RepositorioCategoria(ABC):

    @abstractmethod
    def crear(self, categoria: Categoria) -> Categoria:
        pass

    @abstractmethod
    def obtener_por_id(self, id_categoria: int) -> Categoria | None:
        pass

    @abstractmethod
    def obtener_todos(self) -> list[Categoria]:
        pass

    @abstractmethod
    def actualizar(self, categoria: Categoria) -> Categoria | None:
        pass

    @abstractmethod
    def eliminar(self, id_categoria: int) -> bool:
        pass
