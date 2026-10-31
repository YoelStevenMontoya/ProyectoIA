"""
Script para sacar las tablas del analisis comparativo del informe.

    python comparar.py              -> tablas en consola + CSV en resultados/
                                       (+ graficas PNG si hay matplotlib)
    python comparar.py --torneo     -> ademas corre el torneo IA vs IA que usamos
                                       para ajustar el peso de la funcion de evaluacion

Todo se corre sobre los MISMOS casos de prueba (puzzle/casos.py) para que la
comparacion sea justa.
"""

import argparse
import csv
import os
import random
import time

from puzzle.casos import CASOS_PRUEBA
from puzzle.problema import estado_a_texto
from puzzle.heuristicas import detalle_manhattan, h_manhattan_ponderada, h_mal_ubicadas_ponderada
from puzzle.solucionador import ALGORITMOS, resolver
from conecta4.tablero import Tablero, JUGADOR1, oponente
from conecta4.minimax import mejor_jugada
import conecta4.evaluacion as evaluacion

CARPETA = "resultados"
REPETICIONES = 3  # el tiempo es el promedio de varias corridas

# Posiciones de Conecta 4 para comparar minimax con y sin poda.
# Son listas de columnas (0 a 6) jugadas alternando Rojo, Amarillo, Rojo...
POSICIONES_C4 = {
    "Inicio (tablero vacio)": [],
    "Apertura (4 jugadas)": [3, 3, 2, 4],
    "Medio juego (10 jugadas)": [5, 3, 1, 1, 3, 4, 2, 2, 3, 3],
}


# ----------------------------------------------------------------------
# Busqueda (puzzle)
# ----------------------------------------------------------------------

def comparar_busqueda():
    filas = []
    print("=" * 100)
    print("COMPARACION DE ALGORITMOS DE BUSQUEDA - 8-PUZZLE PONDERADO")
    print("=" * 100)

    for nombre_caso, (estado, pasos_opt, costo_opt) in CASOS_PRUEBA.items():
        print(f"\n{nombre_caso}   (optimo: {pasos_opt} pasos / costo {costo_opt})")
        print(estado_a_texto(estado))
        enc = (f"{'Algoritmo':34s} {'Pasos':>6s} {'Costo':>7s} {'Expandidos':>11s} {'Generados':>10s} "
               f"{'MaxFront':>9s} {'MemNodos':>9s} {'MemKB':>9s} {'ms':>9s}")
        print(enc)
        print("-" * len(enc))

        for alg in ALGORITMOS:
            tiempos = []
            for _ in range(REPETICIONES):
                r = resolver(alg, estado)
                tiempos.append(r.tiempo)
            r_mem = resolver(alg, estado, medir_memoria=True)
            r.tiempo = sum(tiempos) / len(tiempos)
            r.memoria_kb = r_mem.memoria_kb

            print(f"{alg:34s} {r.profundidad:6d} {r.costo:7d} {r.nodos_expandidos:11d} {r.nodos_generados:10d} "
                  f"{r.max_frontera:9d} {r.max_en_memoria:9d} {r.memoria_kb:9.0f} {r.tiempo * 1000:9.1f}")
            filas.append({
                "caso": nombre_caso, "algoritmo": alg, "pasos": r.profundidad, "costo": r.costo,
                "expandidos": r.nodos_expandidos, "generados": r.nodos_generados,
                "max_frontera": r.max_frontera, "max_nodos_memoria": r.max_en_memoria,
                "memoria_kb": round(r.memoria_kb, 1), "tiempo_ms": round(r.tiempo * 1000, 2),
                "costo_optimo": costo_opt,
            })
    guardar_csv("comparacion_busqueda.csv", filas)
    return filas


