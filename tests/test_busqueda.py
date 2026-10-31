"""
Pruebas de los algoritmos de busqueda sobre el 8-puzzle ponderado.
Correr desde la carpeta del proyecto con:
    python -m unittest discover tests
"""

import random
import unittest

from busqueda import dfs, bfs, ucs, a_estrella
from puzzle.problema import ProblemaPuzzle, META, mezclar, es_resoluble, texto_a_estado
from puzzle.heuristicas import h_manhattan_ponderada, h_mal_ubicadas_ponderada
from puzzle.casos import CASOS_PRUEBA


def verificar_camino(test, problema, res):
    """Revisa que el camino sea valido: cada paso es legal, termina en la meta y el costo cuadra."""
    test.assertTrue(res.exito)
    test.assertEqual(res.estados[0], problema.inicial)
    test.assertTrue(problema.es_meta(res.estados[-1]))
    test.assertEqual(len(res.acciones), res.profundidad)
    costo = 0
    for i, accion in enumerate(res.acciones):
        test.assertIn(accion, problema.acciones(res.estados[i]))
        siguiente = problema.resultado(res.estados[i], accion)
        test.assertEqual(siguiente, res.estados[i + 1])
        costo += problema.costo_accion(res.estados[i], accion, siguiente)
    test.assertEqual(costo, res.costo)


class TestProblema(unittest.TestCase):

    def test_costo_es_el_peso_de_la_ficha(self):
        p = ProblemaPuzzle((1, 2, 3, 4, 5, 6, 7, 0, 8))
        estado = p.inicial
        nuevo = p.resultado(estado, "DERECHA")  # el 8 se mueve a la izquierda
        self.assertEqual(nuevo, META)
        self.assertEqual(p.costo_accion(estado, "DERECHA", nuevo), 8)

    def test_estado_sin_solucion(self):
        self.assertFalse(es_resoluble((2, 1, 3, 4, 5, 6, 7, 8, 0)))
        with self.assertRaises(ValueError):
            ProblemaPuzzle((2, 1, 3, 4, 5, 6, 7, 8, 0))

    def test_mezclar_siempre_resoluble(self):
        for s in range(30):
            self.assertTrue(es_resoluble(mezclar(40, semilla=s)))

    def test_texto_a_estado(self):
        self.assertEqual(texto_a_estado("1 2 3 4 0 5 7 8 6"), (1, 2, 3, 4, 0, 5, 7, 8, 6))
        self.assertEqual(texto_a_estado("123405786"), (1, 2, 3, 4, 0, 5, 7, 8, 6))
        with self.assertRaises(ValueError):
            texto_a_estado("1 1 3 4 0 5 7 8 6")


class TestAlgoritmos(unittest.TestCase):

    def test_meta_como_estado_inicial(self):
        p = ProblemaPuzzle(META)
        for res in (dfs(p), bfs(p), ucs(p), a_estrella(p, h_manhattan_ponderada)):
            self.assertTrue(res.exito)
            self.assertEqual(res.costo, 0)
            self.assertEqual(res.profundidad, 0)

    def test_casos_de_prueba(self):
        for nombre, (estado, pasos_opt, costo_opt) in CASOS_PRUEBA.items():
            with self.subTest(caso=nombre):
                p = ProblemaPuzzle(estado)
                r_dfs = dfs(p)
                r_bfs = bfs(p)
                r_ucs = ucs(p)
                r_h2 = a_estrella(p, h_manhattan_ponderada)
                r_h1 = a_estrella(p, h_mal_ubicadas_ponderada)
                for r in (r_dfs, r_bfs, r_ucs, r_h2, r_h1):
                    verificar_camino(self, p, r)

                # BFS -> minimo numero de pasos
                self.assertEqual(r_bfs.profundidad, pasos_opt)
                # UCS y A* -> minimo costo
                self.assertEqual(r_ucs.costo, costo_opt)
                self.assertEqual(r_h2.costo, costo_opt)
                self.assertEqual(r_h1.costo, costo_opt)
                # A* expande menos que UCS, y h2 menos que h1
                self.assertLess(r_h2.nodos_expandidos, r_ucs.nodos_expandidos)
                self.assertLessEqual(r_h2.nodos_expandidos, r_h1.nodos_expandidos)
                # nadie tiene un costo menor que el optimo
                self.assertGreaterEqual(r_bfs.costo, costo_opt)
                self.assertGreaterEqual(r_dfs.costo, costo_opt)

    def test_dfs_con_limite(self):
        estado, pasos_opt, _ = CASOS_PRUEBA["Caso 3 - Medio"]
        p = ProblemaPuzzle(estado)
        self.assertFalse(dfs(p, limite=pasos_opt - 1).exito)  # con menos pasos que el optimo no hay solucion
        res = dfs(p, limite=pasos_opt + 4)
        verificar_camino(self, p, res)
        self.assertLessEqual(res.profundidad, pasos_opt + 4)


class TestHeuristicas(unittest.TestCase):

    def test_h_es_cero_en_la_meta(self):
        self.assertEqual(h_manhattan_ponderada(META), 0)
        self.assertEqual(h_mal_ubicadas_ponderada(META), 0)

    def test_h2_domina_a_h1(self):
        for s in range(200):
            e = mezclar(30, semilla=s)
            self.assertGreaterEqual(h_manhattan_ponderada(e), h_mal_ubicadas_ponderada(e))

    def test_admisibles(self):
        """h(n) <= costo real optimo (calculado con UCS) en estados aleatorios."""
        for s in range(25):
            e = mezclar(random.Random(s).randint(5, 25), semilla=s)
            optimo = ucs(ProblemaPuzzle(e)).costo
            self.assertLessEqual(h_manhattan_ponderada(e), optimo)
            self.assertLessEqual(h_mal_ubicadas_ponderada(e), optimo)

    def test_consistentes(self):
        """h(n) <= c(n, n') + h(n') para todos los vecinos de muchos estados."""
        for s in range(300):
            e = mezclar(50, semilla=s)
            p = ProblemaPuzzle(e)
            for accion in p.acciones(e):
                vecino = p.resultado(e, accion)
                c = p.costo_accion(e, accion, vecino)
                for h in (h_manhattan_ponderada, h_mal_ubicadas_ponderada):
                    self.assertLessEqual(h(e), c + h(vecino))


if __name__ == "__main__":
    unittest.main()
