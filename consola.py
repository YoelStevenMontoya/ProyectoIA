"""
Version de consola de la aplicacion (respaldo por si falla la interfaz
grafica o no hay Tkinter). Tiene lo mismo: elegir algoritmo, resolver,
ver metricas, comparar, y jugar Conecta 4 contra la maquina.
"""

from puzzle.problema import mezclar, texto_a_estado, estado_a_texto, es_resoluble
from puzzle.solucionador import ALGORITMOS, DFS, resolver, pasos_legibles
from puzzle.casos import CASOS_PRUEBA
from conecta4.tablero import Tablero, JUGADOR1, JUGADOR2, NOMBRES, oponente
from conecta4.minimax import decidir_jugada

MAX_PASOS_MOSTRAR = 40


def pedir_entero(mensaje, minimo, maximo, defecto=None):
    while True:
        texto = input(mensaje).strip()
        if texto == "" and defecto is not None:
            return defecto
        try:
            valor = int(texto)
            if minimo <= valor <= maximo:
                return valor
        except ValueError:
            pass
        print(f"  Escribe un numero entre {minimo} y {maximo}.")


def linea():
    print("-" * 60)


# ----------------------------------------------------------------------
# Puzzle
# ----------------------------------------------------------------------

def elegir_estado(actual):
    print("\n¿Como quieres el estado inicial?")
    print("  1. Mezclar al azar")
    print("  2. Escribirlo")
    print("  3. Usar un caso de prueba")
    print("  4. Dejar el actual")
    op = pedir_entero("Opcion: ", 1, 4, 4)
    if op == 1:
        movs = pedir_entero("Numero de movimientos aleatorios [20]: ", 1, 500, 20)
        return mezclar(movs)
    if op == 2:
        while True:
            texto = input("Escribe los 9 numeros por filas (0 = hueco), ej. 1 2 3 4 0 5 7 8 6: ")
            try:
                estado = texto_a_estado(texto)
            except ValueError as e:
                print("  " + str(e))
                continue
            if not es_resoluble(estado):
                print("  Ese estado no tiene solucion (paridad de inversiones). Prueba otro.")
                continue
            return estado
    if op == 3:
        nombres = list(CASOS_PRUEBA.keys())
        for i, n in enumerate(nombres, 1):
            print(f"  {i}. {n}")
        k = pedir_entero("Caso: ", 1, len(nombres))
        return CASOS_PRUEBA[nombres[k - 1]][0]
    return actual


def mostrar_solucion(res):
    print()
    print(res.resumen())
    if not res.exito:
        return
    pasos = pasos_legibles(res.estados, res.acciones)
    print(f"\n  Camino ({len(pasos)} pasos):")
    for i, p in enumerate(pasos[:MAX_PASOS_MOSTRAR], 1):
        print(f"   {i:3d}. {p}")
    if len(pasos) > MAX_PASOS_MOSTRAR:
        print(f"   ... ({len(pasos) - MAX_PASOS_MOSTRAR} pasos mas, no se muestran)")


def tabla_comparacion(resultados):
    print()
    enc = f"{'Algoritmo':36s} {'Pasos':>6s} {'Costo':>7s} {'Expand.':>8s} {'Generad.':>9s} {'Mem.nodos':>9s} {'KB':>8s} {'ms':>9s}"
    print(enc)
    print("-" * len(enc))
    for r in resultados:
        kb = f"{r.memoria_kb:.0f}" if r.memoria_kb is not None else "-"
        pasos = str(r.profundidad) if r.exito else "-"
        costo = str(r.costo) if r.exito else "-"
        print(f"{r.algoritmo:36s} {pasos:>6s} {costo:>7s} {r.nodos_expandidos:8d} {r.nodos_generados:9d} "
              f"{r.max_en_memoria:9d} {kb:>8s} {r.tiempo * 1000:9.1f}")


