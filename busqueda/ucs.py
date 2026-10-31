"""
Busqueda de costo uniforme (UCS).

Frontera: COLA DE PRIORIDAD (heapq) ordenada por g(n), el costo acumulado.
Siempre se expande el nodo mas barato hasta el momento.

Detalles de implementacion:
  * La prueba de meta se hace al SACAR el nodo de la cola. Si se hiciera al
    generarlo se podria devolver un camino que no es el mas barato.
  * heapq no permite "actualizar" la prioridad de un elemento. Cuando se
    encuentra un camino mas barato a un estado se mete otra entrada y la
    vieja se ignora cuando salga (la detectamos comparando con mejor_g).
  * Se usa un contador como desempate para que heapq nunca tenga que
    comparar dos objetos Nodo (y para que el orden sea FIFO en empates).
"""

import heapq
from itertools import count

from busqueda.nodo import Nodo
from busqueda.resultado import armar_resultado


def ucs(problema):
    nombre = "Costo uniforme"
    raiz = Nodo(problema.inicial)
    contador = count()

    frontera = [(0, next(contador), raiz)]
    mejor_g = {raiz.estado: 0}  # menor costo conocido para llegar a cada estado
    expandidos = 0
    generados = 1
    max_frontera = 1

    while frontera:
        g, _, nodo = heapq.heappop(frontera)

        if g > mejor_g[nodo.estado]:
            continue  # entrada vieja, ya habia un camino mas barato

        if problema.es_meta(nodo.estado):
            return armar_resultado(nombre, nodo, expandidos, generados, max_frontera, len(mejor_g))

        expandidos += 1
        for hijo in nodo.expandir(problema):
            generados += 1
            if hijo.estado not in mejor_g or hijo.costo < mejor_g[hijo.estado]:
                mejor_g[hijo.estado] = hijo.costo
                heapq.heappush(frontera, (hijo.costo, next(contador), hijo))

        if len(frontera) > max_frontera:
            max_frontera = len(frontera)

    res = armar_resultado(nombre, None, expandidos, generados, max_frontera, len(mejor_g))
    res.mensaje = "Se exploro todo el espacio alcanzable."
    return res
