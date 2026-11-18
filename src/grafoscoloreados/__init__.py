from sys import argv, exit

import networkx
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from grafoscoloreados.classes import NO_COLOR, NODE_COLORS, InternalGraph

MAX_NODOS: int = 12

# Grafo de ejemplo (el mismo que se usa en la prueba de escritorio)
EJEMPLO_NODOS: int = 7
EJEMPLO_ARISTAS: list[tuple[int, int]] = [
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 2),
    (1, 4),
    (2, 5),
    (3, 4),
    (3, 6),
    (4, 5),
    (5, 6),
]


class NetworkXCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.draw_graph(InternalGraph(0))

    def draw_graph(self, grafo: InternalGraph) -> None:
        self.axes.clear()
        self.axes.axis("off")

        if len(grafo) == 0:
            self.axes.text(
                0.5,
                0.5,
                "Grafo vacío",
                ha="center",
                va="center",
                transform=self.axes.transAxes,
                color="gray",
            )
            self.draw()
            return

        G = networkx.Graph()
        G.add_nodes_from(range(len(grafo)))
        G.add_edges_from(grafo.edges())
        pos = networkx.spring_layout(G, seed=42, k=1.2)

        colores = [
            NODE_COLORS[c] if c != NO_COLOR else "lightgray" for c in grafo.colors()
        ]
        networkx.draw(
            G,
            pos,
            ax=self.axes,
            with_labels=True,
            node_color=colores,
            node_size=800,
            edge_color="gray",
            font_color="white",
            font_weight="bold",
            width=2,
        )

        self.axes.margins(0.15)

        usados = sorted({c for c in grafo.colors() if c != NO_COLOR})
        if usados:
            leyenda = [
                Patch(facecolor=NODE_COLORS[c], label=f"Color {c}") for c in usados
            ]
            # La leyenda va fuera del área del grafo para no tapar vértices
            self.axes.legend(
                handles=leyenda,
                loc="center left",
                bbox_to_anchor=(1.0, 0.5),
                title="Colores",
            )
            self.axes.set_title(f"Grafo coloreado con {len(usados)} color(es)")
        else:
            self.axes.set_title("Grafo (sin colorear)")
        self.figure.subplots_adjust(left=0.02, right=0.85, top=0.88, bottom=0.02)
        self.draw()


