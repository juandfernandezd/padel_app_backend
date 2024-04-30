import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QTableWidgetItem, QTableWidget, QVBoxLayout
from PyQt5.QtCore import Qt

class ScoreboardApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Scoreboard")
        self.setGeometry(100, 100, 600, 200)  # Tamaño inicial de la ventana

        # Crear una cuadrícula para organizar los widgets
        layout = QGridLayout()
        self.setLayout(layout)

        # Encabezados de la tabla
        headers = ["", "Games", "Set 1", "Set 2", "Set 3"]

        # Agregar encabezados a la cuadrícula
        for col, header in enumerate(headers):
            label = QLabel(header)
            layout.addWidget(label, 0, col + 1)  # Fila 0 para encabezados, columnas desplazadas para ajustar los nombres

        # Datos de ejemplo de jugadores y puntajes
        player_scores = {
            "Jugador1": [30, 4, 0, 0],
            "Jugador2": [15, 2, 0, 0]
        }

        # Mostrar los datos en una tabla
        row = 1  # Comenzar desde la fila 1 para datos de jugadores
        for player, scores in player_scores.items():
            layout.addWidget(QLabel(player), row, 0)  # Nombre del jugador en la primera columna
            for col, score in enumerate(scores):
                item = QTableWidgetItem(str(score))
                item.setFlags(item.flags() ^  Qt.ItemIsEditable)  # Hacer que las celdas no sean editables
                layout.addWidget(QLabel(str(score)), row, col + 1)
            row += 1

        self.show()

def main():
    app = QApplication(sys.argv)
    scoreboard = ScoreboardApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
