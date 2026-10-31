"""
Casos de prueba fijos. Se usan en la interfaz (lista de ejemplos), en
comparar.py y en las pruebas, para que todos los algoritmos se comparen
sobre las mismas entradas.

Se generaron con mezclar(movimientos, semilla) y se dejaron escritos
para que no cambien. El numero de pasos optimo se saco con BFS y el costo
optimo con UCS.
"""

CASOS_PRUEBA = {
    # nombre: (estado, pasos minimos, costo minimo)
    "Caso 1 - Facil": ((1, 5, 0,
                        7, 4, 2,
                        8, 6, 3), 10, 46),
    "Caso 2 - Medio (BFS no es optimo en costo)": ((1, 2, 3,
                                                    7, 5, 8,
                                                    0, 4, 6), 18, 91),
    "Caso 3 - Medio": ((5, 8, 2,
                        4, 0, 1,
                        6, 3, 7), 20, 94),
    "Caso 4 - Dificil": ((8, 7, 1,
                          6, 5, 4,
                          2, 3, 0), 26, 122),
}
