import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QSizePolicy, QTableWidget, QTableWidgetItem)
from PyQt6.QtGui import QFont, QAction
import nmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal

dispositivos = []  
estado = "beta"

class OptiNet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"OptiNet -- {estado}")
        self.setMinimumSize(1280, 800)
        self.UI()
        self.show()
    def UI(self):
        menu = self.menuBar()
        menu.setStyleSheet("background-color: black;")
        
        menu_config = menu.addMenu("Configuracion")
        menu_ayuda = menu.addMenu("Ayuda")
        
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        menu_config.addAction(exit_action)
        
        ayuda_action = QAction("Soporte", self)
        ayuda_action.triggered.connect(self.soporte)
        menu_ayuda.addAction(ayuda_action)
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        """barra principal"""
        barra_lat = QVBoxLayout()
        def Boton(text):
            boton = QPushButton(text)
            boton.setFont(QFont("", 16))
            boton.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            return boton
        
        boton_principal = Boton("Inicio")
        boton_trafico = Boton("Trafico en Tiempo Real")
        boton_dispositivos = Boton("Dispositivos")
        boton_wifi = Boton("Wi-Fi")
        boton_ancho_banda = Boton("Ancho de Banda")
        boton_reporte = Boton("Reportes")
        boton_left = Boton("jarvis abre\nleft")
        
        barra_lat.addWidget(boton_principal)
        barra_lat.addWidget(boton_trafico)
        barra_lat.addWidget(boton_dispositivos)
        barra_lat.addWidget(boton_wifi)
        barra_lat.addWidget(boton_ancho_banda)
        barra_lat.addWidget(boton_reporte)
        barra_lat.addWidget(boton_left)
        
        self.stack = QStackedWidget()
        
        self.pagina_principal = self.principal()
        self.pagina_trafico = self.trafico()
        self.pagina_dispositivos = self.dispositivos()
        self.pagina_wifi = self.wifi()
        self.pagina_ancho_banda = self.ancho_banda()
        self.pagina_reporte = self.reporte()
        self.pagina_left = self.reporte()
        
        for pagina in [self.pagina_principal, self.pagina_trafico, self.pagina_dispositivos, self.pagina_wifi, self.pagina_ancho_banda, self.pagina_reporte, self.pagina_left]:
            self.stack.addWidget(pagina)
        
        boton_principal.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_principal))
        boton_trafico.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_trafico))
        boton_dispositivos.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_dispositivos))
        boton_wifi.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_wifi))
        boton_ancho_banda.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_ancho_banda))
        boton_reporte.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_reporte))
        boton_left.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_left))
        
        main_layout.addLayout(barra_lat, 1)
        main_layout.addWidget(self.stack, 6)
        
        self.setCentralWidget(main_widget)
    def soporte(self):
        """abrir pagina de ayuda"""
        pass
    
    def trafico(self):
        pagina = QWidget()
        layoutmain = QVBoxLayout(pagina)
        label = QLabel("Información de tráfico")
        layoutmain.addWidget(label)
        return pagina
    def dispositivos(self):
        self.label_estado = QLabel("Esperando actualización...")
        pagina = QWidget()
        lay1 = QHBoxLayout(pagina)
        lay2 = QVBoxLayout()
        self.tabla_dispositivos = QTableWidget(self)
        self.tabla_dispositivos.setRowCount(23)
        self.tabla_dispositivos.setColumnCount(2)
        self.tabla_dispositivos.setColumnWidth(0,425)
        self.tabla_dispositivos.setColumnWidth(1,425)
        self.tabla_dispositivos.setHorizontalHeaderLabels(["IP", "MAC"])
        boton_actualizacion = QPushButton("Actualizar")
        boton_actualizacion.setMaximumSize(100, 100)
        boton_actualizacion.clicked.connect(self.actualizar_tabla_dispositivos)
        
        lay2.addWidget(self.label_estado)
        lay2.addWidget(boton_actualizacion)
        
        lay1.addWidget(self.tabla_dispositivos, 5)
        lay1.addLayout(lay2, 3)
        return pagina
    def wifi(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        label = QLabel("Wi-Fi")
        lay1.addWidget(label)
        return pagina
    def ancho_banda(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        label = QLabel("Ancho de Banda")
        lay1.addWidget(label)
        return pagina
    def reporte(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        label = QLabel("Reportes")
        lay1.addWidget(label)
        return pagina
    def principal(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        label = QLabel("Página Principal")
        lay1.addWidget(label)
        return pagina
    def actualizar_tabla_dispositivos(self):
        # Se actualiza el estado para mostrar "Cargando..."
        self.label_estado.setText("Cargando...")
        
        # Creamos un thread para escanear los dispositivos y evitar congelar la GUI
        self.thread = DispositivosThread()
        self.thread.dispositivos_actualizados.connect(self.actualizar_tabla)
        self.thread.start()
    def actualizar_tabla(self, dispositivos):
        self.tabla_dispositivos.setRowCount(0)
        for dispositivo in dispositivos:
            row_position = self.tabla_dispositivos.rowCount()
            self.tabla_dispositivos.insertRow(row_position)
            self.tabla_dispositivos.setItem(row_position, 0, QTableWidgetItem(dispositivo[0]))
            self.tabla_dispositivos.setItem(row_position, 1, QTableWidgetItem(dispositivo[1]))
        
        self.label_estado.setText("Actualizado")
class DispositivosThread(QThread):
    dispositivos_actualizados = pyqtSignal(list)
    def run(self):
        dispositivos = Dispositivos.escanear_dispositivos("192.168.18.0/24")
        #dispositivos += Dispositivos.escanear_dispositivos("192.168.137.0/24")
        self.dispositivos_actualizados.emit(dispositivos)
class Dispositivos:
    @staticmethod
    def escanear_dispositivos(red="192.168.18.0/24"):
        nm = nmap.PortScanner()
        print(f"Escaneando la red {red}...")
        nm.scan(hosts=red, arguments='-sn')
        dispositivos = []
        for host in nm.all_hosts():
            ip = host
            mac = nm[host]['addresses'].get('mac', 'MAC no disponible')
            dispositivos.append([ip, mac])
        return dispositivos
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = OptiNet()
    sys.exit(app.exec())