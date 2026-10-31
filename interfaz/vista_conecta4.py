"""
Pestaña de Conecta 4: modo adversario con minimax y poda alfa-beta.
Se puede jugar Humano vs Maquina o poner a jugar Maquina vs Maquina.
Por cada jugada de la maquina se muestran los nodos con y sin poda.
"""

import tkinter as tk
from tkinter import ttk

from conecta4.tablero import Tablero, FILAS, COLUMNAS, JUGADOR1, JUGADOR2, NOMBRES, oponente
from conecta4.minimax import decidir_jugada
from interfaz.util import ejecutar_en_hilo

CELDA = 72
COLOR_TABLERO = "#1f4fa3"
COLORES = {JUGADOR1: "#d7263d", JUGADOR2: "#f4c430"}
COLOR_HUECO = "#f4f6fa"

# Sin poda, profundidad 7 ya son cerca de un millon de nodos por jugada
# (varios segundos o minutos en Python), por eso solo se compara hasta 6.
LIMITE_SIN_PODA = 6


class VistaConecta4(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=10)
        self.tablero = Tablero()
        self.turno = JUGADOR1
        self.terminado = False
        self.pensando = False
        self.pausado = False
        self.partida_id = 0          # sirve para ignorar resultados de una partida vieja
        self.jugador_humano = JUGADOR1
        self.historial = []          # (numero, jugador, InfoJugada)
        self.num_jugada = 0
        self.columna_hover = None
        self.linea_ganadora = []

        self._crear_tablero()
        self._crear_panel()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.nueva_partida()

    # ------------------------------------------------------------------
    # Construccion
    # ------------------------------------------------------------------

    def _crear_tablero(self):
        marco = ttk.Frame(self)
        marco.grid(row=0, column=0, sticky="n", padx=(0, 15))
        ancho = COLUMNAS * CELDA
        alto = (FILAS + 1) * CELDA  # una fila extra arriba para la ficha "flotando"
        self.canvas = tk.Canvas(marco, width=ancho, height=alto, bg="white", highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._click)
        self.canvas.bind("<Motion>", self._mover_mouse)
        self.canvas.bind("<Leave>", lambda e: self._set_hover(None))

        self.lbl_turno = ttk.Label(marco, text="", font=("Helvetica", 14, "bold"))
        self.lbl_turno.pack(pady=8)

    def _crear_panel(self):
        panel = ttk.Frame(self)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)
        panel.rowconfigure(2, weight=1)

        # --- configuracion ---
        conf = ttk.LabelFrame(panel, text=" Configuracion de la partida ", padding=8)
        conf.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.modo = tk.StringVar(value="hm")
        ttk.Radiobutton(conf, text="Humano vs Maquina", value="hm", variable=self.modo,
                        command=self._cambio_modo).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(conf, text="Maquina vs Maquina", value="mm", variable=self.modo,
                        command=self._cambio_modo).grid(row=1, column=0, columnspan=2, sticky="w")

        # opciones de humano vs maquina
        self.marco_hm = ttk.Frame(conf)
        self.marco_hm.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Label(self.marco_hm, text="Empieza:").grid(row=0, column=0, sticky="w")
        self.empieza = tk.StringVar(value="humano")
        ttk.Radiobutton(self.marco_hm, text="Yo (Rojo)", value="humano",
                        variable=self.empieza).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(self.marco_hm, text="Maquina", value="maquina",
                        variable=self.empieza).grid(row=0, column=2, sticky="w")
        ttk.Label(self.marco_hm, text="Profundidad maquina:").grid(row=1, column=0, columnspan=2, sticky="w", pady=4)
        self.prof_maquina = tk.IntVar(value=5)
        ttk.Spinbox(self.marco_hm, from_=1, to=8, textvariable=self.prof_maquina, width=4).grid(row=1, column=2, sticky="w")

        # opciones de maquina vs maquina
        self.marco_mm = ttk.Frame(conf)
        ttk.Label(self.marco_mm, text="Profundidad Rojo:").grid(row=0, column=0, sticky="w")
        self.prof_rojo = tk.IntVar(value=5)
        ttk.Spinbox(self.marco_mm, from_=1, to=8, textvariable=self.prof_rojo, width=4).grid(row=0, column=1, padx=4)
        ttk.Label(self.marco_mm, text="Profundidad Amarillo:").grid(row=1, column=0, sticky="w", pady=4)
        self.prof_amarillo = tk.IntVar(value=3)
        ttk.Spinbox(self.marco_mm, from_=1, to=8, textvariable=self.prof_amarillo, width=4).grid(row=1, column=1, padx=4)

        self.comparar_sin_poda = tk.BooleanVar(value=True)
        ttk.Checkbutton(conf, text=f"Contar tambien nodos SIN poda (hasta prof. {LIMITE_SIN_PODA})",
                        variable=self.comparar_sin_poda).grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))

        botones = ttk.Frame(conf)
        botones.grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Button(botones, text="Nueva partida", style="Accion.TButton",
                   command=self.nueva_partida).pack(side="left")
        self.btn_pausa = ttk.Button(botones, text="Pausar", command=self._alternar_pausa)
        self.btn_pausa.pack(side="left", padx=6)

        # --- info de la ultima jugada ---
        info = ttk.LabelFrame(panel, text=" Ultima jugada de la maquina ", padding=8)
        info.grid(row=0, column=1, sticky="nsew")
        self.lbls_info = {}
        campos = [("col", "Columna elegida"), ("valor", "Valor minimax"), ("prof", "Profundidad limite"),
                  ("con", "Nodos CON poda"), ("sin", "Nodos SIN poda"), ("red", "Reduccion"),
                  ("podas", "Podas (cortes)"), ("t_con", "Tiempo con poda"), ("t_sin", "Tiempo sin poda")]
        for i, (clave, texto) in enumerate(campos):
            ttk.Label(info, text=texto + ":").grid(row=i, column=0, sticky="w")
            lbl = ttk.Label(info, text="-", font=("Helvetica", 10, "bold"))
            lbl.grid(row=i, column=1, sticky="w", padx=8)
            self.lbls_info[clave] = lbl

        ttk.Label(panel, text="Historial de jugadas de la maquina",
                  font=("Helvetica", 12, "bold")).grid(row=1, column=0, columnspan=2, sticky="w", pady=(12, 2))

        columnas = ("n", "jug", "prof", "col", "con", "sin", "red", "ms")
        titulos = ("#", "Jugador", "Prof.", "Col.", "Con poda", "Sin poda", "Reduccion", "Tiempo ms")
        anchos = (40, 80, 50, 45, 90, 90, 85, 85)
        self.tabla = ttk.Treeview(panel, columns=columnas, show="headings", height=10)
        for c, t, a in zip(columnas, titulos, anchos):
            self.tabla.heading(c, text=t)
            self.tabla.column(c, width=a, anchor="e" if c not in ("jug",) else "w")
        self.tabla.grid(row=2, column=0, columnspan=2, sticky="nsew")

        self.lbl_totales = ttk.Label(panel, text="", font=("Helvetica", 10))
        self.lbl_totales.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

        ttk.Label(panel, foreground="#555", justify="left",
                  text="Valor > 0: la posicion favorece a la maquina que juega; valor < 0: favorece al rival.\n"
                       "Sin poda y con poda eligen la MISMA jugada; la poda solo evita revisar ramas inutiles.").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(6, 0))

    # ------------------------------------------------------------------
    # Partida
    # ------------------------------------------------------------------

    def _cambio_modo(self):
        if self.modo.get() == "hm":
            self.marco_mm.grid_forget()
            self.marco_hm.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))
        else:
            self.marco_hm.grid_forget()
            self.marco_mm.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))

    def nueva_partida(self):
        self.partida_id += 1
        self.tablero = Tablero()
        self.turno = JUGADOR1  # Rojo siempre empieza
        self.terminado = False
        self.pensando = False
        self.pausado = False
        self.btn_pausa.config(text="Pausar")
        self.historial = []
        self.num_jugada = 0
        self.linea_ganadora = []
        if self.modo.get() == "hm":
            self.jugador_humano = JUGADOR1 if self.empieza.get() == "humano" else JUGADOR2
        else:
            self.jugador_humano = None
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for lbl in self.lbls_info.values():
            lbl.config(text="-")
        self.lbl_totales.config(text="")
        self._dibujar()
        self._siguiente_turno()

    def _es_turno_maquina(self):
        return self.jugador_humano is None or self.turno != self.jugador_humano

    def _profundidad_de(self, jugador):
        try:
            if self.jugador_humano is not None:
                p = int(self.prof_maquina.get())
            elif jugador == JUGADOR1:
                p = int(self.prof_rojo.get())
            else:
                p = int(self.prof_amarillo.get())
        except (ValueError, tk.TclError):
            p = 4
        return max(1, min(p, 8))

    def _siguiente_turno(self):
        if self.terminado or self.pausado:
            return
        if self._es_turno_maquina():
            self._turno_maquina()
        else:
            self.lbl_turno.config(text=f"Tu turno ({NOMBRES[self.turno]}): haz clic en una columna",
                                  foreground=COLORES[self.turno] if self.turno == JUGADOR1 else "#b08800")

    def _turno_maquina(self):
        jugador = self.turno
        prof = self._profundidad_de(jugador)
        comparar = self.comparar_sin_poda.get() and prof <= LIMITE_SIN_PODA
        copia = self.tablero.copia()
        id_partida = self.partida_id

        self.pensando = True
        self.lbl_turno.config(text=f"La maquina ({NOMBRES[jugador]}) esta pensando...", foreground="#444")

        def listo(info):
            if id_partida != self.partida_id:
                return  # se empezo otra partida mientras pensaba
            self.pensando = False
            self.num_jugada += 1
            self.historial.append((self.num_jugada, jugador, info))
            self._mostrar_info(info, jugador)
            self._aplicar_jugada(info.columna, jugador)
            # en maquina vs maquina se espera un poco para que se alcance a ver
            espera = 600 if self.jugador_humano is None else 50
            self.after(espera, self._siguiente_turno)

        def fallo(e):
            self.pensando = False
            self.lbl_turno.config(text=f"Error en minimax: {e}", foreground="red")

        ejecutar_en_hilo(self, lambda: decidir_jugada(copia, jugador, prof, comparar), listo, fallo)

    def _aplicar_jugada(self, col, jugador):
        fila = self.tablero.jugar(col, jugador)
        if self.jugador_humano is not None and jugador == self.jugador_humano:
            self.num_jugada += 1
        if self.tablero.es_ganadora(fila, col, jugador):
            self.terminado = True
            self.linea_ganadora = self.tablero.linea_ganadora(fila, col, jugador)
            if self.jugador_humano is None:
                texto = f"Gana {NOMBRES[jugador]}!"
            elif jugador == self.jugador_humano:
                texto = "Ganaste!"
            else:
                texto = f"Gana la maquina ({NOMBRES[jugador]})"
            self.lbl_turno.config(text=texto, foreground=COLORES[jugador] if jugador == JUGADOR1 else "#b08800")
        elif self.tablero.lleno():
            self.terminado = True
            self.lbl_turno.config(text="Empate, tablero lleno", foreground="#444")
        else:
            self.turno = oponente(jugador)
        self._dibujar()

    def _click(self, evento):
        if self.terminado or self.pensando or self._es_turno_maquina():
            return
        col = evento.x // CELDA
        if not self.tablero.puede_jugar(col):
            return
        self._aplicar_jugada(col, self.turno)
        self._siguiente_turno()

    def _alternar_pausa(self):
        if self.jugador_humano is not None:
            return  # solo tiene sentido en maquina vs maquina
        self.pausado = not self.pausado
        self.btn_pausa.config(text="Continuar" if self.pausado else "Pausar")
        if not self.pausado and not self.pensando:
            self._siguiente_turno()

    # ------------------------------------------------------------------
    # Mostrar info
    # ------------------------------------------------------------------

    def _mostrar_info(self, info, jugador):
        self.lbls_info["col"].config(text=f"{info.columna + 1}  ({NOMBRES[jugador]})")
        self.lbls_info["valor"].config(text=info.texto_valor())
        self.lbls_info["prof"].config(text=str(info.profundidad))
        self.lbls_info["con"].config(text=f"{info.nodos_poda:,}")
        self.lbls_info["podas"].config(text=f"{info.podas:,}")
        self.lbls_info["t_con"].config(text=f"{info.tiempo_poda * 1000:.1f} ms")
        if info.nodos_sin_poda is not None:
            self.lbls_info["sin"].config(text=f"{info.nodos_sin_poda:,}")
            self.lbls_info["red"].config(text=f"{info.reduccion():.1f} %")
            self.lbls_info["t_sin"].config(text=f"{info.tiempo_sin_poda * 1000:.1f} ms")
        else:
            motivo = "no calculado" if not self.comparar_sin_poda.get() else f"prof. > {LIMITE_SIN_PODA}"
            for clave in ("sin", "red", "t_sin"):
                self.lbls_info[clave].config(text=motivo)

        sin = f"{info.nodos_sin_poda:,}" if info.nodos_sin_poda is not None else "-"
        red = f"{info.reduccion():.1f} %" if info.nodos_sin_poda is not None else "-"
        self.tabla.insert("", "end", values=(self.num_jugada, NOMBRES[jugador], info.profundidad,
                                             info.columna + 1, f"{info.nodos_poda:,}", sin, red,
                                             f"{info.tiempo_poda * 1000:.1f}"))
        self.tabla.see(self.tabla.get_children()[-1])

        # totales (solo de las jugadas donde se calcularon las dos cosas)
        comparables = [i for _, _, i in self.historial if i.nodos_sin_poda is not None]
        total_con = sum(i.nodos_poda for _, _, i in self.historial)
        texto = f"Total nodos con poda: {total_con:,}"
        if comparables:
            c = sum(i.nodos_poda for i in comparables)
            s = sum(i.nodos_sin_poda for i in comparables)
            texto += f"   |   En jugadas comparadas: {c:,} con poda vs {s:,} sin poda  ->  {100 * (1 - c / s):.1f} % menos"
        self.lbl_totales.config(text=texto)

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------

    def _mover_mouse(self, evento):
        col = evento.x // CELDA
        self._set_hover(col if 0 <= col < COLUMNAS else None)

    def _set_hover(self, col):
        if col != self.columna_hover:
            self.columna_hover = col
            self._dibujar()

    def _dibujar(self):
        cv = self.canvas
        cv.delete("all")
        pad = 8

        # ficha flotando sobre la columna (solo si es turno del humano)
        if (self.columna_hover is not None and not self.terminado and not self.pensando
                and not self._es_turno_maquina() and self.tablero.puede_jugar(self.columna_hover)):
            x = self.columna_hover * CELDA
            cv.create_oval(x + pad, pad, x + CELDA - pad, CELDA - pad,
                           fill=COLORES[self.turno], outline="", stipple="gray50")

        cv.create_rectangle(0, CELDA, COLUMNAS * CELDA, (FILAS + 1) * CELDA, fill=COLOR_TABLERO, outline="")
        ganadoras = set(self.linea_ganadora)
        for f in range(FILAS):
            for c in range(COLUMNAS):
                x0 = c * CELDA + pad
                y0 = (f + 1) * CELDA + pad
                valor = self.tablero.celdas[f][c]
                color = COLORES.get(valor, COLOR_HUECO)
                borde = "white" if (f, c) in ganadoras else "#16397a"
                ancho = 5 if (f, c) in ganadoras else 2
                cv.create_oval(x0, y0, x0 + CELDA - 2 * pad, y0 + CELDA - 2 * pad,
                               fill=color, outline=borde, width=ancho)
        # numeros de columna
        for c in range(COLUMNAS):
            cv.create_text(c * CELDA + CELDA / 2, (FILAS + 1) * CELDA - 6, text=str(c + 1),
                           fill="#9fb6e0", font=("Helvetica", 8))
