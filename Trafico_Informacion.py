import sys
import paramiko
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel,QHeaderView
)
from PyQt6.QtCore import pyqtSignal, QThread


class TcpdumpThread(QThread):
    nueva_linea = pyqtSignal(str)

    def __init__(self, ip, usuario, password):
        super().__init__()
        self.ip = ip
        self.usuario = usuario
        self.password = password
        self._stop_flag = False

    def run(self):
        try:
            cliente = paramiko.SSHClient()
            cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            cliente.connect(self.ip, username=self.usuario, password=self.password)

            comando = "sudo tcpdump -i wlan0 -n -l"
            stdin, stdout, stderr = cliente.exec_command(comando, get_pty=True)
            stdin.write(self.password + "\n")
            stdin.flush()

            for linea in iter(stdout.readline, ""):
                if self._stop_flag:
                    break
                self.nueva_linea.emit(linea.strip())

            cliente.close()

        except Exception as e:
            self.nueva_linea.emit(f"[ERROR] {str(e)}")

    def stop(self):
        self._stop_flag = True
        self.terminate()


class SnifferWidget(QWidget):
    def __init__(self, ip, usuario, password, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sniffer TCPDump - wlan0")
        self.resize(1000, 600)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Hora", "Protocolo", "IP Origen", "Puerto Origen",
            "IP Destino", "Puerto Destino", "Info"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.label = QLabel(f"Conectado a {usuario}@{ip} (interfaz: wlan0)")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.tabla)
        self.setLayout(layout)

        self.hilo = TcpdumpThread(ip, usuario, password)
        self.hilo.nueva_linea.connect(self.agregar_linea)
        self.hilo.start()

    def agregar_linea(self, linea):
        if "[ERROR]" in linea:
            self.label.setText(linea)
            return

        datos = self.parsear_linea_tcpdump(linea)
        if datos:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            for i, valor in enumerate(datos):
                self.tabla.setItem(fila, i, QTableWidgetItem(valor))
                self.tabla.scrollToItem(self.tabla.item(fila,0))

    def parsear_linea_tcpdump(self, linea):
        try:
            partes = linea.split()
            hora = partes[0]
            protocolo = partes[1]

            if protocolo != "IP":
                return None  # Solo analizar líneas IP

            if '>' not in partes:
                return None  # No es una línea con formato esperado

            idx = partes.index('>')
            origen_completo = partes[idx - 1]
            destino_completo = partes[idx + 1].replace(":", "")
            info = ' '.join(partes[idx + 2:])

            ip_origen, puerto_origen = self.separar_ip_puerto(origen_completo)
            ip_destino, puerto_destino = self.separar_ip_puerto(destino_completo)

            return [hora, protocolo, ip_origen, puerto_origen, ip_destino, puerto_destino, info]

        except Exception as e:
            return None

    def separar_ip_puerto(self, texto):
        partes = texto.rsplit('.', 1)
        if len(partes) == 2 and partes[1].isdigit():
            return partes[0], partes[1]
        return texto, "-"

    def closeEvent(self, event):
        self.hilo.stop()
        event.accept()