class VentanaPrincipal(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Coloreador de Grafos")
        self.resize(1280, 710)

        self.grafo: InternalGraph = InternalGraph(0)

        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        # ---------------- Panel izquierdo: matriz de adyacencia ----------------
        panel_izq = QVBoxLayout()
        panel_izq.addWidget(
            QLabel("<b>Matriz de adyacencia</b> (1 = hay arista, 0 = no hay)")
        )

        fila_n = QHBoxLayout()
        fila_n.addWidget(QLabel("Número de vértices:"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(1, MAX_NODOS)
        self.spin_n.setValue(MAX_NODOS)
        self.spin_n.valueChanged.connect(self.on_n_changed)
        fila_n.addWidget(self.spin_n)
        fila_n.addStretch()
        panel_izq.addLayout(fila_n)

        self.tabla = QTableWidget(MAX_NODOS, MAX_NODOS)
        etiquetas = [str(i) for i in range(MAX_NODOS)]
        self.tabla.setHorizontalHeaderLabels(etiquetas)
        self.tabla.setVerticalHeaderLabels(etiquetas)
        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tabla.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for i in range(MAX_NODOS):
            for j in range(MAX_NODOS):
                item = QTableWidgetItem("0")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor("black"))
                self.tabla.setItem(i, j, item)
        self.tabla.itemChanged.connect(self.on_item_changed)
        panel_izq.addWidget(self.tabla)

        # ---------------- Panel derecho: grafo, botones y log ----------------
        panel_der = QVBoxLayout()
        self.canvas = NetworkXCanvas(self, width=5, height=4)
        panel_der.addWidget(self.canvas, stretch=3)

        botones = QHBoxLayout()
        for texto, accion in (
            ("Colorear grafo", self.on_colorear),
            ("Ejemplo", self.on_ejemplo),
            ("Conectar todo", self.on_conectar_todo),
            ("Limpiar grafo", self.on_limpiar),
            ("Limpiar log", lambda: self.log.clear()),
        ):
            b = QPushButton(texto)
            b.clicked.connect(accion)
            botones.addWidget(b)
        panel_der.addLayout(botones)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("font-family: monospace;")
        panel_der.addWidget(self.log, stretch=2)

        layout.addLayout(panel_izq, stretch=2)
        layout.addLayout(panel_der, stretch=3)
        self.setCentralWidget(central_widget)

        self.actualizar_habilitadas()
        self.redibujar()

    # ------------------------------------------------------------------
    # Matriz <-> grafo
    # ------------------------------------------------------------------
    def on_item_changed(self, item: QTableWidgetItem) -> None:
        """Mantiene la matriz simétrica (grafo no dirigido) y solo 0/1."""
        i, j = item.row(), item.column()
        valor: str = "1" if item.text().strip() not in ("", "0") else "0"
        if i == j:  # Sin Bucles
            valor = "0"
        self.tabla.blockSignals(True)
        item.setText(valor)
        self.tabla.item(j, i).setText(valor)
        self.tabla.blockSignals(False)
        self.redibujar()

    def on_n_changed(self) -> None:
        self.actualizar_habilitadas()
        self.redibujar()

    def actualizar_habilitadas(self) -> None:
        n = self.spin_n.value()
        self.tabla.blockSignals(True)
        for i in range(MAX_NODOS):
            for j in range(MAX_NODOS):
                if (item := self.tabla.item(i, j)) is None:
                    raise ValueError("Failed to create Item")

                flags = item.flags()
                if i < n and j < n and i != j:
                    item.setFlags(
                        flags | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled
                    )
                    item.setBackground(QColor("white"))
                else:
                    item.setText("0")
                    item.setFlags(flags & ~Qt.ItemFlag.ItemIsEditable)
                    item.setBackground(QColor("#d0d0d0"))
        self.tabla.blockSignals(False)

    def leer_matriz(self) -> list[list[int]]:
        n = self.spin_n.value()
        return [
            [int(self.tabla.item(i, j).text() or 0) for j in range(n)] for i in range(n)
        ]

    def redibujar(self) -> None:
        """Reconstruye el grafo desde la matriz (sin colorear) y lo dibuja."""
        self.grafo = InternalGraph.from_matrix(self.leer_matriz())
        self.canvas.draw_graph(self.grafo)

    # ------------------------------------------------------------------
    # Botones
    # ------------------------------------------------------------------
    def on_colorear(self) -> None:
        self.grafo = InternalGraph.from_matrix(self.leer_matriz())
        if len(self.grafo) == 0:
            return
        self.log.append("<b>Inicio del algoritmo voraz (mayor grado primero)</b>")
        orden = sorted(range(len(self.grafo)), key=lambda v: (-self.grafo.degree(v), v))
        self.log.append(f"Orden de vértices por grado: {orden}")
        try:
            pasos = self.grafo.colorear()
        except ValueError as e:
            self.log.append(f"<span style='color:red'>Error: {e}</span>")
            return

        for p in pasos:
            self.log.append(
                f"Vértice {p['vertice']} (grado {p['grado']}): "
                f"colores de vecinos = {p['prohibidos']} → color {p['color']}"
            )
        valido = "sí" if self.grafo.es_valido() else "NO"
        self.log.append(
            f"<b>Colores usados: {self.grafo.num_colors()}</b> | "
            f"Coloración válida: {valido}\n"
        )
        self.canvas.draw_graph(self.grafo)

    def on_ejemplo(self) -> None:
        self.on_limpiar()
        self.tabla.blockSignals(True)
        for u, v in EJEMPLO_ARISTAS:
            self.tabla.item(u, v).setText("1")
            self.tabla.item(v, u).setText("1")
        self.tabla.blockSignals(False)
        self.spin_n.setValue(EJEMPLO_NODOS)
        self.redibujar()

    def on_conectar_todo(self) -> None:
        n = self.spin_n.value()
        self.tabla.blockSignals(True)
        for i in range(MAX_NODOS):
            for j in range(MAX_NODOS):
                valor = "1" if i < n and j < n and i != j else "0"
                self.tabla.item(i, j).setText(valor)
        self.tabla.blockSignals(False)
        self.redibujar()

    def on_limpiar(self) -> None:
        self.tabla.blockSignals(True)
        for i in range(MAX_NODOS):
            for j in range(MAX_NODOS):
                self.tabla.item(i, j).setText("0")
        self.tabla.blockSignals(False)
        self.redibujar()


def main() -> None:
    """Entry point"""
    app: QApplication = QApplication(argv)
    ventana_principal: VentanaPrincipal = VentanaPrincipal()
    ventana_principal.showMaximized()
    exit(app.exec())
