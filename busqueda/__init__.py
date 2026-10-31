"""
Algoritmos de busqueda implementados por el grupo (sin librerias externas).
Todos reciben un objeto problema con: inicial, acciones(), resultado(),
es_meta() y costo_accion(); por eso sirven para cualquier problema.
"""

from busqueda.dfs import dfs
from busqueda.bfs import bfs
from busqueda.ucs import ucs
from busqueda.a_estrella import a_estrella
from busqueda.resultado import ResultadoBusqueda

__all__ = ["dfs", "bfs", "ucs", "a_estrella", "ResultadoBusqueda"]