def ejemplo_heuristica():
    """Calculo de h1 y h2 paso a paso sobre el caso 1 (para el informe)."""
    estado = list(CASOS_PRUEBA.values())[0][0]
    print("\n" + "=" * 60)
    print("EJEMPLO DE CALCULO DE LA HEURISTICA (caso 1)")
    print("=" * 60)
    print(estado_a_texto(estado))
    print(f"\n{'Ficha':>5s} {'Dist.':>6s} {'Peso':>5s} {'Aporte':>7s}")
    for ficha, d, peso, aporte in detalle_manhattan(estado):
        print(f"{ficha:5d} {d:6d} {peso:5d} {aporte:7d}")
    print(f"h2 (Manhattan ponderada) = {h_manhattan_ponderada(estado)}")
    print(f"h1 (mal ubicadas ponderada) = {h_mal_ubicadas_ponderada(estado)}")
    print(f"Costo optimo real (UCS)  = {list(CASOS_PRUEBA.values())[0][2]}")


# ----------------------------------------------------------------------
# Minimax
# ----------------------------------------------------------------------

def armar_posicion(columnas):
    t = Tablero()
    jugador = JUGADOR1
    for c in columnas:
        t.jugar(c, jugador)
        jugador = oponente(jugador)
    return t, jugador  # tablero y a quien le toca


def comparar_minimax(prof_max=6):
    filas = []
    print("\n" + "=" * 100)
    print("MINIMAX CON Y SIN PODA ALFA-BETA - CONECTA 4")
    print("=" * 100)
    for nombre, cols in POSICIONES_C4.items():
        tablero, jugador = armar_posicion(cols)
        print(f"\n{nombre}  (juega {'Rojo' if jugador == JUGADOR1 else 'Amarillo'})")
        print(tablero)
        enc = f"{'Prof':>4s} {'Col':>4s} {'Sin poda':>10s} {'Con poda':>10s} {'Reduccion':>10s} {'ms sin':>9s} {'ms con':>9s} {'Misma jugada':>13s}"
        print(enc)
        print("-" * len(enc))
        for prof in range(1, prof_max + 1):
            t0 = time.perf_counter()
            col_sp, val_sp, st_sp, _ = mejor_jugada(tablero, jugador, prof, con_poda=False)
            t1 = time.perf_counter()
            col_cp, val_cp, st_cp, _ = mejor_jugada(tablero, jugador, prof, con_poda=True)
            t2 = time.perf_counter()
            red = 100 * (1 - st_cp.nodos / st_sp.nodos)
            igual = "si" if (col_sp == col_cp and val_sp == val_cp) else "NO"
            print(f"{prof:4d} {col_cp + 1:4d} {st_sp.nodos:10d} {st_cp.nodos:10d} {red:9.1f}% "
                  f"{(t1 - t0) * 1000:9.1f} {(t2 - t1) * 1000:9.1f} {igual:>13s}")
            filas.append({
                "posicion": nombre, "profundidad": prof, "columna": col_cp + 1,
                "nodos_sin_poda": st_sp.nodos, "nodos_con_poda": st_cp.nodos,
                "reduccion_pct": round(red, 1), "podas": st_cp.podas,
                "ms_sin_poda": round((t1 - t0) * 1000, 1), "ms_con_poda": round((t2 - t1) * 1000, 1),
                "misma_jugada": igual,
            })
    guardar_csv("comparacion_minimax.csv", filas)
    return filas


