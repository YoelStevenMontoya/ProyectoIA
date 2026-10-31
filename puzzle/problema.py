"""
Modelado del 8-puzzle ponderado como espacio de estados.

Idea del problema:
    Es el 8-puzzle de siempre (tablero 3x3, fichas del 1 al 8 y un hueco),
    pero cada ficha tiene un PESO igual a su numero. Mover la ficha 7 cuesta 7
    y mover la ficha 1 cuesta 1. Asi los costos de las acciones NO son todos
    iguales, que es lo que se necesita para que costo uniforme y A* tengan
    sentido (con costos iguales UCS seria lo mismo que BFS).

Representacion del estado:
    Una tupla de 9 enteros leida por filas, el 0 es el hueco.
    Ej: (1, 2, 3,
         4, 0, 5,
         7, 8, 6)
    Usamos tupla porque es inmutable y se puede meter en sets y dicts
    (necesario para controlar estados repetidos).
"""

import random

N = 3  # tamaño del tablero (3x3)

META = (1, 2, 3,
        4, 5, 6,
        7, 8, 0)

# Las acciones son hacia donde se mueve el HUECO.
# (cambio de fila, cambio de columna)
MOVIMIENTOS = {
    "ARRIBA": (-1, 0),
    "ABAJO": (1, 0),
    "IZQUIERDA": (0, -1),
    "DERECHA": (0, 1),
}

# Cuando el hueco se mueve hacia arriba, la ficha que estaba arriba baja.
# Esto solo se usa para mostrar los pasos de forma entendible.
SENTIDO_FICHA = {
    "ARRIBA": "abajo",
    "ABAJO": "arriba",
    "IZQUIERDA": "a la derecha",
    "DERECHA": "a la izquierda",
}


def peso_ficha(ficha):
    """El peso de una ficha es su propio numero (ficha 5 -> pesa 5)."""
    return ficha


class ProblemaPuzzle:
    """
    Define el problema siguiendo la formulacion vista en clase:
    estado inicial, acciones, funcion de transicion (resultado),
    prueba de meta y costo de cada accion.

    Los algoritmos de busqueda solo usan estos metodos, asi que no
    "saben" que estan resolviendo un puzzle.
    """

    def __init__(self, inicial, meta=META):
        inicial = tuple(inicial)
        if not es_estado_valido(inicial):
            raise ValueError("El estado debe tener los numeros del 0 al 8 sin repetir")
        if not es_resoluble(inicial, meta):
            raise ValueError("Ese estado no tiene solucion (paridad de inversiones distinta a la meta)")
        self.inicial = inicial
        self.meta = tuple(meta)

    def acciones(self, estado):
        """Lista de movimientos validos del hueco en este estado."""
        pos = estado.index(0)
        fila, col = divmod(pos, N)
        validas = []
        # el orden importa para DFS/BFS: siempre se intenta en este orden
        for nombre, (df, dc) in MOVIMIENTOS.items():
            nf, nc = fila + df, col + dc
            if 0 <= nf < N and 0 <= nc < N:
                validas.append(nombre)
        return validas

    def resultado(self, estado, accion):
        """Funcion de transicion: devuelve el estado nuevo despues de la accion."""
        pos = estado.index(0)
        fila, col = divmod(pos, N)
        df, dc = MOVIMIENTOS[accion]
        nueva_pos = (fila + df) * N + (col + dc)

        lista = list(estado)
        lista[pos], lista[nueva_pos] = lista[nueva_pos], lista[pos]
        return tuple(lista)

    def es_meta(self, estado):
        return estado == self.meta

    def costo_accion(self, estado, accion, estado_nuevo):
        """
        Costo de mover una ficha = peso de la ficha que se desliza.
        La ficha que se movio es la que quedo donde antes estaba el hueco.
        """
        pos_hueco_antes = estado.index(0)
        ficha_movida = estado_nuevo[pos_hueco_antes]
        return peso_ficha(ficha_movida)

    def ficha_movida(self, estado, accion):
        """Que ficha se mueve con esta accion (para mostrar la solucion)."""
        pos = estado.index(0)
        fila, col = divmod(pos, N)
        df, dc = MOVIMIENTOS[accion]
        return estado[(fila + df) * N + (col + dc)]


# ----------------------------------------------------------------------
# Funciones de apoyo
# ----------------------------------------------------------------------

def es_estado_valido(estado):
    return len(estado) == N * N and sorted(estado) == list(range(N * N))


def contar_inversiones(estado):
    """Pares de fichas (sin contar el hueco) que estan en orden invertido."""
    fichas = [x for x in estado if x != 0]
    inv = 0
    for i in range(len(fichas)):
        for j in range(i + 1, len(fichas)):
            if fichas[i] > fichas[j]:
                inv += 1
    return inv


def es_resoluble(estado, meta=META):
    """
    En un tablero de ancho impar (3x3) un movimiento nunca cambia la
    paridad del numero de inversiones, entonces el estado tiene solucion
    solo si su paridad es la misma que la de la meta.
    """
    return contar_inversiones(estado) % 2 == contar_inversiones(meta) % 2


def mezclar(num_movimientos=20, semilla=None, meta=META):
    """
    Genera un estado inicial haciendo movimientos aleatorios desde la meta.
    Asi el estado siempre tiene solucion. Se evita deshacer el movimiento
    anterior para que la mezcla sea mas "real".
    """
    rnd = random.Random(semilla)
    problema_aux = ProblemaPuzzle(meta, meta)
    estado = tuple(meta)
    opuesto = {"ARRIBA": "ABAJO", "ABAJO": "ARRIBA",
               "IZQUIERDA": "DERECHA", "DERECHA": "IZQUIERDA"}
    anterior = None
    for _ in range(num_movimientos):
        opciones = problema_aux.acciones(estado)
        if anterior is not None and len(opciones) > 1:
            opciones = [a for a in opciones if a != opuesto[anterior]]
        accion = rnd.choice(opciones)
        estado = problema_aux.resultado(estado, accion)
        anterior = accion
    return estado


def texto_a_estado(texto):
    """
    Convierte lo que escribe el usuario en un estado.
    Acepta '1 2 3 4 0 5 7 8 6', '1,2,3,4,0,5,7,8,6' o '123405786'.
    """
    limpio = texto.replace(",", " ").replace(";", " ").strip()
    if " " in limpio:
        partes = limpio.split()
    else:
        partes = list(limpio)
    try:
        estado = tuple(int(p) for p in partes)
    except ValueError:
        raise ValueError("Solo se permiten numeros del 0 al 8")
    if not es_estado_valido(estado):
        raise ValueError("Deben ser los numeros del 0 al 8, cada uno una sola vez")
    return estado


def estado_a_texto(estado):
    """Representacion en varias lineas para consola."""
    filas = []
    for f in range(N):
        fila = estado[f * N:(f + 1) * N]
        filas.append(" ".join(str(x) if x != 0 else "_" for x in fila))
    return "\n".join(filas)
