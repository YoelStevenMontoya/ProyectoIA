"""
Pestaña del 8-puzzle ponderado: elegir estado inicial, elegir algoritmo,
resolver, ver metricas y animar la solucion paso a paso.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from puzzle.problema import (N, META, ProblemaPuzzle, mezclar, texto_a_estado,
                             es_resoluble, peso_ficha)
from puzzle.solucionador import ALGORITMOS, DFS, resolver, pasos_legibles
from puzzle.casos import CASOS_PRUEBA
from interfaz.util import ejecutar_en_hilo, mezclar_color

TAM_CELDA = 90
MARGEN = 10
COLOR_LIVIANA = "#d6e6ff"
COLOR_PESADA = "#1d3f7a"
COLOR_FONDO = "#eef1f5"
COLOR_META = "#2e8b57"


class VistaPuzzle(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=10)

        self.estado_inicial = mezclar(20, semilla=2)
        self.resultado = None      # ultimo ResultadoBusqueda
        self.paso_actual = 0       # paso de la solucion que se esta mostrando
        self.animando = False
        self.ocupado = False       # hay un algoritmo corriendo
        self.costo_manual = 0
        self.movs_manual = 0
        self.costos_acumulados = [0]

        self._crear_tablero()
        self._crear_controles()
        self._crear_resultados()

        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        self._mostrar_estado_inicial()

    # ------------------------------------------------------------------
    # Construccion de la ventana
    # ------------------------------------------------------------------

    def _crear_tablero(self):
        marco = ttk.Frame(self)
        marco.grid(row=0, column=0, sticky="n", padx=(0, 15))

        lado = N * TAM_CELDA + 2 * MARGEN
        self.canvas = tk.Canvas(marco, width=lado, height=lado, bg=COLOR_FONDO,
                                highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._click_tablero)

        self.lbl_paso = ttk.Label(marco, text="", font=("Helvetica", 11))
        self.lbl_paso.pack(pady=(8, 2))
        self.lbl_info = ttk.Label(marco, text="Tip: haz clic en una ficha junto al hueco para moverla",
                                  foreground="#666")
        self.lbl_info.pack()

        barra = ttk.Frame(marco)
        barra.pack(pady=8)
        self.btn_inicio = ttk.Button(barra, text="|<", width=4, command=lambda: self._ir_a_paso(0))
        self.btn_atras = ttk.Button(barra, text="<", width=4, command=lambda: self._ir_a_paso(self.paso_actual - 1))
        self.btn_animar = ttk.Button(barra, text="Animar", width=9, command=self._alternar_animacion)
        self.btn_adelante = ttk.Button(barra, text=">", width=4, command=lambda: self._ir_a_paso(self.paso_actual + 1))
        self.btn_fin = ttk.Button(barra, text=">|", width=4, command=self._ir_al_final)
        for b in (self.btn_inicio, self.btn_atras, self.btn_animar, self.btn_adelante, self.btn_fin):
            b.pack(side="left", padx=2)

        vel = ttk.Frame(marco)
        vel.pack()
        ttk.Label(vel, text="Velocidad:").pack(side="left")
        self.velocidad = tk.IntVar(value=5)
        ttk.Scale(vel, from_=1, to=10, variable=self.velocidad, orient="horizontal",
                  length=160).pack(side="left", padx=5)

        leyenda = ttk.Label(marco, foreground="#444", justify="center",
                            text="Mover una ficha cuesta su numero\n(las mas oscuras son las mas pesadas)")
        leyenda.pack(pady=(12, 0))

    def _crear_controles(self):
        marco = ttk.Frame(self)
        marco.grid(row=0, column=1, sticky="n", padx=(0, 15))

        # --- estado inicial ---
        caja = ttk.LabelFrame(marco, text=" Estado inicial ", padding=8)
        caja.pack(fill="x")

        ttk.Label(caja, text="Escribelo por filas (0 = hueco):").pack(anchor="w")
        fila = ttk.Frame(caja)
        fila.pack(fill="x", pady=3)
        self.entrada_estado = ttk.Entry(fila, width=22)
        self.entrada_estado.pack(side="left")
        self.entrada_estado.bind("<Return>", lambda e: self._aplicar_estado_escrito())
        ttk.Button(fila, text="Usar", command=self._aplicar_estado_escrito).pack(side="left", padx=4)

        fila2 = ttk.Frame(caja)
        fila2.pack(fill="x", pady=3)
        ttk.Label(fila2, text="Movimientos:").pack(side="left")
        self.movs_mezcla = tk.IntVar(value=20)
        ttk.Spinbox(fila2, from_=1, to=200, textvariable=self.movs_mezcla, width=5).pack(side="left", padx=4)
        ttk.Button(fila2, text="Mezclar", command=self._mezclar).pack(side="left")

        ttk.Label(caja, text="Casos de prueba:").pack(anchor="w", pady=(6, 0))
        self.combo_casos = ttk.Combobox(caja, values=list(CASOS_PRUEBA.keys()), state="readonly", width=34)
        self.combo_casos.pack(fill="x")
        self.combo_casos.bind("<<ComboboxSelected>>", self._elegir_caso)

        ttk.Button(caja, text="Poner en la meta", command=lambda: self._cambiar_estado(META)).pack(anchor="w", pady=(6, 0))

        # --- algoritmo ---
        caja2 = ttk.LabelFrame(marco, text=" Algoritmo ", padding=8)
        caja2.pack(fill="x", pady=10)

        self.algoritmo = tk.StringVar(value=ALGORITMOS[3])
        for nombre in ALGORITMOS:
            ttk.Radiobutton(caja2, text=nombre, value=nombre, variable=self.algoritmo).pack(anchor="w", pady=1)

        fila3 = ttk.Frame(caja2)
        fila3.pack(fill="x", pady=(8, 0))
        ttk.Label(fila3, text="Limite DFS (0 = sin limite):").pack(side="left")
        self.limite_dfs = tk.IntVar(value=0)
        ttk.Spinbox(fila3, from_=0, to=500, textvariable=self.limite_dfs, width=5).pack(side="left", padx=4)

        self.medir_memoria = tk.BooleanVar(value=False)
        ttk.Checkbutton(caja2, text="Medir memoria con tracemalloc (mas lento)",
                        variable=self.medir_memoria).pack(anchor="w", pady=(6, 0))

        self.btn_resolver = ttk.Button(marco, text="Resolver", command=self._resolver, style="Accion.TButton")
        self.btn_resolver.pack(fill="x", pady=(0, 5))
        self.btn_comparar = ttk.Button(marco, text="Comparar los 5 algoritmos", command=self._comparar_todos)
        self.btn_comparar.pack(fill="x")

        self.lbl_estado = ttk.Label(marco, text="", foreground="#b35c00")
        self.lbl_estado.pack(pady=6)

    def _crear_resultados(self):
        marco = ttk.Frame(self)
        marco.grid(row=0, column=2, sticky="nsew")
        marco.rowconfigure(1, weight=1)
        marco.rowconfigure(3, weight=1)
        marco.columnconfigure(0, weight=1)

        ttk.Label(marco, text="Resultado", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w")
        cont = ttk.Frame(marco)
        cont.grid(row=1, column=0, sticky="nsew", pady=(2, 8))
        cont.columnconfigure(0, weight=1)
        cont.columnconfigure(1, weight=1)
        cont.rowconfigure(0, weight=1)

        self.txt_metricas = tk.Text(cont, width=34, height=12, font=("Courier", 9), wrap="word",
                                    state="disabled", relief="solid", borderwidth=1)
        self.txt_metricas.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        pasos = ttk.Frame(cont)
        pasos.grid(row=0, column=1, sticky="nsew")
        pasos.rowconfigure(0, weight=1)
        pasos.columnconfigure(0, weight=1)
        self.lista_pasos = tk.Listbox(pasos, width=30, font=("Courier", 9), activestyle="none")
        self.lista_pasos.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(pasos, orient="vertical", command=self.lista_pasos.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.lista_pasos.config(yscrollcommand=barra.set)
        self.lista_pasos.bind("<<ListboxSelect>>", self._click_lista)

        fila_tit = ttk.Frame(marco)
        fila_tit.grid(row=2, column=0, sticky="ew")
        ttk.Label(fila_tit, text="Comparacion (mismo estado inicial)",
                  font=("Helvetica", 12, "bold")).pack(side="left")
        ttk.Button(fila_tit, text="Limpiar tabla", command=self._limpiar_tabla).pack(side="right")

        columnas = ("alg", "pasos", "costo", "exp", "gen", "mem", "kb", "ms")
        titulos = ("Algoritmo", "Pasos", "Costo", "Expand.", "Generad.",
                   "Mem. nodos", "Mem. KB", "ms")
        anchos = (165, 48, 56, 68, 70, 84, 70, 58)
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=6)
        for col, tit, ancho in zip(columnas, titulos, anchos):
            self.tabla.heading(col, text=tit)
            self.tabla.column(col, width=ancho, anchor="w" if col == "alg" else "e", stretch=(col == "alg"))
        self.tabla.grid(row=3, column=0, sticky="nsew", pady=(2, 0))
        barra_h = ttk.Scrollbar(marco, orient="horizontal", command=self.tabla.xview)
        barra_h.grid(row=4, column=0, sticky="ew")
        self.tabla.config(xscrollcommand=barra_h.set)

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------

    def _dibujar(self, estado):
        self.canvas.delete("all")
        es_meta = tuple(estado) == META
        for i, ficha in enumerate(estado):
            fila, col = divmod(i, N)
            x0 = MARGEN + col * TAM_CELDA + 4
            y0 = MARGEN + fila * TAM_CELDA + 4
            x1 = x0 + TAM_CELDA - 8
            y1 = y0 + TAM_CELDA - 8
            if ficha == 0:
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="#dde2ea", outline="#c3cad6")
                continue
            t = (peso_ficha(ficha) - 1) / 7  # 0 para la ficha 1, 1 para la ficha 8
            color = COLOR_META if es_meta else mezclar_color(COLOR_LIVIANA, COLOR_PESADA, t)
            color_texto = "white" if (t > 0.45 or es_meta) else "#1d2b44"
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#0f2346", width=2)
            self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2 - 6, text=str(ficha),
                                    font=("Helvetica", 30, "bold"), fill=color_texto)
            self.canvas.create_text((x0 + x1) / 2, y1 - 14, text=f"costo {peso_ficha(ficha)}",
                                    font=("Helvetica", 9), fill=color_texto)

    def _mostrar_estado_inicial(self):
        self.entrada_estado.delete(0, "end")
        self.entrada_estado.insert(0, " ".join(str(x) for x in self.estado_inicial))
        self._dibujar(self.estado_inicial)
        if self.movs_manual:
            self.lbl_paso.config(text=f"Movimientos manuales: {self.movs_manual}  |  costo: {self.costo_manual}")
        else:
            self.lbl_paso.config(text="Estado inicial")

    def _escribir_metricas(self, texto):
        self.txt_metricas.config(state="normal")
        self.txt_metricas.delete("1.0", "end")
        self.txt_metricas.insert("1.0", texto)
        self.txt_metricas.config(state="disabled")

    # ------------------------------------------------------------------
    # Cambiar el estado inicial
    # ------------------------------------------------------------------

    def _cambiar_estado(self, estado, reiniciar_manual=True):
        if self.ocupado:
            return
        self._detener_animacion()
        self.estado_inicial = tuple(estado)
        self.resultado = None
        self.paso_actual = 0
        if reiniciar_manual:
            self.movs_manual = 0
            self.costo_manual = 0
        self.lista_pasos.delete(0, "end")
        self._escribir_metricas("")
        self._mostrar_estado_inicial()

    def _aplicar_estado_escrito(self):
        try:
            estado = texto_a_estado(self.entrada_estado.get())
        except ValueError as e:
            messagebox.showerror("Estado invalido", str(e))
            return
        if not es_resoluble(estado):
            messagebox.showerror("Sin solucion",
                                 "Ese estado no se puede resolver: tiene un numero impar de inversiones.\n"
                                 "Prueba intercambiando dos fichas cualquiera (que no sean el hueco).")
            return
        self.combo_casos.set("")
        self._cambiar_estado(estado)

    def _mezclar(self):
        try:
            movs = int(self.movs_mezcla.get())
        except (ValueError, tk.TclError):
            movs = 20
        self.combo_casos.set("")
        self._cambiar_estado(mezclar(max(1, movs)))

    def _elegir_caso(self, _evento=None):
        nombre = self.combo_casos.get()
        if nombre in CASOS_PRUEBA:
            self._cambiar_estado(CASOS_PRUEBA[nombre][0])

    def _click_tablero(self, evento):
        """Permite jugar a mano moviendo una ficha que este junto al hueco."""
        if self.ocupado or self.animando:
            return
        col = (evento.x - MARGEN) // TAM_CELDA
        fila = (evento.y - MARGEN) // TAM_CELDA
        if not (0 <= fila < N and 0 <= col < N):
            return

        # si hay una solucion cargada, se juega desde el paso que se esta viendo
        estado = self.resultado.estados[self.paso_actual] if self.resultado and self.resultado.exito else self.estado_inicial
        hueco = estado.index(0)
        fh, ch = divmod(hueco, N)
        if abs(fh - fila) + abs(ch - col) != 1:
            return

        pos = fila * N + col
        nuevo = list(estado)
        ficha = nuevo[pos]
        nuevo[hueco], nuevo[pos] = ficha, 0
        self.movs_manual += 1
        self.costo_manual += peso_ficha(ficha)
        self.combo_casos.set("")
        self._cambiar_estado(nuevo, reiniciar_manual=False)
        if tuple(nuevo) == META:
            self.lbl_paso.config(text=f"Resuelto a mano en {self.movs_manual} movimientos, costo {self.costo_manual}")

    # ------------------------------------------------------------------
    # Correr algoritmos
    # ------------------------------------------------------------------

    def _bloquear(self, si):
        self.ocupado = si
        estado = "disabled" if si else "normal"
        self.btn_resolver.config(state=estado)
        self.btn_comparar.config(state=estado)
        self.lbl_estado.config(text="Buscando..." if si else "")
        self.config(cursor="watch" if si else "")

    def _leer_limite(self):
        try:
            lim = int(self.limite_dfs.get())
        except (ValueError, tk.TclError):
            lim = 0
        return lim if lim > 0 else None

    def _resolver(self):
        if self.ocupado:
            return
        self._detener_animacion()
        nombre = self.algoritmo.get()
        estado = self.estado_inicial
        limite = self._leer_limite()
        memoria = self.medir_memoria.get()

        self._bloquear(True)
        ejecutar_en_hilo(self,
                         lambda: resolver(nombre, estado, limite_dfs=limite, medir_memoria=memoria),
                         self._mostrar_resultado,
                         self._error)

    def _error(self, e):
        self._bloquear(False)
        messagebox.showerror("Error", f"Algo fallo al ejecutar el algoritmo:\n{e}")

    def _mostrar_resultado(self, res, agregar_a_tabla=True):
        self._bloquear(False)
        self.resultado = res
        self.paso_actual = 0
        self.movs_manual = 0
        self.costo_manual = 0

        # costo acumulado en cada paso (se calcula una vez para no repetirlo al animar)
        self.costos_acumulados = [0]
        if res.exito:
            problema = ProblemaPuzzle(res.estados[0])
            for i, accion in enumerate(res.acciones):
                c = problema.costo_accion(res.estados[i], accion, res.estados[i + 1])
                self.costos_acumulados.append(self.costos_acumulados[-1] + c)

        texto = res.resumen()
        if res.exito and res.algoritmo.startswith("DFS") and res.profundidad > 100:
            texto += ("\n\nOjo: DFS no es optimo, por eso el\ncamino es tan largo. "
                      "Prueba ponerle\nun limite de profundidad (ej. 30).")
        self._escribir_metricas(texto)

        self.lista_pasos.delete(0, "end")
        if res.exito:
            pasos = pasos_legibles(res.estados, res.acciones)
            self.lista_pasos.insert("end", "0. Estado inicial",
                                    *[f"{i}. {p}" for i, p in enumerate(pasos, start=1)])
        if agregar_a_tabla:
            self._agregar_a_tabla(res)
        self._ir_a_paso(0)

    def _agregar_a_tabla(self, res):
        kb = f"{res.memoria_kb:.1f}" if res.memoria_kb is not None else "-"
        self.tabla.insert("", "end", values=(
            res.algoritmo,
            res.profundidad if res.exito else "-",
            res.costo if res.exito else "-",
            res.nodos_expandidos,
            res.nodos_generados,
            res.max_en_memoria,
            kb,
            f"{res.tiempo * 1000:.1f}",
        ))
        hijos = self.tabla.get_children()
        if hijos:
            self.tabla.see(hijos[-1])

    def _limpiar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

    def _comparar_todos(self):
        if self.ocupado:
            return
        self._detener_animacion()
        estado = self.estado_inicial
        limite = self._leer_limite()
        memoria = self.medir_memoria.get()

        def trabajo():
            return [resolver(a, estado, limite_dfs=limite if a == DFS else None, medir_memoria=memoria)
                    for a in ALGORITMOS]

        def terminar(resultados):
            self._bloquear(False)
            self._limpiar_tabla()
            for r in resultados:
                self._agregar_a_tabla(r)
            # se deja cargada la solucion de A* h2 para poder animarla
            self.algoritmo.set(ALGORITMOS[3])
            self._mostrar_resultado(resultados[3], agregar_a_tabla=False)

        self._bloquear(True)
        self.lbl_estado.config(text="Corriendo los 5 algoritmos...")
        ejecutar_en_hilo(self, trabajo, terminar, self._error)

    # ------------------------------------------------------------------
    # Navegar / animar la solucion
    # ------------------------------------------------------------------

    def _ir_a_paso(self, paso):
        if not self.resultado or not self.resultado.exito:
            self._mostrar_estado_inicial()
            return
        total = len(self.resultado.estados) - 1
        paso = max(0, min(paso, total))
        self.paso_actual = paso
        estado = self.resultado.estados[paso]
        self._dibujar(estado)

        costo = self.costos_acumulados[paso]
        self.lbl_paso.config(text=f"Paso {paso} de {total}  |  costo acumulado: {costo}")

        self.lista_pasos.selection_clear(0, "end")
        self.lista_pasos.selection_set(paso)
        self.lista_pasos.see(paso)

    def _ir_al_final(self):
        if self.resultado and self.resultado.exito:
            self._ir_a_paso(len(self.resultado.estados) - 1)

    def _click_lista(self, _evento=None):
        sel = self.lista_pasos.curselection()
        if sel and not self.animando:
            self._ir_a_paso(sel[0])

    def _alternar_animacion(self):
        if self.animando:
            self._detener_animacion()
            return
        if not self.resultado or not self.resultado.exito:
            return
        if self.paso_actual >= len(self.resultado.estados) - 1:
            self._ir_a_paso(0)
        self.animando = True
        self.btn_animar.config(text="Pausar")
        self._siguiente_cuadro()

    def _siguiente_cuadro(self):
        if not self.animando:
            return
        if self.paso_actual >= len(self.resultado.estados) - 1:
            self._detener_animacion()
            return
        self._ir_a_paso(self.paso_actual + 1)
        espera = int(1100 / self.velocidad.get())  # velocidad 1 -> 1.1 s, velocidad 10 -> 0.11 s
        self.after(espera, self._siguiente_cuadro)

    def _detener_animacion(self):
        self.animando = False
        self.btn_animar.config(text="Animar")
