from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QGroupBox, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from Sistema_Operativo_Condicional import datos_variantes


class WifiScannerThread(QThread):
    resultados = pyqtSignal(list)

    def run(self):
        try:
            redes = datos_variantes.wifi_datos()
            self.resultados.emit(redes)
        except Exception as e:
            self.resultados.emit([])


class WifiWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.iniciar_actualizacion_automatica()

    def init_ui(self):
        self.layout_principal = QVBoxLayout(self)

        self.tabla1 = QTableWidget()
        self.tabla1.setColumnCount(7)
        self.tabla1.setHorizontalHeaderLabels([
            "SSID", "Intensidad de señal", "Canal", "Banda",
            "Tipo de Seguridad", "Dirección MAC", "tipo Wi-Fi"
        ])
        self.tabla1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.label_grafico = QLabel("Redes Disponibles en el entorno")
        self.label_grafico.setFont(QFont("Arial", 20))

        self.figura, self.x1 = plt.subplots()
        self.canvas = FigureCanvas(self.figura)

        self.label1_1 = QLabel()
        self.label1_2 = QLabel()
        self.label1_3 = QLabel()
        self.label1_4 = QLabel()

        grupo_info = QGroupBox("Información")
        lay_info = QVBoxLayout()
        for label in [self.label1_1, self.label1_2, self.label1_3, self.label1_4]:
            lay_info.addWidget(label)
        grupo_info.setLayout(lay_info)

        layout_superior = QVBoxLayout()
        layout_superior.addWidget(self.label_grafico)
        layout_superior.addWidget(self.tabla1)
        layout_superior.setAlignment(self.label_grafico, Qt.AlignmentFlag.AlignCenter)

        layout_inferior = QHBoxLayout()
        layout_inferior.addWidget(self.canvas)
        layout_inferior.addWidget(grupo_info)

        self.boton_actualizar = QPushButton("Actualizar")
        self.boton_actualizar.clicked.connect(self.actualizar_tabla_wifi)

        self.layout_principal.addLayout(layout_superior, 3)
        self.layout_principal.addLayout(layout_inferior, 2)
        self.layout_principal.addWidget(self.boton_actualizar)

    def iniciar_actualizacion_automatica(self, intervalo_ms=10000):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_tabla_wifi)
        self.timer.start(intervalo_ms)

    def actualizar_tabla_wifi(self):
        self.boton_actualizar.setEnabled(False)
        self.thread = WifiScannerThread()
        self.thread.resultados.connect(self.mostrar_resultados)
        self.thread.start()

    def mostrar_resultados(self, red1):
        self.tabla1.setRowCount(len(red1))

        cantidad_2_4g = 0
        cantidad_5g = 0
        wifi_5_6 = 0

        for i, red in enumerate(red1):
            ssid = red.get("SSID", "Desconocido")
            intensidad = str(red.get("Intensidad", "N/A"))
            canal = red.get("Canal", "-")
            banda = f"{red.get('Banda', '?')}GHz"
            seguridad = red.get("Seguridad", "¿?")
            mac = red.get("MAC", "¿?")
            tipo_wifi = red.get("Wi-fi", "¿?")

            self.tabla1.setItem(i, 0, QTableWidgetItem(ssid))
            self.tabla1.setItem(i, 1, QTableWidgetItem(intensidad))
            self.tabla1.setItem(i, 2, QTableWidgetItem(canal))
            self.tabla1.setItem(i, 3, QTableWidgetItem(banda))
            self.tabla1.setItem(i, 4, QTableWidgetItem(seguridad))
            self.tabla1.setItem(i, 5, QTableWidgetItem(mac))
            self.tabla1.setItem(i, 6, QTableWidgetItem(tipo_wifi))

            if canal == "2.4GHz":
                cantidad_2_4g += 1
            elif canal == "5GHz":
                cantidad_5g += 1
            if tipo_wifi in ["Wi-Fi 5", "Wi-Fi 6"]:
                wifi_5_6 += 1

        self.label1_1.setText(f"Redes Detectadas: {len(red1)}")
        self.label1_2.setText(f"Redes en 2.4GHz: {cantidad_2_4g}")
        self.label1_3.setText(f"Redes en 5GHz: {cantidad_5g}")
        self.label1_4.setText(f"Redes con Wi-Fi 5/6: {wifi_5_6}")

        # Actualizar gráfico
        self.figura.clear()
        self.x1 = self.figura.add_subplot(111)
        self.figura.patch.set_facecolor('black')
        self.x1.set_facecolor('black')

        ssids = [r.get("SSID", "Desconocido") for r in red1]
        intensidades = [int(r.get("Intensidad", "0%").replace("%", "")) for r in red1]

        self.x1.barh(ssids, intensidades, color='white')
        self.x1.set_xlabel("Intensidad (%)", color='white')
        self.x1.set_title("Redes Wi-Fi disponibles", color='white')
        self.x1.tick_params(axis='x', colors='white')
        self.x1.tick_params(axis='y', colors='white')

        for i, v in enumerate(intensidades):
            self.x1.text(v + 1, i, f"{v}%", va='center', color='white')

        self.canvas.draw()
        self.boton_actualizar.setEnabled(True)
