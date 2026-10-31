"""
Busqueda A*.

Es igual a costo uniforme pero la cola de prioridad se ordena por
    f(n) = g(n) + h(n)
donde h(n) es la heuristica (estimado del costo que falta hasta la meta).

Desempate: si dos nodos tienen el mismo f se prefiere el de menor h
(el que esta "mas cerca" de la meta). Esto no cambia la optimalidad pero
ayuda a que A* expanda menos nodos en los empates, que en este problema
son muchos.

Si la heuristica es consistente, cuando un estado sale de la cola ya tiene
su costo optimo. Igual dejamos el control con mejor_g, que permite
"reabrir" un estado si apareciera un camino mas barato, por si alguien
prueba una heuristica que no sea consistente.
"""

import heapq
from itertools import count

from busqueda.nodo import Nodo
from busqueda.resultado import armar_resultado


def a_estrella(problema, heuristica, nombre_h=""):
    nombre = "A*" if not nombre_h else f"A* ({nombre_h})"
    raiz = Nodo(problema.inicial)
    contador = count()

    h0 = heuristica(raiz.estado)
    frontera = [(h0, h0, next(contador), raiz)]
    mejor_g = {raiz.estado: 0}
    expandidos = 0
    generados = 1
    max_frontera = 1

    while frontera:
        f, h, _, nodo = heapq.heappop(frontera)

        if nodo.costo > mejor_g[nodo.estado]:
            continue  # entrada vieja

        if problema.es_meta(nodo.estado):
            return armar_resultado(nombre, nodo, expandidos, generados, max_frontera, len(mejor_g))

        expandidos += 1
        for hijo in nodo.expandir(problema):
            generados += 1
            if hijo.estado not in mejor_g or hijo.costo < mejor_g[hijo.estado]:
                mejor_g[hijo.estado] = hijo.costo
                h_hijo = heuristica(hijo.estado)
                heapq.heappush(frontera, (hijo.costo + h_hijo, h_hijo, next(contador), hijo))

        if len(frontera) > max_frontera:
            max_frontera = len(frontera)

    res = armar_resultado(nombre, None, expandidos, generados, max_frontera, len(mejor_g))
    res.mensaje = "Se exploro todo el espacio alcanzable."
    return res