def torneo_ia(partidas=14, profundidad=4):
    """
    Pone a jugar la IA con PESO_POSICION = 1 contra PESO_POSICION = 3.
    Las 2 primeras jugadas son al azar para que no salga siempre la misma
    partida, y cada apertura se juega dos veces cambiando de color.
    """
    print("\n" + "=" * 60)
    print(f"TORNEO IA vs IA (peso posicion 1 vs 3, profundidad {profundidad})")
    print("=" * 60)
    original = evaluacion.PESO_POSICION
    victorias = {1: 0, 3: 0, "empate": 0}
    rnd = random.Random(11)

    def jugar(peso_rojo, peso_amarillo, semilla):
        r = random.Random(semilla)
        t = Tablero()
        jugador = JUGADOR1
        n = 0
        while True:
            if n < 2:
                col = r.choice(t.columnas_validas())
            else:
                evaluacion.PESO_POSICION = peso_rojo if jugador == JUGADOR1 else peso_amarillo
                col = mejor_jugada(t, jugador, profundidad)[0]
            fila = t.jugar(col, jugador)
            n += 1
            if t.es_ganadora(fila, col, jugador):
                return peso_rojo if jugador == JUGADOR1 else peso_amarillo
            if t.lleno():
                return "empate"
            jugador = oponente(jugador)

    try:
        for i in range(partidas // 2):
            semilla = rnd.random()
            victorias[jugar(1, 3, semilla)] += 1
            victorias[jugar(3, 1, semilla)] += 1
            print(f"  partidas {2 * (i + 1)}: {victorias}")
    finally:
        evaluacion.PESO_POSICION = original
    print(f"Resultado final: peso 1 gano {victorias[1]}, peso 3 gano {victorias[3]}, empates {victorias['empate']}")


# ----------------------------------------------------------------------
# Salidas
# ----------------------------------------------------------------------

def guardar_csv(nombre, filas):
    os.makedirs(CARPETA, exist_ok=True)
    ruta = os.path.join(CARPETA, nombre)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"\n-> guardado {ruta}")


def graficar(filas_busqueda, filas_minimax):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib no esta instalado, no se generan graficas. pip install matplotlib)")
        return

    os.makedirs(CARPETA, exist_ok=True)
    casos = list(CASOS_PRUEBA.keys())
    etiquetas_casos = [c.split(" - ")[0] for c in casos]
    colores = ["#8c8c8c", "#4c9be8", "#f28e2b", "#2e8b57", "#9c6ade"]

    for metrica, titulo, archivo in [("expandidos", "Nodos expandidos (escala log)", "nodos_expandidos.png"),
                                     ("tiempo_ms", "Tiempo de ejecucion en ms (escala log)", "tiempo.png"),
                                     ("memoria_kb", "Memoria pico en KB (escala log)", "memoria.png")]:
        fig, ax = plt.subplots(figsize=(9, 5.2))
        ancho = 0.16
        for i, alg in enumerate(ALGORITMOS):
            valores = [next(f[metrica] for f in filas_busqueda if f["caso"] == c and f["algoritmo"] == alg)
                       for c in casos]
            xs = [k + (i - 2) * ancho for k in range(len(casos))]
            ax.bar(xs, [max(v, 0.01) for v in valores], width=ancho, label=alg, color=colores[i])
        ax.set_yscale("log")
        ax.set_xticks(range(len(casos)))
        ax.set_xticklabels(etiquetas_casos)
        ax.set_title(titulo)
        ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=False)
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(CARPETA, archivo), dpi=130)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for nombre in POSICIONES_C4:
        datos = [f for f in filas_minimax if f["posicion"] == nombre]
        profs = [f["profundidad"] for f in datos]
        ax.plot(profs, [f["nodos_sin_poda"] for f in datos], "o--", label=f"{nombre} - sin poda")
        ax.plot(profs, [f["nodos_con_poda"] for f in datos], "s-", label=f"{nombre} - con poda")
    ax.set_yscale("log")
    ax.set_xlabel("Profundidad limite")
    ax.set_ylabel("Nodos evaluados")
    ax.set_title("Minimax: nodos evaluados con y sin poda alfa-beta")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(CARPETA, "minimax_poda.png"), dpi=130)
    plt.close(fig)
    print(f"-> graficas guardadas en {CARPETA}/")


def main():
    parser = argparse.ArgumentParser(description="Comparacion de algoritmos para el informe")
    parser.add_argument("--torneo", action="store_true", help="correr tambien el torneo IA vs IA")
    parser.add_argument("--sin-graficas", action="store_true", help="no generar las graficas PNG")
    args = parser.parse_args()

    filas_b = comparar_busqueda()
    ejemplo_heuristica()
    filas_m = comparar_minimax()
    if not args.sin_graficas:
        graficar(filas_b, filas_m)
    if args.torneo:
        torneo_ia()


if __name__ == "__main__":
    main()
