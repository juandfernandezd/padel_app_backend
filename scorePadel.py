import sys
import asyncio
import requests
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, QMainWindow, QGridLayout
from PyQt5.QtCore import QTimer, QDateTime, QTime, Qt
from websockets import connect

class TemplateWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.fecha_hora_apertura = QDateTime.currentDateTime()
        self.label_time = QLabel()
        self.setWindowTitle("SCOREPADEL")
        self.initUI()
        self.websocket = None
        

    def initUI(self):
        # Crear un layout vertical principal
        layout_principal = QVBoxLayout(self)

        # para centrar el reloj horizontalmente
        layout_central = QHBoxLayout()

        # para mostrar la hora actual
        self.label_reloj = QLabel()
        self.actualizar_reloj()

        # para mostrar el tiempo transcurrido desde la apertura de la ventana
        self.label_tiempo_transcurrido = QLabel()
        self.actualizar_tiempo_transcurrido()

        layout_principal.addLayout(layout_central)


        # Agregar el QLabel del reloj al layout central
        layout_central.addWidget(self.label_reloj)
        layout_central.setAlignment(Qt.AlignCenter)  # Centrar horizontalmente

        layout_principal.addLayout(layout_central)

        # fila superior con el tiempo del partido
        layout_superior = QHBoxLayout()
        self.label_match_time = QLabel("Match time")
        self.label_match_time.setStyleSheet("font-weight: bold; font-size: 18px;")
        self.label_time = QLabel()  
        layout_superior.addWidget(self.label_match_time)
        layout_superior.addStretch(1)
        layout_superior.addWidget(self.label_time)
        layout_principal.addLayout(layout_superior)

        # línea separadora horizontal
        linea_horizontal = QFrame()
        linea_horizontal.setFrameShape(QFrame.HLine)  # Tipo de línea horizontal
        linea_horizontal.setFrameShadow(QFrame.Sunken)  # Sombra de la línea
        layout_principal.addWidget(linea_horizontal)

        # encabezado de la tabla
        layout_encabezado = QHBoxLayout()
        labels_encabezado = ["Games", "Set 1", "Set 2", "Set 3"]
        for label in labels_encabezado:
            layout_encabezado.addWidget(QLabel(label))
        layout_principal.addLayout(layout_encabezado)

        # línea separadora horizontal
        linea_horizontal = QFrame()
        linea_horizontal.setFrameShape(QFrame.HLine)  # Tipo de línea horizontal
        linea_horizontal.setFrameShadow(QFrame.Sunken)  # Sombra de la línea
        layout_principal.addWidget(linea_horizontal)

        # filas de la tabla
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

            linea_horizontal = QFrame()
            linea_horizontal.setFrameShape(QFrame.HLine)  
            linea_horizontal.setFrameShadow(QFrame.Sunken) 
            layout_principal.addWidget(linea_horizontal)

        self.setWindowTitle('ScorePadel')
        self.setGeometry(300, 300, 400, 200)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_reloj)
        self.timer.start(1000)

        self.timer_transcurrido = QTimer(self)
        self.timer_transcurrido.timeout.connect(self.actualizar_tiempo_transcurrido)
        self.timer_transcurrido.start(1000)

        self.show()

        # Iniciar la conexión WebSocket
        asyncio.ensure_future(self.connect_to_websocket())

    def actualizar_reloj(self):
        tiempo_actual = QTime.currentTime()
        texto_reloj = tiempo_actual.toString('hh:mm')
        self.label_reloj.setText("Reloj: " + texto_reloj)

    def actualizar_tiempo_transcurrido(self):
        tiempo_actual = QDateTime.currentDateTime()
        tiempo_transcurrido = self.fecha_hora_apertura.secsTo(tiempo_actual)
        horas = tiempo_transcurrido // 3600
        minutos = (tiempo_transcurrido % 3600) // 60
        segundos = tiempo_transcurrido % 60
        texto_tiempo_transcurrido = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        self.label_tiempo_transcurrido.setText(texto_tiempo_transcurrido)
        self.label_time.setText(texto_tiempo_transcurrido)
        
    async def connect_to_websocket(self):
        # URL del servidor WebSocket
        uri = "ws://localhost:8000/ws"
        try:
            async with connect(uri) as websocket:
                self.websocket = websocket
                async for message in websocket:
                    # Actualizar la interfaz con el mensaje recibido
                    self.label_time.setText(message)
        except Exception as e:
            print(f"Error de conexión WebSocket: {e}")

class WaitingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCOREPADEL")
        self.initUI()

    def initUI(self):
        layout_principal = QVBoxLayout(self)
        mensaje = QLabel("Esperando partido...")
        mensaje.setStyleSheet("font-size: 40px; font-weight: bold; color: #666;")
        layout_principal.addWidget(mensaje)
        self.setGeometry(300, 300, 400, 200)

def check_match_status():
    url = "http://localhost:8000/registro_partido"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            app = QApplication(sys.argv)
            ventana = TemplateWidget()
            ventana.showMaximized()
            sys.exit(app.exec_())
        else:
            app = QApplication(sys.argv)
            ventana = WaitingWidget()
            ventana.showMaximized()
            sys.exit(app.exec_())
    except Exception as e:
        print(f"Error al verificar el estado del partido: {e}")

if __name__ == '__main__':
    #app = QApplication(sys.argv)
    #window = MatchTemplate()
    #ventana = TablaConSeparadores()
    #ventana = TemplateWidget()
    #ventana.showMaximized()
    #sys.exit(app.exec_())
    check_match_status()