# reportes.py - Página de Reportes IDS/IPS (alertas históricas)

import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

class ReportesWidget(QWidget):
    def __init__(self, raspberry_ip="192.168.10.10", api_port=6001):
        super().__init__()
        self.api_base = f"http://{raspberry_ip}:{api_port}"
        self.setWindowTitle("Reportes IDS/IPS")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.inicializar_ui()

    def inicializar_ui(self):
        titulo = QLabel("Historial de Alertas IDS/IPS")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(titulo)

        self.tabla_alertas = QTableWidget()
        self.tabla_alertas.setColumnCount(4)
        self.tabla_alertas.setHorizontalHeaderLabels(["Hora", "Tipo de Alerta", "IP", "Detalles"])
        self.tabla_alertas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.tabla_alertas)

        btn_actualizar = QPushButton("Actualizar Reportes")
        btn_actualizar.clicked.connect(self.cargar_alertas)
        self.layout.addWidget(btn_actualizar)

        self.cargar_alertas()

    def cargar_alertas(self):
        try:
            response = requests.get(f"{self.api_base}/alertas", timeout=4)
            if response.status_code == 200:
                datos = response.json()
                self.tabla_alertas.setRowCount(len(datos))
                for i, alerta in enumerate(datos):
                    self.tabla_alertas.setItem(i, 0, QTableWidgetItem(alerta.get("hora", "-")))
                    self.tabla_alertas.setItem(i, 1, QTableWidgetItem(alerta.get("tipo", "-")))
                    self.tabla_alertas.setItem(i, 2, QTableWidgetItem(alerta.get("ip", "-")))
                    self.tabla_alertas.setItem(i, 3, QTableWidgetItem(alerta.get("detalle", "-")))
            else:
                QMessageBox.warning(self, "Error", f"Error {response.status_code}: No se pudo cargar el historial")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al conectar con el servidor de reportes: {e}")
