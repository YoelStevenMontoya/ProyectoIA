"""
Heuristicas para A* en el 8-puzzle ponderado.

Como mover la ficha k cuesta k, las heuristicas clasicas (fichas mal
ubicadas y Manhattan) se quedan cortas: subestiman demasiado. Por eso
diseñamos versiones PONDERADAS por el peso de cada ficha.

h1 - Fichas mal ubicadas ponderadas:
     h1(n) = suma de peso(k) para cada ficha k que no esta en su casilla meta.

h2 - Manhattan ponderada (la principal):
     h2(n) = suma de peso(k) * distancia_manhattan(k) para cada ficha k.

Las dos son admisibles y consistentes (el argumento completo esta en el
informe, seccion 6). Resumen:
  * Cada ficha k tiene que moverse al menos manhattan(k) veces y cada
    movimiento suyo cuesta peso(k)  =>  h2 nunca sobreestima.
  * Un movimiento solo cambia de lugar UNA ficha y en UNA casilla, entonces
    h2 cambia como mucho en peso(k), que es justo el costo del paso
    =>  h(n) <= c(n, n') + h(n')  (consistencia).
  * h1 <= h2 para todo estado (h2 domina a h1), por eso A* con h2 expande
    menos nodos.
"""

from puzzle.problema import N, META, peso_ficha


def _posiciones_meta(meta):
    """Diccionario ficha -> (fila, columna) en la meta. Se calcula una sola vez."""
    pos = {}
    for i, ficha in enumerate(meta):
        pos[ficha] = divmod(i, N)
    return pos


_POS_META = _posiciones_meta(META)


def h_cero(estado):
    """h = 0. Con esta heuristica A* se comporta igual que costo uniforme."""
    return 0


def h_mal_ubicadas_ponderada(estado):
    total = 0
    for i, ficha in enumerate(estado):
        if ficha != 0 and ficha != META[i]:
            total += peso_ficha(ficha)
    return total


def h_manhattan_ponderada(estado):
    total = 0
    for i, ficha in enumerate(estado):
        if ficha == 0:
            continue  # el hueco no cuenta, si no la heuristica dejaria de ser admisible
        fila, col = divmod(i, N)
        fila_meta, col_meta = _POS_META[ficha]
        distancia = abs(fila - fila_meta) + abs(col - col_meta)
        total += peso_ficha(ficha) * distancia
    return total


def detalle_manhattan(estado):
    """
    Devuelve la lista (ficha, distancia, peso, aporte) para explicar
    el calculo de h2 sobre un estado concreto (sirve para el informe).
    """
    filas = []
    for i, ficha in enumerate(estado):
        if ficha == 0:
            continue
        fila, col = divmod(i, N)
        fm, cm = _POS_META[ficha]
        d = abs(fila - fm) + abs(col - cm)
        filas.append((ficha, d, peso_ficha(ficha), d * peso_ficha(ficha)))
    filas.sort()
    return filas


# nombre que se muestra en la interfaz -> funcion
HEURISTICAS = {
    "Manhattan ponderada (h2)": h_manhattan_ponderada,
    "Fichas mal ubicadas ponderadas (h1)": h_mal_ubicadas_ponderada,
}
