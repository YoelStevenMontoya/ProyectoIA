import tkinter as tk
from tkinter import ttk

from interfaz.vista_puzzle import VistaPuzzle
from interfaz.vista_conecta4 import VistaConecta4


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Proyecto 1 - Algoritmos de Busqueda | 8-Puzzle ponderado y Conecta 4")
        self.geometry("1320x760")
        self.minsize(1150, 700)

        self._estilos()

        encabezado = ttk.Frame(self, padding=(12, 8))
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="Algoritmos de Busqueda", style="Titulo.TLabel").pack(side="left")
        ttk.Label(encabezado, text="DFS · BFS · Costo uniforme · A* · Minimax con poda alfa-beta",
                  style="Sub.TLabel").pack(side="left", padx=15, pady=(6, 0))

        pestanas = ttk.Notebook(self)
        pestanas.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        pestanas.add(VistaPuzzle(pestanas), text="  8-Puzzle ponderado (DFS, BFS, UCS, A*)  ")
        pestanas.add(VistaConecta4(pestanas), text="  Conecta 4 (Minimax alfa-beta)  ")

    def _estilos(self):
        estilo = ttk.Style(self)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("Titulo.TLabel", font=("Helvetica", 18, "bold"), foreground="#1d3f7a")
        estilo.configure("Sub.TLabel", font=("Helvetica", 11), foreground="#555")
        estilo.configure("Accion.TButton", font=("Helvetica", 11, "bold"), foreground="white",
                         background="#1f4fa3", padding=6)
        estilo.map("Accion.TButton",
                   background=[("disabled", "#9aa7bd"), ("active", "#2b62c4")])
        estilo.configure("Treeview", rowheight=22)
        estilo.configure("Treeview.Heading", font=("Helvetica", 9, "bold"))


def iniciar():
    app = App()
    app.mainloop()
