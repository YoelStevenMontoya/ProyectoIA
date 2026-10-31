"""Cosas que usan las dos vistas de la interfaz."""

import threading
import traceback


def ejecutar_en_hilo(widget, funcion, al_terminar, al_fallar=None):
    """
    Corre `funcion` en otro hilo para que la ventana no se congele mientras
    el algoritmo trabaja (UCS o minimax sin poda pueden tardar segundos).

    Tkinter NO se puede tocar desde otro hilo, entonces el hilo solo guarda
    el resultado y la ventana lo revisa cada 50 ms con after().
    """
    caja = {}

    def trabajo():
        try:
            caja["resultado"] = funcion()
        except Exception as e:  # se muestra el error en la ventana en vez de morir en silencio
            traceback.print_exc()
            caja["error"] = e

    hilo = threading.Thread(target=trabajo, daemon=True)
    hilo.start()

    def revisar():
        if hilo.is_alive():
            widget.after(50, revisar)
            return
        if "error" in caja:
            if al_fallar:
                al_fallar(caja["error"])
        else:
            al_terminar(caja["resultado"])

    widget.after(50, revisar)


def mezclar_color(c1, c2, t):
    """Interpola entre dos colores hex. t=0 -> c1, t=1 -> c2."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"
