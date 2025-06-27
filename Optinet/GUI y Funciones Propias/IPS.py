# IPS.py - Panel de Control IDS/IPS para OptiNet (versin HTTP REST)

import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox,
    QLineEdit, QLabel, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox
)
from PyQt6.QtCore import Qt

class IPSWidget(QWidget):
    def __init__(self, raspberry_ip="192.168.10.10", api_port=6001):
        super().__init__()
        self.api_base = f"http://{raspberry_ip}:{api_port}"
        self.setWindowTitle("Panel de Control IDS/IPS")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.init_ui()

    def init_ui(self):
        self.agregar_control_manual()
        self.agregar_lista_bloqueados()
        self.agregar_opciones_deteccion()
        self.agregar_reglas_personalizadas()

    def agregar_control_manual(self):
        control_manual = QGroupBox("Control Manual de Conexiones")
        control_layout = QHBoxLayout()

        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("IP o MAC")

        btn_block_ip = QPushButton("Bloquear IP")
        btn_block_ip.clicked.connect(lambda: self.enviar_comando("block_ip", self.input_valor.text()))

        btn_unblock_ip = QPushButton("Desbloquear IP")
        btn_unblock_ip.clicked.connect(lambda: self.enviar_comando("unblock_ip", self.input_valor.text()))

        btn_block_mac = QPushButton("Bloquear MAC")
        btn_block_mac.clicked.connect(lambda: self.enviar_comando("block_mac", self.input_valor.text()))

        btn_unblock_mac = QPushButton("Desbloquear MAC")
        btn_unblock_mac.clicked.connect(lambda: self.enviar_comando("unblock_mac", self.input_valor.text()))

        control_layout.addWidget(QLabel("Valor:"))
        control_layout.addWidget(self.input_valor)
        control_layout.addWidget(btn_block_ip)
        control_layout.addWidget(btn_unblock_ip)
        control_layout.addWidget(btn_block_mac)
        control_layout.addWidget(btn_unblock_mac)

        control_manual.setLayout(control_layout)
        self.layout.addWidget(control_manual)

    def agregar_lista_bloqueados(self):
        self.tabla_bloqueados = QTableWidget()
        self.tabla_bloqueados.setColumnCount(2)
        self.tabla_bloqueados.setHorizontalHeaderLabels(["Tipo", "Valor"])
        self.tabla_bloqueados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.actualizar_bloqueados()
        self.layout.addWidget(QLabel("Dispositivos Bloqueados"))
        self.layout.addWidget(self.tabla_bloqueados)

    def actualizar_bloqueados(self):
        try:
            response = requests.get(f"{self.api_base}/bloqueados", timeout=3)
            if response.status_code == 200:
                datos = response.json()
                self.tabla_bloqueados.setRowCount(len(datos))
                for i, d in enumerate(datos):
                    self.tabla_bloqueados.setItem(i, 0, QTableWidgetItem(d["tipo"]))
                    self.tabla_bloqueados.setItem(i, 1, QTableWidgetItem(d["valor"]))
            else:
                QMessageBox.warning(self, "Error", f"No se pudo cargar la lista de bloqueados: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al consultar bloqueados: {e}")

    def agregar_opciones_deteccion(self):
        deteccion_group = QGroupBox("Detección Automática")
        deteccion_layout = QHBoxLayout()

        self.chk_syn = QCheckBox("Detectar SYN Flood")
        self.chk_ports = QCheckBox("Detectar Port Scanning")
        self.chk_dns = QCheckBox("Detectar DNS Spoofing")

        for chk, accion in [
            (self.chk_syn, "toggle_syn"),
            (self.chk_ports, "toggle_portscan"),
            (self.chk_dns, "toggle_dnsspoof")
        ]:
            chk.stateChanged.connect(lambda state, a=accion: self.enviar_comando(a, "on" if state else "off"))
            deteccion_layout.addWidget(chk)

        deteccion_group.setLayout(deteccion_layout)
        self.layout.addWidget(deteccion_group)

    def agregar_reglas_personalizadas(self):
        reglas_group = QGroupBox("Reglas Personalizadas")
        reglas_layout = QHBoxLayout()

        self.input_regla = QLineEdit()
        self.input_regla.setPlaceholderText("Ej: bloquear si puerto 22")
        btn_agregar = QPushButton("Agregar Regla")
        btn_agregar.clicked.connect(lambda: self.enviar_comando("regla_personalizada", self.input_regla.text()))

        reglas_layout.addWidget(self.input_regla)
        reglas_layout.addWidget(btn_agregar)

        reglas_group.setLayout(reglas_layout)
        self.layout.addWidget(reglas_group)

    def enviar_comando(self, accion, valor=None):
        data = {"accion": accion}
        if valor:
            data["valor"] = valor
        try:
            response = requests.post(f"{self.api_base}/comando", json=data, timeout=3)
            if response.status_code == 200:
                self.actualizar_bloqueados()
            else:
                QMessageBox.warning(self, "Error", f"Error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar con la Raspberry:\n{e}")
