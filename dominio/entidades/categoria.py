# ============================================================
# Entidad: Categoria
# ============================================================
# Representa una fila de la tabla 'categorias'.
# El dominio define QUÉ es una categoría y sus reglas.
# ============================================================

from dominio.validaciones import validar_no_vacio


class Categoria:
    def __init__(self, nombre: str, id_categoria: int = None):
        self.id_categoria = id_categoria
        self.nombre = nombre

    def validar(self):
        validar_no_vacio(self.nombre, 'nombre')
