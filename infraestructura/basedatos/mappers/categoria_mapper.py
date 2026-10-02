from dominio.entidades.categoria import Categoria
from infraestructura.basedatos.modelos.categoria_modelo import CategoriaModelo


def a_dominio(modelo: CategoriaModelo) -> Categoria:
    return Categoria(
        id_categoria=modelo.id_categoria,
        nombre=modelo.nombre,
    )

def nuevo_modelo(categoria: Categoria) -> CategoriaModelo:
    return CategoriaModelo(
        nombre=categoria.nombre,
    )
