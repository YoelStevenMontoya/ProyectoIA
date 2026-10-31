"""
Minimax con y sin poda alfa-beta para Conecta 4.

- MAX es la IA y MIN es el rival. La utilidad siempre se calcula desde el
  punto de vista de la IA.
- Estados terminales: alguien hizo 4 en linea o el tablero se lleno.
    * gana la IA   -> +GANAR + profundidad_restante
    * gana el rival -> -GANAR - profundidad_restante
    * empate        -> 0
  Sumar la profundidad restante hace que la IA prefiera ganar rapido y,
  si va a perder, perder lo mas tarde posible.
- Si se llega a la profundidad limite se usa la funcion de evaluacion.

Se cuentan los nodos visitados en las dos versiones para mostrar cuanto se
ahorra la poda. Las dos exploran las columnas en el mismo orden (centro
primero), asi la comparacion es justa. Ese orden ademas ayuda mucho a la
poda porque las mejores jugadas suelen estar en el centro y se encuentran
primero.
"""

import math
import time

from conecta4.tablero import oponente
from conecta4.evaluacion import evaluar

GANAR = 1_000_000
ORDEN_COLUMNAS = [3, 2, 4, 1, 5, 0, 6]


class Estadisticas:
    def __init__(self):
        self.nodos = 0   # nodos visitados (cada llamada recursiva)
        self.hojas = 0   # nodos en los que se aplico la funcion de evaluacion o eran terminales
        self.podas = 0   # veces que se corto una rama


def _columnas_ordenadas(tablero):
    return [c for c in ORDEN_COLUMNAS if tablero.puede_jugar(c)]


def _valor_terminal(tablero, ultima, profundidad, jugador_ia):
    """
    Revisa si el estado es terminal. `ultima` es (fila, col, jugador) de la
    jugada que llevo a este estado. Devuelve el valor o None si no es terminal.
    """
    if ultima is not None:
        fila, col, quien = ultima
        if tablero.es_ganadora(fila, col, quien):
            if quien == jugador_ia:
                return GANAR + profundidad
            return -GANAR - profundidad
    if tablero.lleno():
        return 0
    return None


# ----------------------------------------------------------------------
# Minimax SIN poda (solo para comparar cuantos nodos revisa)
# ----------------------------------------------------------------------

def minimax(tablero, profundidad, maximizando, jugador_ia, stats, ultima=None):
    stats.nodos += 1

    terminal = _valor_terminal(tablero, ultima, profundidad, jugador_ia)
    if terminal is not None:
        stats.hojas += 1
        return terminal
    if profundidad == 0:
        stats.hojas += 1
        return evaluar(tablero, jugador_ia)

    jugador = jugador_ia if maximizando else oponente(jugador_ia)

    if maximizando:
        mejor = -math.inf
        for col in _columnas_ordenadas(tablero):
            fila = tablero.jugar(col, jugador)
            valor = minimax(tablero, profundidad - 1, False, jugador_ia, stats, (fila, col, jugador))
            tablero.deshacer(col)
            mejor = max(mejor, valor)
        return mejor
    else:
        mejor = math.inf
        for col in _columnas_ordenadas(tablero):
            fila = tablero.jugar(col, jugador)
            valor = minimax(tablero, profundidad - 1, True, jugador_ia, stats, (fila, col, jugador))
            tablero.deshacer(col)
            mejor = min(mejor, valor)
        return mejor


# ----------------------------------------------------------------------
# Minimax CON poda alfa-beta
# ----------------------------------------------------------------------

