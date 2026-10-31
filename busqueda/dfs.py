"""
Busqueda en profundidad (DFS) - version de grafo.

Frontera: PILA (LIFO), usamos una lista de Python con append/pop.
Control de repetidos: diccionario `vistos` estado -> profundidad con la que
se metio a la frontera. Un estado que ya se vio no se vuelve a meter.

Limite de profundidad (opcional):
    Si se da un limite, los nodos que lleguen a esa profundidad no se
    expanden. En ese modo dejamos volver a meter un estado si ahora se llega
    a el por un camino MAS CORTO, porque si no se podria perder la solucion
    (el estado quedo marcado desde una rama profunda que fue cortada).

DFS no es optima: devuelve la primera solucion que encuentra, que en el
8-puzzle suele ser larguisima (miles de pasos) si no se pone limite.
"""

from busqueda.nodo import Nodo
from busqueda.resultado import armar_resultado


def dfs(problema, limite=None):
    nombre = "DFS" if limite is None else f"DFS (limite {limite})"
    raiz = Nodo(problema.inicial)

    frontera = [raiz]
    vistos = {raiz.estado: 0}
    expandidos = 0
    generados = 1
    cortados = 0
    max_frontera = 1
    max_memoria = 1

    while frontera:
        nodo = frontera.pop()  # sacamos el ultimo que entro (pila)

        # en modo con limite pueden quedar copias viejas en la pila, se ignoran
        if limite is not None and nodo.profundidad > vistos[nodo.estado]:
            continue

        if problema.es_meta(nodo.estado):
            res = armar_resultado(nombre, nodo, expandidos, generados, max_frontera, max_memoria)
            return res

        if limite is not None and nodo.profundidad >= limite:
            cortados += 1
            continue

        expandidos += 1
        # se meten al reves para que la primera accion quede encima de la pila
        # y se explore primero (asi el orden es el mismo que el de acciones())
        for hijo in reversed(nodo.expandir(problema)):
            generados += 1
            prof_previa = vistos.get(hijo.estado)
            if prof_previa is None or (limite is not None and hijo.profundidad < prof_previa):
                vistos[hijo.estado] = hijo.profundidad
                frontera.append(hijo)

        if len(frontera) > max_frontera:
            max_frontera = len(frontera)
        if len(vistos) > max_memoria:
            max_memoria = len(vistos)

    res = armar_resultado(nombre, None, expandidos, generados, max_frontera, max_memoria)
    if limite is not None and cortados > 0:
        res.mensaje = f"Se cortaron {cortados} nodos por el limite de profundidad, prueba con uno mayor."
    else:
        res.mensaje = "Se exploro todo el espacio alcanzable."
    return res
