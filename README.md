# Proyecto 1 – Algoritmos de Búsqueda

Aplicación en Python que resuelve problemas con los cinco algoritmos de búsqueda vistos en el curso:

| Modo | Problema | Algoritmos |
|------|----------|------------|
| Un agente | **8-puzzle ponderado**: mover la ficha *k* cuesta *k* | DFS, BFS, Costo uniforme (UCS), A* con heurística propia |
| Adversario | **Conecta 4** contra la máquina | Minimax con poda alfa-beta (y sin poda para comparar) |

Elegimos un 8-puzzle con fichas de distinto peso porque en el 8-puzzle normal todos los movimientos cuestan 1 y UCS terminaría siendo igual a BFS. Con pesos, el camino con menos pasos ya no es necesariamente el más barato, y eso permite ver la diferencia entre BFS, UCS y A*.

## Integrantes

Cristhian Ramírez 2310123 
Yoel Steven Montoya 2416571 
Gabriel de Jesús Arango 1823077 

**Curso:** Inteligencia Artificial – 2026
**Docente:** Andres Mauricio Valencia

## Requisitos

- Python 3.9 o superior.
- Tkinter (viene incluido con Python en Windows y macOS).
  En Linux toca instalarlo aparte: `sudo apt install python3-tk`.
- Opcional: `matplotlib`, solo para que `comparar.py` genere las gráficas en PNG.

**No se usa ninguna librería externa para los algoritmos**, todos están programados por el grupo.

## Instalación

```bash
git clone <url-del-repositorio>
cd proyecto1
# opcional, solo para las graficas del script de comparacion:
pip install -r requirements.txt
```

## Ejecución

Todos los comandos se corren desde la carpeta del proyecto.

| Comando | Qué hace |
|---------|----------|
| `python main.py` | Abre la interfaz gráfica |
| `python main.py --consola` | Versión de consola (respaldo si no hay Tkinter o falla la ventana) |
| `python comparar.py` | Corre todos los algoritmos sobre los casos de prueba y genera las tablas del informe (en consola y en `resultados/*.csv`, más gráficas PNG si hay matplotlib) |
| `python comparar.py --torneo` | Lo mismo + torneo IA vs IA que usamos para ajustar la función de evaluación |
| `python -m unittest discover tests` | Pruebas automáticas (21 pruebas) |

En algunos equipos el comando es `python3` en vez de `python`.

## Uso de la interfaz

### Pestaña 1: 8-Puzzle ponderado

1. Escoger el estado inicial: escribirlo (ej. `1 2 3 4 0 5 7 8 6`, el 0 es el hueco), darle a **Mezclar**, o escoger uno de los **casos de prueba**. También se puede jugar a mano haciendo clic en las fichas que están junto al hueco.
2. Elegir el algoritmo (DFS, BFS, UCS, A* con h2 o A* con h1). Para DFS se puede poner un límite de profundidad (0 = sin límite).
3. **Resolver**: se muestran la solución paso a paso, el costo, la profundidad, los nodos expandidos y generados, el máximo de nodos en memoria y el tiempo. Si se marca *Medir memoria* también sale el pico de memoria en KB (con `tracemalloc`).
4. Con los botones `|<  <  Animar  >  >|` se recorre o anima la solución.
5. **Comparar los 5 algoritmos** llena la tabla de abajo con las métricas de todos sobre el mismo estado.

### Pestaña 2: Conecta 4

- **Humano vs Máquina**: se escoge quién empieza y la profundidad de la máquina (1 a 8). Se juega haciendo clic en la columna.
- **Máquina vs Máquina**: cada color con su propia profundidad.
- Por cada jugada de la máquina se muestran la columna elegida, el valor minimax, los nodos evaluados **con poda** y **sin poda**, el porcentaje de reducción, el número de podas y los tiempos. Sin poda solo se calcula hasta profundidad 6 porque más allá se demora demasiado.

## Modelado (resumen)

**8-puzzle ponderado**
- Estado: tupla de 9 enteros leída por filas, `0` = hueco.
- Acciones: mover el hueco `ARRIBA`, `ABAJO`, `IZQUIERDA`, `DERECHA` (si no se sale del tablero).
- Transición: intercambiar el hueco con la ficha vecina.
- Meta: `(1, 2, 3, 4, 5, 6, 7, 8, 0)`.
- Costo de una acción: el número de la ficha que se mueve (de 1 a 8).
- Heurísticas para A*:
  - **h2 – Manhattan ponderada** (la principal): `Σ k · manhattan(k)`.
  - **h1 – Fichas mal ubicadas ponderadas**: `Σ k` de las fichas fuera de su lugar.
  - Ambas son admisibles y consistentes; h2 domina a h1.

**Conecta 4**
- Tablero 6×7, juegan Rojo (empieza) y Amarillo por turnos.
- Terminal: 4 en línea o tablero lleno. Utilidad: ±1 000 000 (más la profundidad restante, para preferir ganar rápido) o 0 en empate.
- Función de evaluación: puntúa las 69 ventanas de 4 casillas (amenazas de 3, líneas de 2, con más peso a las amenazas del rival) más un bono por ocupar casillas centrales.
- Orden de exploración de columnas: centro primero (mejora la poda).

## Estructura del proyecto

```
proyecto1/
├── main.py                 # punto de entrada (interfaz grafica o consola)
├── consola.py              # version de consola
├── comparar.py             # tablas y graficas para el analisis comparativo
├── requirements.txt
├── busqueda/               # algoritmos genericos (sirven para cualquier problema)
│   ├── nodo.py             # nodo del arbol de busqueda
│   ├── resultado.py        # metricas que reporta cada algoritmo
│   ├── dfs.py              # pila (LIFO)
│   ├── bfs.py              # cola (FIFO)
│   ├── ucs.py              # cola de prioridad por g(n)
│   └── a_estrella.py       # cola de prioridad por f(n) = g(n) + h(n)
├── puzzle/
│   ├── problema.py         # formulacion del 8-puzzle ponderado
│   ├── heuristicas.py      # h1 y h2
│   ├── casos.py            # casos de prueba fijos
│   └── solucionador.py     # corre un algoritmo y mide tiempo/memoria
├── conecta4/
│   ├── tablero.py
│   ├── evaluacion.py       # funcion de evaluacion
│   └── minimax.py          # minimax con y sin poda alfa-beta
├── interfaz/               # Tkinter
│   ├── app.py
│   ├── vista_puzzle.py
│   ├── vista_conecta4.py
│   └── util.py
└── tests/                  # pruebas con unittest
```

## Notas

- **DFS sin límite** encuentra una solución, pero larguísima (decenas de miles de pasos), porque no es óptimo. Es lo esperado. Con un límite (ej. 30) da caminos cortos, aunque si el límite es menor que la solución óptima no encuentra nada.
- **BFS** da la solución con menos pasos, pero no siempre la más barata. En el *Caso 2* BFS encuentra 18 pasos con costo 107, mientras que UCS y A* encuentran 20 pasos con costo 91.
- La métrica *Max. nodos en memoria* es el número de estados distintos guardados (frontera + explorados). La memoria en KB se mide aparte con `tracemalloc` porque esa medición hace más lento el programa.

## Fuentes y herramientas de apoyo

- Russell, S., & Norvig, P. (2021). *Artificial Intelligence: A Modern Approach* (4.ª ed.). Pearson. Capítulos 3 y 5.
- Documentación de Python: `heapq`, `collections.deque`, `tkinter`, `tracemalloc`.
- Herramientas de IA usadas como apoyo: _declarar aquí y en el informe cuáles se usaron y para qué._
