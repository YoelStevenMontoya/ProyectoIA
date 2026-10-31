"""
Funcion de evaluacion para Conecta 4 (se usa cuando minimax llega a la
profundidad limite sin que el juego haya terminado).

Mira todas las "ventanas" de 4 casillas seguidas del tablero (horizontales,
verticales y diagonales, son 69 en total) y le da puntos segun lo que hay:

    Ventana                         Puntos (desde el punto de vista de la IA)
    3 fichas propias + 1 vacia      +100   (amenaza de ganar)
    2 fichas propias + 2 vacias     +10    (linea que puede crecer)
    3 del rival + 1 vacia           -120   (amenaza del rival, pesa MAS: defender primero)
    2 del rival + 2 vacias          -10
    ventana con fichas de los dos   0      (ya no le sirve a nadie)

Ademas suma un bono por posicion: cada casilla vale el numero de ventanas
de 4 que pasan por ella (las del centro estan en mas lineas, hasta 13; las
esquinas en solo 3), multiplicado por PESO_POSICION. Asi la IA prefiere el
centro, que es lo que se recomienda en estrategia de Conecta 4.

Los pesos los ajustamos poniendo a jugar la IA contra si misma con
distintos valores (ver torneo_ia() en comparar.py): con PESO_POSICION = 3
le gano a la version con peso 1 en la mayoria de partidas, por eso
nos quedamos con 3.
"""

from conecta4.tablero import FILAS, COLUMNAS, VACIO, oponente

PUNTOS_TRES = 100
PUNTOS_DOS = 10
PUNTOS_TRES_RIVAL = -120
PUNTOS_DOS_RIVAL = -10
PESO_POSICION = 3


def _calcular_ventanas():
    ventanas = []
    for f in range(FILAS):
        for c in range(COLUMNAS):
            for df, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                f_fin = f + 3 * df
                c_fin = c + 3 * dc
                if 0 <= f_fin < FILAS and 0 <= c_fin < COLUMNAS:
                    ventanas.append([(f + i * df, c + i * dc) for i in range(4)])
    return ventanas


VENTANAS = _calcular_ventanas()  # 69 ventanas, se calculan una sola vez


def _calcular_tabla_posicion():
    tabla = [[0] * COLUMNAS for _ in range(FILAS)]
    for ventana in VENTANAS:
        for f, c in ventana:
            tabla[f][c] += 1
    return tabla


TABLA_POSICION = _calcular_tabla_posicion()
# Queda asi (se puede comprobar imprimiendola):
#  3  4  5  7  5  4  3
#  4  6  8 10  8  6  4
#  5  8 11 13 11  8  5
#  5  8 11 13 11  8  5
#  4  6  8 10  8  6  4
#  3  4  5  7  5  4  3


def puntuar_ventana(valores, jugador):
    propias = valores.count(jugador)
    rivales = valores.count(oponente(jugador))
    vacias = valores.count(VACIO)

    if propias == 3 and vacias == 1:
        return PUNTOS_TRES
    if propias == 2 and vacias == 2:
        return PUNTOS_DOS
    if rivales == 3 and vacias == 1:
        return PUNTOS_TRES_RIVAL
    if rivales == 2 and vacias == 2:
        return PUNTOS_DOS_RIVAL
    return 0


def evaluar(tablero, jugador):
    """Puntaje del tablero desde el punto de vista de `jugador` (positivo = bueno para el)."""
    celdas = tablero.celdas
    puntaje = 0

    for ventana in VENTANAS:
        valores = [celdas[f][c] for f, c in ventana]
        puntaje += puntuar_ventana(valores, jugador)

    rival = oponente(jugador)
    for f in range(FILAS):
        for c in range(COLUMNAS):
            if celdas[f][c] == jugador:
                puntaje += PESO_POSICION * TABLA_POSICION[f][c]
            elif celdas[f][c] == rival:
                puntaje -= PESO_POSICION * TABLA_POSICION[f][c]

    return puntaje