def menu_puzzle():
    estado = mezclar(20, semilla=2)
    while True:
        linea()
        print("8-PUZZLE PONDERADO  (mover la ficha k cuesta k)")
        print("Estado actual:")
        print(estado_a_texto(estado))
        print("\n  1. Cambiar estado inicial")
        for i, a in enumerate(ALGORITMOS, 2):
            print(f"  {i}. Resolver con {a}")
        print(f"  {len(ALGORITMOS) + 2}. Comparar los 5 algoritmos")
        print("  0. Volver")
        op = pedir_entero("Opcion: ", 0, len(ALGORITMOS) + 2)

        if op == 0:
            return
        if op == 1:
            estado = elegir_estado(estado)
            continue

        medir = input("¿Medir memoria con tracemalloc? (s/N): ").strip().lower() == "s"
        if op == len(ALGORITMOS) + 2:
            lim = pedir_entero("Limite de profundidad para DFS (0 = sin limite) [0]: ", 0, 1000, 0)
            print("Corriendo...")
            resultados = [resolver(a, estado, limite_dfs=(lim or None) if a == DFS else None,
                                   medir_memoria=medir) for a in ALGORITMOS]
            tabla_comparacion(resultados)
        else:
            nombre = ALGORITMOS[op - 2]
            lim = None
            if nombre == DFS:
                lim = pedir_entero("Limite de profundidad (0 = sin limite) [0]: ", 0, 1000, 0) or None
            print("Corriendo...")
            mostrar_solucion(resolver(nombre, estado, limite_dfs=lim, medir_memoria=medir))
        input("\n(Enter para continuar)")


# ----------------------------------------------------------------------
# Conecta 4
# ----------------------------------------------------------------------

def mostrar_info_jugada(info, jugador):
    print(f"  La maquina ({NOMBRES[jugador]}) juega en la columna {info.columna + 1}")
    print(f"  Valor: {info.texto_valor()} | profundidad {info.profundidad}")
    print(f"  Nodos con poda: {info.nodos_poda:,}  ({info.tiempo_poda * 1000:.1f} ms, {info.podas} podas)")
    if info.nodos_sin_poda is not None:
        print(f"  Nodos sin poda: {info.nodos_sin_poda:,}  ({info.tiempo_sin_poda * 1000:.1f} ms)"
              f"  -> reduccion {info.reduccion():.1f} %")


def menu_conecta4():
    linea()
    print("CONECTA 4 vs LA MAQUINA  (X = Rojo, O = Amarillo, Rojo empieza)")
    prof = pedir_entero("Profundidad de la maquina (1-8) [5]: ", 1, 8, 5)
    empieza_humano = input("¿Quieres empezar tu? (S/n): ").strip().lower() != "n"
    comparar = prof <= 6 and input("¿Contar tambien nodos sin poda? (S/n): ").strip().lower() != "n"

    humano = JUGADOR1 if empieza_humano else JUGADOR2
    tablero = Tablero()
    turno = JUGADOR1
    total_con = total_sin = 0

    while True:
        print()
        print(tablero)
        if turno == humano:
            cols = [c + 1 for c in tablero.columnas_validas()]
            while True:
                c = pedir_entero(f"Tu turno ({NOMBRES[humano]}), columna {cols}: ", 1, 7)
                if tablero.puede_jugar(c - 1):
                    break
                print("  Esa columna esta llena.")
            col = c - 1
        else:
            print("La maquina esta pensando...")
            info = decidir_jugada(tablero, turno, prof, comparar)
            mostrar_info_jugada(info, turno)
            total_con += info.nodos_poda
            if info.nodos_sin_poda:
                total_sin += info.nodos_sin_poda
            col = info.columna

        fila = tablero.jugar(col, turno)
        if tablero.es_ganadora(fila, col, turno):
            print()
            print(tablero)
            print("\n¡Ganaste!" if turno == humano else "\nGano la maquina.")
            break
        if tablero.lleno():
            print()
            print(tablero)
            print("\nEmpate.")
            break
        turno = oponente(turno)

    if total_sin:
        print(f"\nTotal de la partida: {total_con:,} nodos con poda vs {total_sin:,} sin poda "
              f"({100 * (1 - total_con / total_sin):.1f} % menos)")
    input("\n(Enter para continuar)")


def menu_principal():
    while True:
        linea()
        print("PROYECTO 1 - ALGORITMOS DE BUSQUEDA (version consola)")
        print("  1. 8-Puzzle ponderado (DFS, BFS, UCS, A*)")
        print("  2. Conecta 4 contra la maquina (Minimax con poda alfa-beta)")
        print("  0. Salir")
        op = pedir_entero("Opcion: ", 0, 2)
        if op == 0:
            print("Chao!")
            return
        if op == 1:
            menu_puzzle()
        else:
            menu_conecta4()


def main():
    try:
        menu_principal()
    except (KeyboardInterrupt, EOFError):
        print("\nChao!")


if __name__ == "__main__":
    main()
