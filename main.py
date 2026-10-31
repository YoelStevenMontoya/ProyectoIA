"""
Proyecto 1 - Algoritmos de Busqueda

Ejecutar:
    python main.py            -> interfaz grafica (Tkinter)
    python main.py --consola  -> version de consola

Si Tkinter no esta instalado se abre automaticamente la version de consola.
"""

import sys


def main():
    if "--consola" in sys.argv or "-c" in sys.argv:
        import consola
        consola.main()
        return

    try:
        import tkinter  # noqa: F401  (solo para ver si esta disponible)
    except ImportError:
        print("No se encontro Tkinter, se abre la version de consola.")
        print("(En Linux se instala con: sudo apt install python3-tk)\n")
        import consola
        consola.main()
        return

    from interfaz.app import iniciar
    try:
        iniciar()
    except tkinter.TclError as e:
        # pasa por ejemplo en un servidor sin pantalla
        print(f"No se pudo abrir la ventana ({e}). Se abre la version de consola.\n")
        import consola
        consola.main()


if __name__ == "__main__":
    main()
