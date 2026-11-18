# https://medium.com/data-science/graph-coloring-with-networkx-88c45f09b8f4
# https://networkx.org/documentation/stable/reference/drawing.html
from grafoscoloreados.constans import NO_COLOR, NODE_COLORS


class Node:
    __slots__ = ("color_index", "label")

    def __init__(self, label: str | int, color_index: int = NO_COLOR) -> None:
        self.label: str | int = label
        self.color_index: int = color_index


class InternalGraph:
    __slots__ = ("_adj", "_nodes")
    def __init__(self, n: int = 0) -> None:
        self._nodes: list[Node] = [Node(i) for i in range(n)]
        self._adj: list[list[bool]] = [[False] * n for _ in range(n)]

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------
    @classmethod
    def from_matrix(
        cls, matrix: list[list[int | float]], n: int | None = None
    ) -> InternalGraph:
        """Crea el grafo (no dirigido) a partir de una matriz de adyacencia.
        Cualquier valor distinto de 0 fuera de la diagonal cuenta como arista."""
        n = len(matrix) if n is None else n
        g = cls(n)
        for i in range(n):
            for j in range(n):
                if i != j and (matrix[i][j] != 0 or matrix[j][i] != 0):
                    g._adj[i][j] = g._adj[j][i] = True
        return g

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self._nodes)

    @property
    def nodes(self) -> list[Node]:
        return self._nodes

    def neighbors(self, v: int) -> list[int]:
        return [u for u in range(len(self._nodes)) if self._adj[v][u]]

    def degree(self, v: int) -> int:
        return len(self.neighbors(v))

    def edges(self) -> list[tuple[int, int]]:
        n = len(self._nodes)
        return [(i, j) for i in range(n) for j in range(i + 1, n) if self._adj[i][j]]

    def colors(self) -> list[int]:
        return [node.color_index for node in self._nodes]

    def num_colors(self) -> int:
        usados = {c for c in self.colors() if c != NO_COLOR}
        return len(usados)

    def reset_colors(self) -> None:
        for node in self._nodes:
            node.color_index = NO_COLOR

    def es_valido(self) -> bool:
        """True si ningún par de vértices adyacentes comparte color."""
        return all(
            self._nodes[i].color_index != self._nodes[j].color_index
            for i, j in self.edges()
        )

    # ------------------------------------------------------------------
    # Algoritmo voraz (Welsh-Powell: mayor grado primero)
    # ------------------------------------------------------------------
    def colorear(self) -> list[dict]:
        """Colorea el grafo con un algoritmo voraz.

        1. Ordena los vértices por grado de mayor a menor (empate: menor número).
        2. Recorre ese orden y a cada vértice le asigna el menor color
           (0..11) que no usen sus vecinos ya coloreados.

        Devuelve la lista de pasos (sirve para el log y la prueba de escritorio).
        """
        self.reset_colors()
        n = len(self._nodes)
        orden = sorted(range(n), key=lambda v: (-self.degree(v), v))
        pasos: list[dict] = []

        for v in orden:
            prohibidos = sorted(
                {
                    self._nodes[u].color_index
                    for u in self.neighbors(v)
                    if self._nodes[u].color_index != NO_COLOR
                }
            )
            color = 0
            while color in prohibidos:
                color += 1
            if color >= len(NODE_COLORS):
                self.reset_colors()
                raise ValueError(
                    f"El grafo necesita más de {len(NODE_COLORS)} colores "
                    f"(solo hay colores del 0 al {len(NODE_COLORS) - 1})."
                )
            self._nodes[v].color_index = color
            pasos.append(
                {
                    "vertice": v,
                    "grado": self.degree(v),
                    "prohibidos": prohibidos,
                    "color": color,
                }
            )
        return pasos
