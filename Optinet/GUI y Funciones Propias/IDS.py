from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QLineEdit, QMessageBox
)
import threading
import os
import platform
import subprocess
import re

# Clase RedMonitorLigero (igual que la tuya)
class RedMonitorLigero:
    def __init__(self, whitelist=None):
        self.whitelist = whitelist if whitelist else set()
        self.dispositivos_detectados = []
        self.dispositivos_sospechosos = []
        self.alertas_ids = []

    def escanear_red(self, ip_base="192.168.0.", rango=10):
        print("[*] Escaneando la red con ping...")
        self.dispositivos_detectados.clear()
        sistema = platform.system()

        for i in range(1, rango + 1):
            ip = f"{ip_base}{i}"
            if sistema == "Windows":
                os.system(f"ping -n 1 -w 200 {ip} > nul")
            else:
                os.system(f"ping -c 1 -W 1 {ip} > /dev/null")

        self._leer_tabla_arp()

    def _leer_tabla_arp(self):
        print("[*] Leyendo tabla ARP...")
        self.dispositivos_detectados.clear()
        salida = subprocess.check_output("arp -a", shell=True).decode()
        lineas = salida.splitlines()

        for linea in lineas:
            if "-" in linea or ":" in linea:
                partes = re.split(r"\s+", linea.strip())
                if len(partes) >= 2:
                    ip = partes[0]
                    mac = partes[1].lower()
                    self.dispositivos_detectados.append({'ip': ip, 'mac': mac})

    def detectar_fantasmas(self):
        print("[*] Detectando dispositivos no autorizados...")
        self.dispositivos_sospechosos = [
            d for d in self.dispositivos_detectados if d['mac'] not in self.whitelist
        ]
        self.alertas_ids.clear()
        for d in self.dispositivos_sospechosos:
            alerta = f"[ALERTA] Dispositivo fantasma: {d['ip']} | {d['mac']}"
            self.alertas_ids.append(alerta)
            print(alerta)

    def obtener_dispositivos(self):
        return self.dispositivos_detectados

    def obtener_sospechosos(self):
        return self.dispositivos_sospechosos

    def obtener_alertas_ids(self):
        return self.alertas_ids

# Widget para integrar en la pestaña 'dispositivos'
class RedMonitorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.monitor = RedMonitorLigero()

        layout = QVBoxLayout()

        btn_layout = QHBoxLayout()
        self.btn_escanear = QPushButton("Escanear Red")
        self.btn_detectar = QPushButton("Detectar Fantasmas")
        btn_layout.addWidget(self.btn_escanear)
        btn_layout.addWidget(self.btn_detectar)
        layout.addLayout(btn_layout)

        layout.addWidget(QLabel("Dispositivos Detectados:"))
        self.lista_dispositivos = QListWidget()
        layout.addWidget(self.lista_dispositivos)

        layout.addWidget(QLabel("Dispositivos Sospechosos (no autorizados):"))
        self.lista_sospechosos = QListWidget()
        layout.addWidget(self.lista_sospechosos)

        layout.addWidget(QLabel("Alertas IDS:"))
        self.lista_alertas = QListWidget()
        layout.addWidget(self.lista_alertas)

        whitelist_layout = QHBoxLayout()
        self.input_mac = QLineEdit()
        self.input_mac.setPlaceholderText("Agregar MAC a whitelist (ej: 00-14-22-01-23-45)")
        self.btn_agregar_mac = QPushButton("Agregar MAC")
        whitelist_layout.addWidget(self.input_mac)
        whitelist_layout.addWidget(self.btn_agregar_mac)
        layout.addLayout(whitelist_layout)

        self.setLayout(layout)

        self.btn_escanear.clicked.connect(self.escanear_red)
        self.btn_detectar.clicked.connect(self.detectar_fantasmas)
        self.btn_agregar_mac.clicked.connect(self.agregar_mac_whitelist)

    def escanear_red(self):
        self.btn_escanear.setEnabled(False)
        self.lista_dispositivos.clear()
        self.lista_sospechosos.clear()
        self.lista_alertas.clear()

        def trabajo():
            self.monitor.escanear_red()
            dispositivos = self.monitor.obtener_dispositivos()
            self.lista_dispositivos.clear()
            for d in dispositivos:
                self.lista_dispositivos.addItem(f"{d['ip']} | {d['mac']}")
            self.btn_escanear.setEnabled(True)

        threading.Thread(target=trabajo, daemon=True).start()

    def detectar_fantasmas(self):
        self.monitor.detectar_fantasmas()
        sospechosos = self.monitor.obtener_sospechosos()
        alertas = self.monitor.obtener_alertas_ids()

        self.lista_sospechosos.clear()
        for d in sospechosos:
            self.lista_sospechosos.addItem(f"{d['ip']} | {d['mac']}")

        self.lista_alertas.clear()
        for alerta in alertas:
            self.lista_alertas.addItem(alerta)

    def agregar_mac_whitelist(self):
        mac = self.input_mac.text().strip().lower()
        if not mac:
            QMessageBox.warning(self, "Error", "Debe ingresar una MAC válida.")
            return
        if mac in self.monitor.whitelist:
            QMessageBox.information(self, "Info", "MAC ya está en la whitelist.")
            return
        self.monitor.whitelist.add(mac)
        QMessageBox.information(self, "Éxito", f"MAC {mac} agregada a whitelist.")
        self.input_mac.clear()

