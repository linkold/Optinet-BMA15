import sys
import pickle
import requests
import urllib3
from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QLabel,QHeaderView
)
from PyQt6.QtCore import QTimer

# Desactiva advertencias de certificado si es autofirmado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TablaMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor de Dispositivos en Red")
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.label_estado = QLabel("Estado: actualizando datos...")
        self.tabla = QTableWidget()
        layout.addWidget(self.label_estado)
        layout.addWidget(self.tabla)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_tabla)
        self.timer.start(500)  # cada 1 segundos
        self.actualizar_tabla()

    def actualizar_tabla(self):
        try:
            url = "https://192.168.10.10:4443/descargar"
            respuesta = requests.get(url, verify=False, timeout=5)

            with open("datos_tmp.pkl", "wb") as f:
                f.write(respuesta.content)

            with open("datos_tmp.pkl", "rb") as f:
                datos = pickle.load(f)

            self.label_estado.setText("Última actualización exitosa.")
            self.mostrar_tabla(datos)
        except Exception as e:
            self.label_estado.setText(f"Error al obtener datos: {e}")

    def mostrar_tabla(self, datos):
        columnas = ["IP", "MAC", "Estado", "Tiempo de conexión (s)", "Tráfico (kbps)"]
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setRowCount(len(datos))
        self.tabla.setHorizontalHeaderLabels(columnas)

        for fila, fila_dato in enumerate(datos):
            for col, valor in enumerate(fila_dato):
                self.tabla.setItem(fila, col, QTableWidgetItem(str(valor)))

