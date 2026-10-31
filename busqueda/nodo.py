class Nodo:
    """
    Nodo del arbol de busqueda.

    OJO: nodo != estado. El estado es la configuracion del tablero; el nodo
    ademas guarda como llegamos ahi (padre y accion), el costo acumulado g
    y la profundidad. Dos nodos distintos pueden tener el mismo estado.
    """

    __slots__ = ("estado", "padre", "accion", "costo", "profundidad")

    def __init__(self, estado, padre=None, accion=None, costo=0):
        self.estado = estado
        self.padre = padre
        self.accion = accion
        self.costo = costo  # g(n): costo del camino desde la raiz
        self.profundidad = 0 if padre is None else padre.profundidad + 1

    def hijo(self, problema, accion):
        """Genera el nodo hijo aplicando la accion (funcion de transicion)."""
        nuevo = problema.resultado(self.estado, accion)
        costo = self.costo + problema.costo_accion(self.estado, accion, nuevo)
        return Nodo(nuevo, self, accion, costo)

    def expandir(self, problema):
        return [self.hijo(problema, a) for a in problema.acciones(self.estado)]

    def camino(self):
        """Lista de nodos desde la raiz hasta este nodo."""
        nodo, camino = self, []
        while nodo is not None:
            camino.append(nodo)
            nodo = nodo.padre
        camino.reverse()
        return camino

    def __repr__(self):
        return f"Nodo({self.estado}, g={self.costo}, prof={self.profundidad})"
