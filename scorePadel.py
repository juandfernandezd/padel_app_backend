import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, QMainWindow
from PyQt5.QtCore import QTimer, QTime, Qt
class MatchTemplate(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SCOREPADEL")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        grid_layout = QGridLayout()
        central_widget.setLayout(grid_layout)

        # Añadir elementos a la rejilla
        grid_layout.addWidget(QLabel("match time"), 0, 0)
        grid_layout.addWidget(QLabel("| 08:35|"), 0, 1)
        grid_layout.addWidget(QLabel("games"), 0, 2)
        grid_layout.addWidget(QLabel("set 1"), 0, 3)
        grid_layout.addWidget(QLabel("set 2"), 0, 4)
        grid_layout.addWidget(QLabel("set 3"), 0, 5)

        # Crear la línea separadora horizontal
        linea_horizontal = QFrame()
        linea_horizontal.setFrameShape(QFrame.HLine)  # Tipo de línea horizontal
        linea_horizontal.setFrameShadow(QFrame.Sunken)  # Sombra de la línea
        grid_layout.addWidget(linea_horizontal)

        # Crear la línea separadora vertical
        linea_vertical = QFrame()
        linea_vertical.setFrameShape(QFrame.VLine)  # Tipo de línea vertical
        linea_vertical.setFrameShadow(QFrame.Sunken)  # Sombra de la línea
        grid_layout.addWidget(linea_vertical)
        # Añadir los jugadores
        players = ["nombre 1", "nombre 2", "nombre 3", "nombre 4"]
        scores = ["15", "", "40", "15"]

        for i, (player, score) in enumerate(zip(players, scores), start=1):
            grid_layout.addWidget(QLabel(f"o {player}"), i, 0)
            grid_layout.addWidget(QLabel(f"| {score}"), i, 2)
            for j in range(3):
                grid_layout.addWidget(QLabel("|"), i, j + 3)

        self.show()

class TablaConSeparadores(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Crear un layout vertical principal
        layout_principal = QVBoxLayout(self)

        # Crear una línea separadora horizontal
        linea_horizontal = QFrame()
        linea_horizontal.setFrameShape(QFrame.HLine)  # Tipo de línea horizontal
        linea_horizontal.setFrameShadow(QFrame.Sunken)  # Sombra de la línea

        # Agregar la línea separadora horizontal al layout principal
        layout_principal.addWidget(linea_horizontal)

        # Crear un layout horizontal para contener la línea horizontal y vertical
        layout_horizontal = QHBoxLayout()

        # Crear una línea separadora vertical
        linea_vertical = QFrame()
        linea_vertical.setFrameShape(QFrame.VLine)  # Tipo de línea vertical
        linea_vertical.setFrameShadow(QFrame.Sunken)  # Sombra de la línea

        # Agregar la línea separadora vertical al layout horizontal
        layout_horizontal.addWidget(linea_vertical)

        # Agregar el layout horizontal al layout principal
        layout_principal.addLayout(layout_horizontal)

        self.setWindowTitle('Tabla con Separadores')
        self.setGeometry(300, 300, 400, 200)
        self.show()

class TemplateWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Crear un layout vertical principal
        layout_principal = QVBoxLayout(self)

        # Crear un QHBoxLayout para centrar el reloj horizontalmente
        layout_central = QHBoxLayout()

        # Crear un QLabel para mostrar la hora actual
        self.label_reloj = QLabel()
        self.actualizar_reloj()

        # Agregar el QLabel del reloj al layout central
        layout_central.addWidget(self.label_reloj)
        layout_central.setAlignment(Qt.AlignCenter)  # Centrar horizontalmente

        # Agregar el layout central al layout principal
        layout_principal.addLayout(layout_central)

        # Crear la fila superior con el tiempo del partido
        layout_superior = QHBoxLayout()
        label_match_time = QLabel("Match time")
        label_time = QLabel("12:35")
        layout_superior.addWidget(label_match_time)
        layout_superior.addStretch(1)
        layout_superior.addWidget(label_time)
        layout_principal.addLayout(layout_superior)

        # Crear la línea separadora horizontal
        linea_horizontal = QFrame()
        linea_horizontal.setFrameShape(QFrame.HLine)  # Tipo de línea horizontal
        linea_horizontal.setFrameShadow(QFrame.Sunken)  # Sombra de la línea
        layout_principal.addWidget(linea_horizontal)

        # Crear el encabezado de la tabla
        layout_encabezado = QHBoxLayout()
        labels_encabezado = ["Games", "Set 1", "Set 2", "Set 3"]
        for label in labels_encabezado:
            layout_encabezado.addWidget(QLabel(label))
        layout_principal.addLayout(layout_encabezado)

        # Crear la línea separadora horizontal
        linea_horizontal = QFrame()
        linea_horizontal.setFrameShape(QFrame.HLine)  # Tipo de línea horizontal
        linea_horizontal.setFrameShadow(QFrame.Sunken)  # Sombra de la línea
        layout_principal.addWidget(linea_horizontal)

        # Crear las filas de la tabla
        datos_tabla = [
            ["Luis Felipe Hernandez", "15", "6", "1", "0"],
            ["Juan David Fernandez", "", "", "", ""],
            ["Sebastian Giraldo", "30", "3", "2", "0"],
            ["Mateo Beltran", "", "", "", ""]
        ]
        for fila_datos in datos_tabla:
            layout_fila = QHBoxLayout()
            for dato in fila_datos:
                layout_fila.addWidget(QLabel(dato))
            layout_principal.addLayout(layout_fila)

            # Agregar una línea separadora horizontal después de cada fila
            linea_horizontal = QFrame()
            linea_horizontal.setFrameShape(QFrame.HLine)  # Tipo de línea horizontal
            linea_horizontal.setFrameShadow(QFrame.Sunken)  # Sombra de la línea
            layout_principal.addWidget(linea_horizontal)

        self.setWindowTitle('Template de Tabla')
        self.setGeometry(300, 300, 400, 200)

        # Configurar el temporizador para actualizar el reloj cada segundo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_reloj)
        self.timer.start(1000)

        self.show()

    def actualizar_reloj(self):
        tiempo_actual = QTime.currentTime()
        texto_reloj = tiempo_actual.toString('hh:mm')
        self.label_reloj.setText("Reloj: " + texto_reloj)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #window = MatchTemplate()
    #ventana = TablaConSeparadores()
    ventana = TemplateWidget()
    sys.exit(app.exec_())
