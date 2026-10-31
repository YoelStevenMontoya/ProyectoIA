import random
import unittest

from conecta4.tablero import Tablero, JUGADOR1, JUGADOR2, oponente
from conecta4.minimax import mejor_jugada, decidir_jugada, GANAR
from conecta4.evaluacion import VENTANAS, evaluar


def tablero_desde(columnas):
    t = Tablero()
    j = JUGADOR1
    for c in columnas:
        t.jugar(c, j)
        j = oponente(j)
    return t, j


class TestTablero(unittest.TestCase):

    def test_gravedad_y_deshacer(self):
        t = Tablero()
        self.assertEqual(t.jugar(3, JUGADOR1), 5)  # cae hasta abajo
        self.assertEqual(t.jugar(3, JUGADOR2), 4)
        t.deshacer(3)
        self.assertEqual(t.alturas[3], 1)
        self.assertEqual(t.celdas[4][3], 0)

    def test_columna_llena(self):
        t = Tablero()
        for i in range(6):
            t.jugar(0, JUGADOR1 if i % 2 == 0 else JUGADOR2)
        self.assertFalse(t.puede_jugar(0))
        with self.assertRaises(ValueError):
            t.jugar(0, JUGADOR1)

    def test_victorias(self):
        # horizontal
        t, _ = tablero_desde([0, 0, 1, 1, 2, 2])
        f = t.jugar(3, JUGADOR1)
        self.assertTrue(t.es_ganadora(f, 3, JUGADOR1))
        # vertical
        t, _ = tablero_desde([0, 1, 0, 1, 0, 1])
        f = t.jugar(0, JUGADOR1)
        self.assertTrue(t.es_ganadora(f, 0, JUGADOR1))
        # diagonal /
        t, _ = tablero_desde([0, 1, 1, 2, 2, 3, 2, 3, 3, 6])
        f = t.jugar(3, JUGADOR1)
        self.assertTrue(t.es_ganadora(f, 3, JUGADOR1))
        # no gana
        t, _ = tablero_desde([0, 0, 1, 1])
        f = t.jugar(2, JUGADOR1)
        self.assertFalse(t.es_ganadora(f, 2, JUGADOR1))

    def test_numero_de_ventanas(self):
        # 24 horizontales + 21 verticales + 12 + 12 diagonales
        self.assertEqual(len(VENTANAS), 69)

    def test_evaluacion_simetrica(self):
        t, _ = tablero_desde([3, 2, 3, 4, 1])
        self.assertEqual(evaluar(t, JUGADOR1), -evaluar(t, JUGADOR2))


class TestMinimax(unittest.TestCase):

    def test_gana_cuando_puede(self):
        # Rojo tiene 3 abajo (cols 0,1,2) y le toca: debe jugar en la 3
        t, j = tablero_desde([0, 0, 1, 1, 2, 5])
        self.assertEqual(j, JUGADOR1)
        col, valor, _, _ = mejor_jugada(t, j, 4)
        self.assertEqual(col, 3)
        self.assertGreaterEqual(valor, GANAR)

    def test_bloquea_al_rival(self):
        # Amarillo tiene 3 en vertical en la columna 6, Rojo tiene que tapar
        t, j = tablero_desde([0, 6, 1, 6, 5, 6])
        self.assertEqual(j, JUGADOR1)
        col, _, _, _ = mejor_jugada(t, j, 4)
        self.assertEqual(col, 6)

    def test_poda_da_lo_mismo_que_minimax(self):
        """Con y sin poda se debe obtener el mismo valor y la misma jugada."""
        rnd = random.Random(3)
        for _ in range(25):
            t = Tablero()
            j = JUGADOR1
            for _ in range(rnd.randint(0, 16)):
                c = rnd.choice(t.columnas_validas())
                f = t.jugar(c, j)
                if t.es_ganadora(f, c, j):
                    t.deshacer(c)
                    break
                j = oponente(j)
            for prof in (1, 2, 3, 4):
                con = mejor_jugada(t, j, prof, con_poda=True)
                sin = mejor_jugada(t, j, prof, con_poda=False)
                self.assertEqual(con[0], sin[0])
                self.assertEqual(con[1], sin[1])
                self.assertLessEqual(con[2].nodos, sin[2].nodos)

    def test_poda_reduce_nodos(self):
        info = decidir_jugada(Tablero(), JUGADOR1, 5, comparar_sin_poda=True)
        self.assertLess(info.nodos_poda, info.nodos_sin_poda)
        self.assertGreater(info.reduccion(), 50)

    def test_no_modifica_el_tablero(self):
        t, j = tablero_desde([3, 3, 2])
        antes = [fila[:] for fila in t.celdas]
        decidir_jugada(t, j, 4)
        self.assertEqual(t.celdas, antes)


if __name__ == "__main__":
    unittest.main()
