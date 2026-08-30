import sys
import pickle
import requests
import urllib3
from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QLabel,QHeaderView
)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal

# Desactiva advertencias de certificado si es autofirmado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DescargarDatosWorker(QThread):
    datos_obtenidos = pyqtSignal(list)
    error = pyqtSignal(str)

    def run(self):
        try:
            url = "https://192.168.10.10:4443/descargar"
            respuesta = requests.get(url, verify=False, timeout=5)

            with open("datos_tmp.pkl", "wb") as f:
                f.write(respuesta.content)

            with open("datos_tmp.pkl", "rb") as f:
                datos = pickle.load(f)

            self.datos_obtenidos.emit(datos)
        except Exception as e:
            self.error.emit(str(e))


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

        self._workers = []
        self._en_descarga = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_tabla)
        self.timer.start(500)  # cada 0,5 segundos
        self.actualizar_tabla()

    def actualizar_tabla(self):
        if self._en_descarga:
            return
        self._en_descarga = True

        worker = DescargarDatosWorker()
        worker.datos_obtenidos.connect(self._mostrar_exito)
        worker.error.connect(self._mostrar_error)
        worker.finished.connect(self._worker_terminado)
        worker.finished.connect(worker.deleteLater)
        self._workers.append(worker)
        worker.start()

    def _worker_terminado(self):
        self._en_descarga = False

    def _mostrar_error(self, mensaje):
        self.label_estado.setText(f"Error al obtener datos: {mensaje}")

    def _mostrar_exito(self, datos):
        self.label_estado.setText("Última actualización exitosa.")
        self.mostrar_tabla(datos)

    def mostrar_tabla(self, datos):
        columnas = ["IP", "MAC", "Estado", "Tiempo de conexión (s)", "Tráfico (kbps)"]
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setRowCount(len(datos))
        self.tabla.setHorizontalHeaderLabels(columnas)

        for fila, fila_dato in enumerate(datos):
            for col, valor in enumerate(fila_dato):
                self.tabla.setItem(fila, col, QTableWidgetItem(str(valor)))

