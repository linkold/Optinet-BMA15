# seguridad.py - Página de Seguridad para OptiNet (vía HTTP Flask)
# seguridad.py - Página de Seguridad para OptiNet (vía servidor HTTP en Raspberry)

import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QHBoxLayout, QGroupBox, QHeaderView, QMessageBox
)


class SeguridadWidget(QWidget):
    def __init__(self, raspberry_ip="192.168.10.10", api_port=6001):
        super().__init__()
        self.api_base = f"http://{raspberry_ip}:{api_port}"
        self.setWindowTitle("Seguridad IDS/IPS")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_botones_control()
        self.init_tablas()

    def init_botones_control(self):
        grupo = QGroupBox("Controles de Captura")
        layout = QHBoxLayout()

        btn_iniciar = QPushButton("Iniciar Captura")
        btn_iniciar.clicked.connect(lambda: self.enviar_comando("iniciar_captura"))

        btn_detener = QPushButton("Detener Captura")
        btn_detener.clicked.connect(lambda: self.enviar_comando("detener_captura"))

        layout.addWidget(btn_iniciar)
        layout.addWidget(btn_detener)

        grupo.setLayout(layout)
        self.layout.addWidget(grupo)

    def init_tablas(self):
        # Tabla: Dispositivos Detectados
        self.tabla_dispositivos = QTableWidget()
        self.tabla_dispositivos.setColumnCount(2)
        self.tabla_dispositivos.setHorizontalHeaderLabels(["IP", "MAC"])
        self.tabla_dispositivos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(QLabel("Dispositivos Detectados"))
        self.layout.addWidget(self.tabla_dispositivos)

        # Tabla: Dispositivos Sospechosos
        self.tabla_sospechosos = QTableWidget()
        self.tabla_sospechosos.setColumnCount(2)
        self.tabla_sospechosos.setHorizontalHeaderLabels(["IP", "MAC"])
        self.tabla_sospechosos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(QLabel("Dispositivos Sospechosos (No Autorizados)"))
        self.layout.addWidget(self.tabla_sospechosos)

        # Tabla: Alertas IDS
        self.tabla_alertas = QTableWidget()
        self.tabla_alertas.setColumnCount(3)
        self.tabla_alertas.setHorizontalHeaderLabels(["Hora", "Tipo", "Detalle"])
        self.tabla_alertas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(QLabel("Alertas IDS Recientes"))
        self.layout.addWidget(self.tabla_alertas)

        # Cargar datos al iniciar
        self.cargar_datos()

    def cargar_datos(self):
        self.cargar_tabla("dispositivos", self.tabla_dispositivos, ["ip", "mac"])
        self.cargar_tabla("sospechosos", self.tabla_sospechosos, ["ip", "mac"])
        self.cargar_tabla("alertas", self.tabla_alertas, ["hora", "tipo", "detalle"])

    def cargar_tabla(self, endpoint, tabla, campos):
        try:
            response = requests.get(f"{self.api_base}/{endpoint}", timeout=5)
            if response.status_code == 200:
                datos = response.json()
                tabla.setRowCount(len(datos))
                for i, item in enumerate(datos):
                    for j, campo in enumerate(campos):
                        tabla.setItem(i, j, QTableWidgetItem(str(item.get(campo, ""))))
            else:
                QMessageBox.warning(self, "Error", f"Fallo al obtener /{endpoint}: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al obtener /{endpoint}: {e}")

    def enviar_comando(self, accion):
        try:
            response = requests.post(f"{self.api_base}/comando", json={"accion": accion}, timeout=3)
            if response.status_code == 200:
                QMessageBox.information(self, "Éxito", f"{accion} ejecutado correctamente")
                self.cargar_datos()  # Refrescar
            else:
                QMessageBox.warning(self, "Error", f"Fallo al ejecutar {accion}: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error de conexión: {e}")