def alfa_beta(tablero, profundidad, alfa, beta, maximizando, jugador_ia, stats, ultima=None):
    """
    alfa = mejor valor que MAX ya tiene asegurado en el camino actual
    beta = mejor valor que MIN ya tiene asegurado en el camino actual
    Si en algun momento alfa >= beta, el otro jugador nunca dejaria llegar
    a este nodo, entonces no vale la pena seguir mirando sus hijos (poda).
    """
    stats.nodos += 1

    terminal = _valor_terminal(tablero, ultima, profundidad, jugador_ia)
    if terminal is not None:
        stats.hojas += 1
        return terminal
    if profundidad == 0:
        stats.hojas += 1
        return evaluar(tablero, jugador_ia)

    jugador = jugador_ia if maximizando else oponente(jugador_ia)

    if maximizando:
        valor = -math.inf
        for col in _columnas_ordenadas(tablero):
            fila = tablero.jugar(col, jugador)
            valor = max(valor, alfa_beta(tablero, profundidad - 1, alfa, beta, False,
                                         jugador_ia, stats, (fila, col, jugador)))
            tablero.deshacer(col)
            alfa = max(alfa, valor)
            if alfa >= beta:
                stats.podas += 1
                break  # poda beta: MIN no va a dejar que lleguemos aqui
        return valor
    else:
        valor = math.inf
        for col in _columnas_ordenadas(tablero):
            fila = tablero.jugar(col, jugador)
            valor = min(valor, alfa_beta(tablero, profundidad - 1, alfa, beta, True,
                                         jugador_ia, stats, (fila, col, jugador)))
            tablero.deshacer(col)
            beta = min(beta, valor)
            if alfa >= beta:
                stats.podas += 1
                break  # poda alfa: MAX ya tiene algo mejor en otra rama
        return valor


# ----------------------------------------------------------------------
# Decision en la raiz
# ----------------------------------------------------------------------

def mejor_jugada(tablero, jugador_ia, profundidad, con_poda=True):
    """
    Prueba cada columna (la raiz es un nodo MAX) y devuelve
    (mejor_columna, valor, estadisticas, valores_por_columna).
    """
    stats = Estadisticas()
    stats.nodos += 1  # la raiz
    tablero = tablero.copia()  # para no dañar el tablero del juego

    mejor_col = None
    mejor_valor = -math.inf
    alfa, beta = -math.inf, math.inf
    valores = {}

    for col in _columnas_ordenadas(tablero):
        fila = tablero.jugar(col, jugador_ia)
        if con_poda:
            valor = alfa_beta(tablero, profundidad - 1, alfa, beta, False,
                              jugador_ia, stats, (fila, col, jugador_ia))
        else:
            valor = minimax(tablero, profundidad - 1, False, jugador_ia, stats,
                            (fila, col, jugador_ia))
        tablero.deshacer(col)
        valores[col] = valor

        if valor > mejor_valor:
            mejor_valor = valor
            mejor_col = col
        if con_poda:
            alfa = max(alfa, mejor_valor)

    return mejor_col, mejor_valor, stats, valores


class InfoJugada:
    """Lo que se le muestra al usuario de cada jugada de la maquina."""

    def __init__(self):
        self.columna = None
        self.valor = 0
        self.profundidad = 0
        self.nodos_poda = 0
        self.hojas_poda = 0
        self.podas = 0
        self.tiempo_poda = 0.0
        self.nodos_sin_poda = None  # None si no se calculo
        self.tiempo_sin_poda = None

    def reduccion(self):
        """Porcentaje de nodos que se ahorro la poda."""
        if not self.nodos_sin_poda:
            return None
        return 100.0 * (1 - self.nodos_poda / self.nodos_sin_poda)

    def texto_valor(self):
        if self.valor >= GANAR:
            return "gana seguro"
        if self.valor <= -GANAR:
            return "pierde si el rival juega bien"
        return str(self.valor)


def decidir_jugada(tablero, jugador_ia, profundidad, comparar_sin_poda=True):
    """
    Decide la jugada con alfa-beta. Si comparar_sin_poda=True tambien corre
    minimax normal con la misma profundidad SOLO para contar sus nodos.
    """
    info = InfoJugada()
    info.profundidad = profundidad

    inicio = time.perf_counter()
    col, valor, stats, _ = mejor_jugada(tablero, jugador_ia, profundidad, con_poda=True)
    info.tiempo_poda = time.perf_counter() - inicio
    info.columna = col
    info.valor = valor
    info.nodos_poda = stats.nodos
    info.hojas_poda = stats.hojas
    info.podas = stats.podas

    if comparar_sin_poda:
        inicio = time.perf_counter()
        _, _, stats_sp, _ = mejor_jugada(tablero, jugador_ia, profundidad, con_poda=False)
        info.tiempo_sin_poda = time.perf_counter() - inicio
        info.nodos_sin_poda = stats_sp.nodos

    return info
