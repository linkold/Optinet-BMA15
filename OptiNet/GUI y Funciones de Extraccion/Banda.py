import sys
import subprocess
import threading
import time
import socket
from collections import defaultdict, deque

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QApplication, QLabel, QTextEdit, QPushButton, QFileDialog
)
from PyQt6.QtCore import QTimer
from scapy.all import sniff, get_if_list, get_if_addr
from scapy.layers.inet import IP, ICMP
from ping3 import ping


class BandwidthMonitor(threading.Thread):
    def __init__(self, target_ip, iface, interval, callback):
        super().__init__(daemon=True)
        self.target_ip = target_ip
        self.iface = iface
        self.interval = interval
        self.callback = callback
        self.running = False
        self.total_bytes = 0

    def _packet_handler(self, packet):
        if packet.haslayer(IP) and not packet.haslayer(ICMP):
            ip = packet.getlayer(IP)
            if ip.src == self.target_ip or ip.dst == self.target_ip:
                self.total_bytes += len(packet)

    def _sniff_packets(self):
        sniff(prn=self._packet_handler, store=0, iface=self.iface, stop_filter=lambda _: not self.running)

    def run(self):
        self.running = True
        threading.Thread(target=self._sniff_packets, daemon=True).start()

        while self.running:
            start = self.total_bytes
            time.sleep(self.interval)
            end = self.total_bytes
            kbps = ((end - start) * 8) / 1024 / self.interval
            self.callback(kbps)

    def stop(self):
        self.running = False


class DispositivoMonitor:
    def __init__(self, ip):
        self.ip = ip
        self.start_time = None
        self.status = "Desconectado"

    def ping(self):
        try:
            if ping(self.ip, timeout=0.5) is not None:
                if self.start_time is None:
                    self.start_time = time.monotonic()
                self.status = "Conectado"
            else:
                self.status = "Desconectado"
                self.start_time = None
        except:
            self.status = "Desconectado"
            self.start_time = None
        return self.status

    def tiempo(self):
        if self.start_time and self.status == "Conectado":
            return f"{int(time.monotonic() - self.start_time)} seg"
        return "0 seg"


class BandaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor de Ancho de Banda")
        self.layout = QVBoxLayout(self)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["IP", "MAC", "Tipo", "Estado", "Tiempo", "Uso actual (kbps)"])
        self.layout.addWidget(self.tabla)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.ip_iface_map = {
            get_if_addr(iface): iface
            for iface in get_if_list()
            if get_if_addr(iface)
        }

        self.monitores = {}
        self.bandwidths = {}
        self.fila_por_ip = {}
        self.historial = defaultdict(lambda: deque(maxlen=10))
        self.consumo_total = defaultdict(float)
        self.mac_por_ip = {}
        self.ips_por_mac = defaultdict(set)

        self.area_ranking = QTextEdit()
        self.area_ranking.setReadOnly(True)
        self.layout.addWidget(QLabel("Top consumidores y conflictos:"))
        self.layout.addWidget(self.area_ranking)

        self.boton_exportar = QPushButton("Exportar historial a CSV")
        self.boton_exportar.clicked.connect(self.exportar_historial)
        self.layout.addWidget(self.boton_exportar)

        self.scan_network()

        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self.scan_network)
        self.scan_timer.start(30000)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.actualizar_todos)
        self.update_timer.start(1000)

    def scan_network(self):
        try:
            salida = subprocess.check_output(["arp", "-a"], shell=True).decode()
        except:
            return

        dispositivos = []
        bloques = salida.split("\nInterface: ")[1:]
        for bloque in bloques:
            lineas = bloque.splitlines()[1:]
            for l in lineas:
                if "dynamic" in l or "static" in l:
                    partes = l.split()
                    if len(partes) >= 3:
                        ip, mac, tipo = partes[:3]
                        if not ip.endswith(".255") and not ip.startswith(("224.", "239.", "255.")):
                            dispositivos.append([ip, mac, tipo])

        for ip, mac, tipo in dispositivos:
            if ip in self.monitores:
                continue

            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.fila_por_ip[ip] = row

            self.mac_por_ip[ip] = mac
            self.ips_por_mac[mac].add(ip)

            tipo_desc = tipo + (" (fantasma)" if tipo.lower() not in ["dynamic", "static"] else "")

            self.tabla.setItem(row, 0, QTableWidgetItem(ip))
            self.tabla.setItem(row, 1, QTableWidgetItem(mac))
            self.tabla.setItem(row, 2, QTableWidgetItem(tipo_desc))
            self.tabla.setItem(row, 3, QTableWidgetItem("..."))
            self.tabla.setItem(row, 4, QTableWidgetItem("0 seg"))
            self.tabla.setItem(row, 5, QTableWidgetItem("0.00"))

            self.monitores[ip] = DispositivoMonitor(ip)

            interfaz = None
            for iface_ip in self.ip_iface_map:
                if ".".join(iface_ip.split(".")[:3]) == ".".join(ip.split(".")[:3]):
                    interfaz = self.ip_iface_map[iface_ip]
                    break

            if interfaz:
                def make_callback(row, ip):
                    return lambda kbps: self._actualizar_consumo(ip, row, kbps)
                monitor = BandwidthMonitor(ip, interfaz, 1, make_callback(row, ip))
                monitor.start()
                self.bandwidths[ip] = monitor

    def _actualizar_consumo(self, ip, row, kbps):
        self.tabla.setItem(row, 5, QTableWidgetItem(f"{kbps:.2f}"))
        self.historial[ip].append(kbps)
        self.consumo_total[ip] += kbps

    def actualizar_todos(self):
        for ip, monitor in self.monitores.items():
            estado = monitor.ping()
            tiempo = monitor.tiempo()
            fila = self.fila_por_ip[ip]
            self.tabla.setItem(fila, 3, QTableWidgetItem(estado))
            self.tabla.setItem(fila, 4, QTableWidgetItem(tiempo))

        ranking = sorted(self.consumo_total.items(), key=lambda x: x[1], reverse=True)[:5]
        conflictos = [f"Conflicto: MAC {mac} tiene múltiples IPs: {', '.join(ips)}"
                      for mac, ips in self.ips_por_mac.items() if len(ips) > 1]

        texto = "[Top 5 IPs por consumo acumulado]\n"
        texto += "\n".join([f"{ip}: {total:.2f} kbps" for ip, total in ranking])
        if conflictos:
            texto += "\n\n[Conflictos detectados]\n" + "\n".join(conflictos)
        self.area_ranking.setPlainText(texto)

    def exportar_historial(self):
        nombre_archivo, _ = QFileDialog.getSaveFileName(self, "Guardar historial", "historial.csv", "CSV Files (*.csv)")
        if not nombre_archivo:
            return
        try:
            with open(nombre_archivo, "w") as f:
                f.write("IP," + ",".join([f"t{i+1}" for i in range(10)]) + "\n")
                for ip, datos in self.historial.items():
                    fila = f"{ip}," + ",".join(f"{v:.2f}" for v in datos)
                    f.write(fila + "\n")
        except Exception as e:
            print(f"Error exportando historial: {e}")

    def obtener_ip_local(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = BandaWidget()
    w.show()
    sys.exit(app.exec())
