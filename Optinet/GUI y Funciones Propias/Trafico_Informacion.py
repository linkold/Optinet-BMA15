from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QListWidget, QPlainTextEdit,
    QFileDialog, QLineEdit
)
from PyQt6.QtWidgets import QMessageBox, QComboBox, QDialog, QTextEdit, QVBoxLayout
from PyQt6.QtCore import QThread, pyqtSignal
from scapy.all import sniff, IP, TCP, UDP, ICMP, get_if_list, get_if_addr
from scapy.utils import wrpcap
from datetime import datetime
import socket


class SnifferThread(QThread):
    nuevo_paquete = pyqtSignal(dict)

    def __init__(self, interfaz, filtro=None):
        super().__init__()
        self.interfaz = interfaz
        self.filtro = filtro
        self.pausar = False
        self.detener = False

    def run(self):
        try:
            sniff(
                iface=self.interfaz,
                filter=self.filtro,
                prn=self.analizar_paquete,
                store=False,
                stop_filter=lambda x: self.detener
            )
        except Exception as e:
            print(f"[ERROR] Error al iniciar el sniffer: {e}", flush=True)

    def analizar_paquete(self, paquete):
        if self.detener or self.pausar:
            return

        if IP in paquete:
            hora = datetime.now().strftime("%H:%M:%S")
            ip_origen = paquete[IP].src
            ip_destino = paquete[IP].dst
            protocolo = "Otro"
            puerto_origen = "-"
            puerto_destino = "-"

            if TCP in paquete:
                protocolo = "TCP"
                puerto_origen = paquete[TCP].sport
                puerto_destino = paquete[TCP].dport
            elif UDP in paquete:
                protocolo = "UDP"
                puerto_origen = paquete[UDP].sport
                puerto_destino = paquete[UDP].dport
            elif ICMP in paquete:
                protocolo = "ICMP"

            self.nuevo_paquete.emit({
                "hora": hora,
                "ip_origen": ip_origen,
                "puerto_origen": str(puerto_origen),
                "ip_destino": ip_destino,
                "puerto_destino": str(puerto_destino),
                "protocolo": protocolo,
                "paquete": paquete
            })


class SnifferWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analizador de Paquetes - Avanzado")
        self.resize(1100, 600)

        self.label = QLabel("Interfaz detectada: buscando...")

        # Botones
        self.boton_iniciar = QPushButton("Iniciar Captura")
        self.boton_pausa = QPushButton("Pausar Captura")
        self.boton_detener = QPushButton("Detener Captura")
        self.boton_guardar = QPushButton("Guardar Captura")

        self.boton_iniciar.clicked.connect(self.iniciar_sniffer)
        self.boton_pausa.clicked.connect(self.toggle_pausa)
        self.boton_detener.clicked.connect(self.detener_sniffer)
        self.boton_guardar.clicked.connect(self.guardar_captura)

        self.boton_pausa.setEnabled(False)
        self.boton_detener.setEnabled(False)
        self.boton_guardar.setEnabled(False)

        # Campo de filtro
        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Filtro BPF opcional (ej: tcp or udp or host 192.168.1.1)")

        # Tabla de paquetes
        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels([
            "Hora", "IP Origen", "Puerto Origen", "IP Destino", "Puerto Destino", "Protocolo"
        ])
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        # Vista de cabezales
        self.lista_cabezales = QListWidget()
        self.lista_cabezales.currentTextChanged.connect(self.mostrar_detalle_cabezal)
        self.detalles_cabezal = QPlainTextEdit()
        self.detalles_cabezal.setReadOnly(True)

        # Vista del payload
        self.payload_text = QPlainTextEdit()
        self.payload_text.setReadOnly(True)

        # Contadores
        self.contadores = {"TCP": 0, "UDP": 0, "ICMP": 0, "Otro": 0}
        self.label_contadores = QLabel("Contador de paquetes: TCP=0 | UDP=0 | ICMP=0 | Otro=0")
        self.contadores_por_ip_origen = {}
        self.contadores_por_ip_destino = {}
        self.paquetes_datos = []

        # Layouts
        layout_botones = QHBoxLayout()
        layout_botones.addWidget(self.boton_iniciar)
        layout_botones.addWidget(self.boton_pausa)
        layout_botones.addWidget(self.boton_detener)
        layout_botones.addWidget(self.boton_guardar)

        layout_izquierda = QVBoxLayout()
        layout_izquierda.addWidget(self.label)
        layout_izquierda.addWidget(self.filtro_input)
        layout_izquierda.addLayout(layout_botones)
        layout_izquierda.addWidget(self.tabla)
        layout_izquierda.addWidget(self.label_contadores)

        layout_derecha = QVBoxLayout()
        #layout_derecha.addWidget(QLabel("Cabezales del paquete"))
        #layout_derecha.addWidget(self.lista_cabezales)
        #layout_derecha.addWidget(QLabel("Contenido del cabezal"))
        #layout_derecha.addWidget(self.detalles_cabezal)
        layout_derecha.addWidget(QLabel("Payload"))
        layout_derecha.addWidget(self.payload_text)

        layout_total = QHBoxLayout()
        layout_total.addLayout(layout_izquierda, 3)
        layout_total.addLayout(layout_derecha, 2)
        self.setLayout(layout_total)

        self.hilo_sniffer = None
        self.en_pausa = False
        self.paquetes_guardados = []

        self.interfaz = self.detectar_interfaz()
        self.combo_filtro_protocolo = QComboBox()
        self.combo_filtro_protocolo.addItems(["Todos", "TCP", "UDP", "ICMP", "Otro"])
        self.combo_filtro_protocolo.currentTextChanged.connect(self.filtrar_tabla_por_protocolo)

        # Nuevo: Botón para mostrar resumen estadístico
        self.boton_resumen = QPushButton("Mostrar Resumen Estadístico")
        self.boton_resumen.clicked.connect(self.mostrar_resumen_estadistico)

        # Añadir widgets nuevos al layout botones
        layout_botones.addWidget(self.combo_filtro_protocolo)
        layout_botones.addWidget(self.boton_resumen)

        # Datos para análisis
        self.contadores_por_ip_origen = {}
        self.contadores_por_ip_destino = {}

        # Lista para almacenar todos los datos (diccionarios) de los paquetes
        self.paquetes_datos = []
        
    def detectar_interfaz(self):
        try:
            ip_local = self.ip_principal()
            for iface in get_if_list():
                try:
                    ip_iface = get_if_addr(iface)
                    if ip_iface == ip_local:
                        self.label.setText(f"Interfaz detectada: {iface}")
                        return iface
                except Exception:
                    continue
        except Exception as e:
            print(f"[ERROR] No se pudo detectar la interfaz: {e}", flush=True)
        self.label.setText("No se pudo detectar la interfaz.")
        return None

    def ip_principal(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    def iniciar_sniffer(self):
        if self.interfaz is None:
            self.label.setText("No se pudo iniciar el sniffer.")
            return

        filtro = self.filtro_input.text().strip() or None

        self.hilo_sniffer = SnifferThread(self.interfaz, filtro=filtro)
        self.hilo_sniffer.nuevo_paquete.connect(self.agregar_paquete_tabla)
        self.hilo_sniffer.start()

        self.boton_iniciar.setEnabled(False)
        self.boton_pausa.setEnabled(True)
        self.boton_detener.setEnabled(True)
        self.boton_guardar.setEnabled(True)
        self.label.setText(f"Capturando en {self.interfaz}...")

    def toggle_pausa(self):
        if self.hilo_sniffer:
            self.en_pausa = not self.en_pausa
            self.hilo_sniffer.pausar = self.en_pausa
            self.boton_pausa.setText("Reanudar Captura" if self.en_pausa else "Pausar Captura")

    def detener_sniffer(self):
        if self.hilo_sniffer:
            self.hilo_sniffer.detener = True
            self.hilo_sniffer.wait()
            self.hilo_sniffer = None

        self.label.setText("Captura detenida.")
        self.boton_iniciar.setEnabled(True)
        self.boton_pausa.setEnabled(False)
        self.boton_guardar.setEnabled(False)
        self.boton_pausa.setText("Pausar Captura")
        self.boton_detener.setEnabled(False)

    def agregar_paquete_tabla(self, datos):
        # Guardar datos para análisis
        self.paquetes_datos.append(datos)

        # Actualizar contadores por IP origen y destino
        ip_origen = datos["ip_origen"]
        ip_destino = datos["ip_destino"]
        self.contadores_por_ip_origen[ip_origen] = self.contadores_por_ip_origen.get(ip_origen, 0) + 1
        self.contadores_por_ip_destino[ip_destino] = self.contadores_por_ip_destino.get(ip_destino, 0) + 1

        # Insertar en tabla solo si filtro actual permite
        filtro_actual = self.combo_filtro_protocolo.currentText()
        if filtro_actual == "Todos" or filtro_actual == datos["protocolo"]:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            for i, key in enumerate(["hora", "ip_origen", "puerto_origen", "ip_destino", "puerto_destino", "protocolo"]):
                self.tabla.setItem(fila, i, QTableWidgetItem(datos[key]))

        # Actualizar contadores de protocolo
        protocolo = datos["protocolo"]
        self.contadores[protocolo] += 1
        txt = " | ".join(f"{k}={v}" for k, v in self.contadores.items())
        self.label_contadores.setText(f"Contador de paquetes: {txt}")

        # Guardar el paquete real para detalles y guardar
        self.paquetes_guardados.append(datos["paquete"])

        # Limpiar la lista de cabezales y llenarla con capas del paquete actual
        self.lista_cabezales.clear()
        paquete = datos["paquete"]
        capa = paquete
        while capa:
            nombre_capa = capa.__class__.__name__
            self.lista_cabezales.addItem(nombre_capa)
            capa = capa.payload
            if capa is None or capa == b"":
                break

        # Mostrar automáticamente el detalle del primer cabezal y el payload
        if self.lista_cabezales.count() > 0:
            primer_cabezal = self.lista_cabezales.item(0).text()
            self.mostrar_detalle_cabezal(primer_cabezal)
            self.mostrar_payload(paquete)
            
    def mostrar_detalle_cabezal(self, capa_nombre):
        if not self.paquetes_guardados:
            return
        paquete = self.paquetes_guardados[-1]
        capa = paquete
        while capa:
            if capa.__class__.__name__ == capa_nombre:
                self.detalles_cabezal.setPlainText(capa.show(dump=True))
                break
            capa = capa.payload
            if capa is None or capa == b"":
                break


    def guardar_captura(self):
        if not self.paquetes_guardados:
            return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar como", "", "Archivo PCAP (*.pcap)")
        if ruta:
            wrpcap(ruta, self.paquetes_guardados)
            self.label.setText("Captura guardada en archivo.")
            
    def filtrar_tabla_por_protocolo(self, protocolo):
        self.tabla.clearContents()
        self.tabla.setRowCount(0)

        for datos in self.paquetes_datos:
            if protocolo == "Todos" or datos["protocolo"] == protocolo:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                for i, key in enumerate(["hora", "ip_origen", "puerto_origen", "ip_destino", "puerto_destino", "protocolo"]):
                    self.tabla.setItem(fila, i, QTableWidgetItem(datos[key]))

    def mostrar_resumen_estadistico(self):
        texto = "Resumen estadístico de la captura:\n\n"

        texto += "Paquetes por protocolo:\n"
        for proto, count in self.contadores.items():
            texto += f"  {proto}: {count}\n"

        texto += "\nPaquetes por IP Origen:\n"
        for ip, count in sorted(self.contadores_por_ip_origen.items(), key=lambda x: x[1], reverse=True):
            texto += f"  {ip}: {count}\n"

        texto += "\nPaquetes por IP Destino:\n"
        for ip, count in sorted(self.contadores_por_ip_destino.items(), key=lambda x: x[1], reverse=True):
            texto += f"  {ip}: {count}\n"

        dlg = QDialog(self)
        dlg.setWindowTitle("Resumen Estadístico")
        layout = QVBoxLayout(dlg)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(texto)
        layout.addWidget(text_edit)
        dlg.resize(400, 500)
        dlg.exec()
    def mostrar_payload(self, paquete):
        try:
            # Extraer payload raw si existe
            payload = bytes(paquete.payload)
            if payload:
                self.payload_text.setPlainText(payload.hex())
            else:
                self.payload_text.setPlainText("(Sin payload)")
        except Exception as e:
            self.payload_text.setPlainText(f"Error al mostrar payload: {e}")

