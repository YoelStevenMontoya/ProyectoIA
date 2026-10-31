"""
Punto unico para correr cualquier algoritmo sobre el puzzle.
Lo usan la interfaz grafica, la consola y el script de comparacion,
asi todos miden el tiempo y la memoria de la misma forma.
"""

import time
import tracemalloc

from busqueda import dfs, bfs, ucs, a_estrella
from puzzle.problema import ProblemaPuzzle
from puzzle.heuristicas import h_manhattan_ponderada, h_mal_ubicadas_ponderada

# nombres que se muestran al usuario
DFS = "DFS (profundidad)"
BFS = "BFS (amplitud)"
UCS = "Costo uniforme (UCS)"
A_H2 = "A* - Manhattan ponderada (h2)"
A_H1 = "A* - Mal ubicadas ponderadas (h1)"

ALGORITMOS = [DFS, BFS, UCS, A_H2, A_H1]


def _correr(nombre, problema, limite_dfs):
    if nombre == DFS:
        return dfs(problema, limite=limite_dfs)
    if nombre == BFS:
        return bfs(problema)
    if nombre == UCS:
        return ucs(problema)
    if nombre == A_H2:
        return a_estrella(problema, h_manhattan_ponderada, "h2 Manhattan pond.")
    if nombre == A_H1:
        return a_estrella(problema, h_mal_ubicadas_ponderada, "h1 mal ubicadas pond.")
    raise ValueError(f"Algoritmo desconocido: {nombre}")


def resolver(nombre, estado_inicial, limite_dfs=None, medir_memoria=False):
    """
    Corre el algoritmo y devuelve un ResultadoBusqueda con tiempo incluido.

    Si medir_memoria=True se usa tracemalloc para el pico de memoria.
    tracemalloc hace mas lento el codigo, por eso cuando se mide memoria
    se hace una segunda corrida aparte y el tiempo reportado es el de la
    corrida SIN tracemalloc.
    """
    problema = ProblemaPuzzle(estado_inicial)

    inicio = time.perf_counter()
    resultado = _correr(nombre, problema, limite_dfs)
    resultado.tiempo = time.perf_counter() - inicio

    if medir_memoria:
        tracemalloc.start()
        _correr(nombre, problema, limite_dfs)
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        resultado.memoria_kb = pico / 1024

    return resultado


def pasos_legibles(estados, acciones):
    """
    Convierte la solucion en frases tipo 'Mover 6 hacia arriba (costo 6)'.
    Devuelve una lista de strings.
    """
    from puzzle.problema import SENTIDO_FICHA, peso_ficha
    pasos = []
    for i, accion in enumerate(acciones):
        antes = estados[i]
        despues = estados[i + 1]
        ficha = despues[antes.index(0)]
        pasos.append(f"Mover {ficha} {SENTIDO_FICHA[accion]} (costo {peso_ficha(ficha)})")
    return pasos
