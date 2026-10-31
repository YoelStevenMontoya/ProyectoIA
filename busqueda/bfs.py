"""
Busqueda en amplitud (BFS) - version de grafo.

Frontera: COLA (FIFO) con collections.deque (popleft es O(1), con una
lista normal pop(0) seria O(n)).

Se hace la prueba de meta cuando el nodo se GENERA y no cuando se saca de la
cola. En BFS esto sigue dando la solucion con menos pasos y ahorra expandir
todo un nivel completo.

Ojo: BFS encuentra la solucion con MENOS PASOS, pero como las fichas pesan
distinto, no necesariamente es la de menor COSTO.
"""

from collections import deque

from busqueda.nodo import Nodo
from busqueda.resultado import armar_resultado


def bfs(problema):
    nombre = "BFS"
    raiz = Nodo(problema.inicial)
    if problema.es_meta(raiz.estado):
        return armar_resultado(nombre, raiz, 0, 1, 1, 1)

    frontera = deque([raiz])
    vistos = {raiz.estado}  # estados en la frontera o ya expandidos
    expandidos = 0
    generados = 1
    max_frontera = 1

    while frontera:
        nodo = frontera.popleft()
        expandidos += 1

        for hijo in nodo.expandir(problema):
            generados += 1
            if hijo.estado in vistos:
                continue
            if problema.es_meta(hijo.estado):
                return armar_resultado(nombre, hijo, expandidos, generados,
                                       max(max_frontera, len(frontera) + 1), len(vistos) + 1)
            vistos.add(hijo.estado)
            frontera.append(hijo)

        if len(frontera) > max_frontera:
            max_frontera = len(frontera)

    res = armar_resultado(nombre, None, expandidos, generados, max_frontera, len(vistos))
    res.mensaje = "Se exploro todo el espacio alcanzable."
    return res
