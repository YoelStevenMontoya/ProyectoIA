"""
Tablero de Conecta 4 (6 filas x 7 columnas).

La fila 0 es la de ARRIBA (asi se dibuja mas facil). Las fichas "caen",
entonces en cada columna se llena de abajo hacia arriba. Guardamos la
altura de cada columna para no tener que recorrerla cada vez.

Para que minimax sea rapido el tablero se modifica en el sitio con
jugar() y deshacer() en vez de copiarlo en cada nodo.
"""

FILAS = 6
COLUMNAS = 7
VACIO = 0
JUGADOR1 = 1  # rojo, empieza por defecto
JUGADOR2 = 2  # amarillo

NOMBRES = {JUGADOR1: "Rojo", JUGADOR2: "Amarillo"}


def oponente(jugador):
    return JUGADOR2 if jugador == JUGADOR1 else JUGADOR1


class Tablero:

    def __init__(self):
        self.celdas = [[VACIO] * COLUMNAS for _ in range(FILAS)]
        self.alturas = [0] * COLUMNAS
        self.num_fichas = 0

    def copia(self):
        t = Tablero()
        t.celdas = [fila[:] for fila in self.celdas]
        t.alturas = self.alturas[:]
        t.num_fichas = self.num_fichas
        return t

    def puede_jugar(self, col):
        return 0 <= col < COLUMNAS and self.alturas[col] < FILAS

    def columnas_validas(self):
        return [c for c in range(COLUMNAS) if self.alturas[c] < FILAS]

    def jugar(self, col, jugador):
        """Deja caer una ficha en la columna. Devuelve la fila donde quedo."""
        if not self.puede_jugar(col):
            raise ValueError(f"La columna {col + 1} esta llena o no existe")
        fila = FILAS - 1 - self.alturas[col]
        self.celdas[fila][col] = jugador
        self.alturas[col] += 1
        self.num_fichas += 1
        return fila

    def deshacer(self, col):
        """Quita la ficha de mas arriba de la columna (para minimax)."""
        self.alturas[col] -= 1
        fila = FILAS - 1 - self.alturas[col]
        self.celdas[fila][col] = VACIO
        self.num_fichas -= 1

    def lleno(self):
        return self.num_fichas == FILAS * COLUMNAS

    def es_ganadora(self, fila, col, jugador):
        """
        Revisa si la ficha que acaba de caer en (fila, col) forma 4 en linea.
        Solo hace falta mirar las lineas que pasan por esa casilla.
        """
        direcciones = [(0, 1), (1, 0), (1, 1), (1, -1)]  # horizontal, vertical, 2 diagonales
        for df, dc in direcciones:
            cuenta = 1
            # hacia un lado
            f, c = fila + df, col + dc
            while 0 <= f < FILAS and 0 <= c < COLUMNAS and self.celdas[f][c] == jugador:
                cuenta += 1
                f += df
                c += dc
            # hacia el otro lado
            f, c = fila - df, col - dc
            while 0 <= f < FILAS and 0 <= c < COLUMNAS and self.celdas[f][c] == jugador:
                cuenta += 1
                f -= df
                c -= dc
            if cuenta >= 4:
                return True
        return False

    def linea_ganadora(self, fila, col, jugador):
        """Igual que es_ganadora pero devuelve las casillas (para resaltarlas en la interfaz)."""
        for df, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            casillas = [(fila, col)]
            f, c = fila + df, col + dc
            while 0 <= f < FILAS and 0 <= c < COLUMNAS and self.celdas[f][c] == jugador:
                casillas.append((f, c))
                f += df
                c += dc
            f, c = fila - df, col - dc
            while 0 <= f < FILAS and 0 <= c < COLUMNAS and self.celdas[f][c] == jugador:
                casillas.append((f, c))
                f -= df
                c -= dc
            if len(casillas) >= 4:
                return casillas
        return []

    def __str__(self):
        simbolos = {VACIO: ".", JUGADOR1: "X", JUGADOR2: "O"}
        lineas = [" ".join(simbolos[x] for x in fila) for fila in self.celdas]
        lineas.append(" ".join(str(c + 1) for c in range(COLUMNAS)))
        return "\n".join(lineas)
