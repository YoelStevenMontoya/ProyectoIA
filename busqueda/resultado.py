from dataclasses import dataclass, field


@dataclass
class ResultadoBusqueda:
    """Todo lo que reporta un algoritmo al terminar (para mostrar y comparar)."""

    algoritmo: str
    exito: bool = False
    estados: list = field(default_factory=list)   # estados del camino solucion
    acciones: list = field(default_factory=list)  # acciones del camino solucion
    costo: int = 0                 # costo total del camino
    profundidad: int = 0           # numero de pasos de la solucion
    nodos_expandidos: int = 0
    nodos_generados: int = 0
    max_frontera: int = 0          # tamaño maximo que alcanzo la frontera
    max_en_memoria: int = 0        # max(frontera + explorados): medida de memoria en nodos
    tiempo: float = 0.0            # segundos
    memoria_kb: float = None       # pico de memoria (tracemalloc), solo si se pide
    mensaje: str = ""

    def resumen(self):
        """Texto corto con las metricas, se usa en consola y en la interfaz."""
        lineas = [f"Algoritmo: {self.algoritmo}"]
        if not self.exito:
            lineas.append("  NO se encontro solucion")
            if self.mensaje:
                lineas.append(f"  ({self.mensaje})")
        else:
            lineas.append("  Solucion encontrada")
            lineas.append(f"  Pasos (profundidad): {self.profundidad}")
            lineas.append(f"  Costo total:         {self.costo}")
        lineas.append(f"  Nodos expandidos:    {self.nodos_expandidos}")
        lineas.append(f"  Nodos generados:     {self.nodos_generados}")
        lineas.append(f"  Max. frontera:       {self.max_frontera}")
        lineas.append(f"  Max. nodos en memoria: {self.max_en_memoria}")
        lineas.append(f"  Tiempo:              {self.tiempo * 1000:.2f} ms")
        if self.memoria_kb is not None:
            lineas.append(f"  Memoria pico:        {self.memoria_kb:.1f} KB")
        return "\n".join(lineas)


def armar_resultado(nombre, nodo_meta, expandidos, generados, max_frontera, max_memoria):
    """Construye el resultado a partir del nodo meta (o None si fallo)."""
    res = ResultadoBusqueda(algoritmo=nombre,
                            nodos_expandidos=expandidos,
                            nodos_generados=generados,
                            max_frontera=max_frontera,
                            max_en_memoria=max_memoria)
    if nodo_meta is not None:
        camino = nodo_meta.camino()
        res.exito = True
        res.estados = [n.estado for n in camino]
        res.acciones = [n.accion for n in camino[1:]]
        res.costo = nodo_meta.costo
        res.profundidad = nodo_meta.profundidad
    return res
