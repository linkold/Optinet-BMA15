import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QLabel, QStackedWidget, QSizePolicy, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QMessageBox,QGroupBox,QPlainTextEdit,QListWidget,QLineEdit)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
#import platform
#import netifaces
import psutil
import subprocess
#from scapy.all import ARP, Ether, srp, get_if_list, get_if_addr
import pyqtgraph as pg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


cantidad_dispositivos = 0
dispositivos = []  
estado = ""
ip_adaptador = ""
ip_escaneadas = []  # Variable global para almacenar todas las IPs escaneadas
class OptiNet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"OptiNet -- {estado}")
        self.setMinimumSize(1280, 800)
        self.UI()
        self.show()
        self.actualizador()
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
        
        barra_lat = QVBoxLayout()
        
        def Boton(text):
            boton = QPushButton(text)
            boton.setFont(QFont("", 16))
            boton.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            return boton
        
        self.estado_internet = QLabel()
        self.estado_internet.setFont(QFont("Arial",15))
        if datos_variantes.conectado():
            self.estado_internet.setText("Esta Conectado\na internet ✅")
        else:
            self.estado_internet.setText("No esta Conectado\na internet ❌")
        
        boton_principal = Boton("Inicio")
        boton_trafico = Boton("Trafico en Tiempo Real")
        boton_dispositivos = Boton("Dispositivos")
        boton_wifi = Boton("Wi-Fi")
        boton_ancho_banda = Boton("Ancho de Banda")
        boton_reporte = Boton("Reportes")
        boton_control_parental = Boton("Control Parental")
        barra_lat.addWidget(boton_principal)
        barra_lat.addWidget(boton_trafico)
        barra_lat.addWidget(boton_dispositivos)
        barra_lat.addWidget(boton_wifi)
        barra_lat.addWidget(boton_ancho_banda)
        barra_lat.addWidget(boton_reporte)
        barra_lat.addWidget(boton_control_parental)
        barra_lat.addWidget(self.estado_internet)
        barra_lat.setAlignment(self.estado_internet,Qt.AlignmentFlag.AlignCenter)
        self.stack = QStackedWidget()
        
        self.pagina_principal = self.principal()
        self.pagina_trafico = self.trafico()
        self.pagina_dispositivos = self.dispositivos()
        self.pagina_wifi = self.wifi()
        self.pagina_ancho_banda = self.ancho_banda()
        self.pagina_reporte = self.reporte()
        self.pagina_control_parental = self.control_parental()
        for pagina in [self.pagina_principal, self.pagina_trafico, self.pagina_dispositivos, self.pagina_wifi, self.pagina_ancho_banda, self.pagina_reporte, self.pagina_control_parental]:
            self.stack.addWidget(pagina)
        
        boton_principal.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_principal))
        boton_trafico.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_trafico))
        boton_dispositivos.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_dispositivos))
        boton_wifi.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_wifi))
        boton_ancho_banda.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_ancho_banda))
        boton_reporte.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_reporte))
        boton_control_parental.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_control_parental))
        
        main_layout.addLayout(barra_lat, 1)
        main_layout.addWidget(self.stack, 6)
        
        self.setCentralWidget(main_widget)
    def principal(self):
        pagina = QWidget()
        laymain = QVBoxLayout(pagina)
        lay1 = QVBoxLayout()
        tamano_letra_principal_menor = 15
        tamano_letra_principal_mayor = 20
        fuente_letra = "Arial"
        # Título
        label_titulo1 = QLabel("Bienvenido a Optinet")
        label_titulo1.setFont(QFont(fuente_letra, 25))
        lay1.addWidget(label_titulo1)
        lay1.setAlignment(label_titulo1, Qt.AlignmentFlag.AlignCenter)
        # Analisis del Computador
        layout_info = QHBoxLayout()
        # --- RAM ---
        
        mem = psutil.virtual_memory()
        ram_usada = round(mem.used / (1024 ** 3), 2)
        self.ram_total = round(mem.total / (1024 ** 3), 2)
        self.Ram_uso_label = QLabel(f"Usada: {ram_usada} GB")
        self.Ram_total_label = QLabel(f"Total: {self.ram_total} GB")
        
        self.Ram_uso_label.setFont(QFont(fuente_letra,tamano_letra_principal_menor))
        self.Ram_total_label.setFont(QFont(fuente_letra,tamano_letra_principal_menor))
        
        grupo1 = QGroupBox("Memoria RAM")
        grupo1.setFont(QFont(fuente_letra,tamano_letra_principal_mayor))
        grupo1_layout = QVBoxLayout()
        grupo1_layout.addWidget(self.Ram_uso_label)
        grupo1_layout.addWidget(self.Ram_total_label)
        grupo1.setLayout(grupo1_layout)
        # --- CPU ---
        cpu_uso = psutil.cpu_percent(interval=1)
        self.Cpu_uso_label = QLabel(f"Uso actual: {cpu_uso}%")
        self.Cpu_nucleos_label = QLabel(f"Núcleos: {psutil.cpu_count(logical=True)}")
        
        self.Cpu_uso_label.setFont(QFont(fuente_letra,tamano_letra_principal_menor))
        self.Cpu_nucleos_label.setFont(QFont(fuente_letra,tamano_letra_principal_menor))
        
        grupo2 = QGroupBox("Uso del CPU")
        grupo2.setFont(QFont(fuente_letra,tamano_letra_principal_mayor))
        grupo2_layout = QVBoxLayout()
        grupo2_layout.addWidget(self.Cpu_uso_label)
        grupo2_layout.addWidget(self.Cpu_nucleos_label)
        grupo2.setLayout(grupo2_layout)
        # --- Disco ---
        
        disco_total = disco_usado = 0
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disco_total += usage.total
                disco_usado += usage.used
            except Exception:
                pass
        self.disco_total_label = QLabel(f"Total: {round(disco_total / (1024 ** 3), 2)} GB")
        self.disco_usado_label = QLabel(f"Usado: {round(disco_usado / (1024 ** 3), 2)} GB")
        self.disco_total_label = QLabel(f"Total: {round(disco_total / (1024 ** 3), 2)} GB")
        self.disco_usado_label = QLabel(f"Usado: {round(disco_usado / (1024 ** 3), 2)} GB")
        
        self.disco_total_label.setFont(QFont(fuente_letra,tamano_letra_principal_menor))
        self.disco_usado_label.setFont(QFont(fuente_letra,tamano_letra_principal_menor))
        
        grupo3 = QGroupBox("Disco")
        grupo3.setFont(QFont(fuente_letra,tamano_letra_principal_mayor))
        grupo3_layout = QVBoxLayout()
        grupo3_layout.addWidget(self.disco_total_label)
        grupo3_layout.addWidget(self.disco_usado_label)
        grupo3.setLayout(grupo3_layout)
        ## --- Batería ---
        try:
            bateria = psutil.sensors_battery()
            self.bateria_porcentaje_label = QLabel(f"Porcentaje: {bateria.percent}%")
            self.bateria_estado_label = QLabel("Cargando" if bateria.power_plugged else "No Cargando")
        except Exception:
            self.bateria_porcentaje_label = QLabel("No hay Hay bateria")
            self.bateria_estado_label = QLabel("")
        self.bateria_estado_label.setFont(QFont(fuente_letra,tamano_letra_principal_menor))
        self.bateria_porcentaje_label.setFont(QFont(fuente_letra,tamano_letra_principal_menor))
        grupo4 = QGroupBox("Batería")
        grupo4.setFont(QFont(fuente_letra,tamano_letra_principal_mayor))
        grupo4_layout = QVBoxLayout()
        try:
            grupo4_layout.addWidget(self.bateria_porcentaje_label)
            grupo4_layout.addWidget(self.bateria_estado_label)
        except Exception:
            pass
        grupo4.setLayout(grupo4_layout)
        #--- Conectividad ---
        self.internet_estado_label = QLabel("Espere...")
        
        self.internet_estado_label.setFont(QFont("",tamano_letra_principal_menor))
        
        grupo5 = QGroupBox("Conectividad")
        grupo5.setFont(QFont(fuente_letra,tamano_letra_principal_mayor))
        grupo5_layout = QVBoxLayout()
        grupo5_layout.addWidget(self.internet_estado_label)
        
        grupo5.setLayout(grupo5_layout)
        
        
        self.x = list(range(60))  # últimos 60 segundos
        self.y_cpu = [0] * 60          # uso del CPU inicial
        self.y_ram = [0] * 60          # uso del RAM inicial
        
        self.cpu = pg.PlotWidget(title="Uso del CPU (%)")
        self.curva1 = self.cpu.plot(self.x, self.y_cpu, pen=pg.mkPen('r', width=2))
        
        self.ram = pg.PlotWidget(title="Uso del RAM (%)")
        self.curva2 = self.ram.plot(self.x, self.y_ram, pen=pg.mkPen('r', width=2))
        # Añadir todos los cuadros al layout principal
        layout_info.addWidget(grupo1)
        layout_info.addWidget(grupo2)
        layout_info.addWidget(grupo3)
        layout_info.addWidget(grupo4)
        layout_info.addWidget(grupo5)
        layout_graficas = QHBoxLayout()
        
        layout_graficas.addWidget(self.cpu)
        layout_graficas.addWidget(self.ram)
        
        laymain.addLayout(lay1, 1)
        laymain.addLayout(layout_info, 3)
        laymain.addLayout(layout_graficas,5)
        return pagina
    def trafico(self):
        pico_maximo_subida = "Sin Informacion" 
        pico_maximo_descarga = "Sin informacion"
        
        pagina = QWidget()
        layoutmain = QVBoxLayout(pagina)
        layh1 = QHBoxLayout()
        titulo = QLabel("Trafico En Tiempo Real")
        titulo.setFont(QFont("Arial",20))
        #grafica provisional 
        self.x = list(range(60)) 
        self.y_cpu = [0] * 60    
        self.y_ram = [0] * 60    
        
        self.cpu = pg.PlotWidget(title="Subida")
        
        
        self.ram = pg.PlotWidget(title="Descarga")
        
        
        maximos = QLabel(f"Pico Maximo Descarga:  {pico_maximo_descarga}\t\t||\t\tPico Maximo Subida:  {pico_maximo_subida}")
        self.tabla_dispositivos1 = QTableWidget(self)
        self.tabla_dispositivos1.setColumnCount(5)
        self.tabla_dispositivos1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_dispositivos1.setHorizontalHeaderLabels(["Protocolo","IP Origen","IP Destino","MAC Origuen","MAC Destino"])
        
        layh1.addWidget(self.cpu)
        layh1.addWidget(self.ram)
        layoutmain.addWidget(titulo)
        layoutmain.addLayout(layh1)
        layoutmain.addWidget(maximos)
        layoutmain.setAlignment(maximos,Qt.AlignmentFlag.AlignHCenter)
        layoutmain.setAlignment(titulo,Qt.AlignmentFlag.AlignHCenter)
        layoutmain.addWidget(self.tabla_dispositivos1)
        return pagina
    def dispositivos(self):
        global cantidad_dispositivos
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        lay2 = QVBoxLayout()
        lay3 = QHBoxLayout()
        
        grupo = QGroupBox("Informacion")
        self.label_estado = QLabel("Esperando actualización...")
        layV1 = QVBoxLayout()
        Cantidad = QLabel(f"Cantidad de Dispositivos\nConectados: {cantidad_dispositivos}")
        estado = self.label_estado
        layV1.addWidget(Cantidad)
        layV1.addWidget(estado)
        grupo.setLayout(layV1)
        
        boton_actualizacion = QPushButton("Actualizar")
        boton_actualizacion.setFont(QFont("Arial",20))
        boton_actualizacion.setSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Preferred)
        boton_actualizacion.clicked.connect(self.actualizar_tabla_dispositivos)
        self.tabla_dispositivos = QTableWidget(self)
        self.tabla_dispositivos.setColumnCount(2)
        self.tabla_dispositivos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_dispositivos.setHorizontalHeaderLabels(["IP", "MAC"])
        registro = QPlainTextEdit()
        registro.setReadOnly(True)
        
        lay3.addWidget(registro)
        lay3.addWidget(grupo)
        
        lay1.addWidget(self.tabla_dispositivos,6)
        lay1.addWidget(boton_actualizacion)
        lay1.addLayout(lay3,3)
        return pagina
    def wifi(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        self.tabla1 = QTableWidget(self)
        self.tabla1.setColumnCount(7)
        self.tabla1.setHorizontalHeaderLabels(["SSID","Intensidad de señal","Canal","Banda","Tipo de Seguridad","Direccion MAC","tipo Wi-Fi"])
        self.tabla1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        red1 = datos_variantes.wifi_datos_windows()
        self.tabla1.setRowCount(len(red1))
        for linea, red in enumerate(red1):
            self.tabla1.setItem(linea, 0, QTableWidgetItem(red["SSID"]))
            self.tabla1.setItem(linea, 1, QTableWidgetItem(red["Intensidad"]))
            self.tabla1.setItem(linea, 2, QTableWidgetItem(red["Canal"]))
            self.tabla1.setItem(linea, 3, QTableWidgetItem(f"{red["Banda"]}GHz"))
            self.tabla1.setItem(linea, 4, QTableWidgetItem(red["Seguridad"]))
            self.tabla1.setItem(linea, 5, QTableWidgetItem(red["MAC"]))
            self.tabla1.setItem(linea, 6, QTableWidgetItem(red["Wi-fi"]))
            
        self.figura, self.x1 = plt.subplots()
        self.canvas = FigureCanvas(self.figura)
        self.figura.patch.set_facecolor('black')
        self.x1.set_facecolor('black')           
        ssids = [red["SSID"] for red in red1]
        intensidades = [int(red["Intensidad"].replace("%", "")) for red in red1]
        self.x1.barh(ssids, intensidades, color='white')
        self.x1.set_xlabel("Intensidad (%)", color='white')
        self.x1.set_title("Redes Wi-Fi disponibles", color='white')
        self.x1.tick_params(axis='x', colors='white')
        self.x1.tick_params(axis='y', colors='white')
        for i, v in enumerate(intensidades):
            self.x1.text(v + 1, i, f"{v}%", va='center', color='white')
            
        label1 = QLabel()
        label1.setFont(QFont("Arial",20))
        label1.setText("Redes Disponibles en el entorno")
        layoutH1 = QVBoxLayout()
        layoutH1.addWidget(label1)
        layoutH1.addWidget(self.tabla1)
        layoutH1.setAlignment(label1, Qt.AlignmentFlag.AlignCenter)
        layoutH2 = QHBoxLayout()
        
        label = QGroupBox("Informacion")
        lay = QVBoxLayout()
        label1_1 = QLabel("Redes Detectadas: 12")
        label1_2 = QLabel("Sugerencias\t\t\t")
        lay.addWidget(label1_1)
        lay.addWidget(label1_2)
        label.setLayout(lay)

        
        self.ram = pg.PlotWidget(title="SSID vs Canal")
        
        layoutH2.addWidget(self.canvas)
        layoutH2.addWidget(self.cpu)
        layoutH2.addWidget(label)
        
        laymain = QVBoxLayout()
        laymain.addLayout(layoutH1,3)
        laymain.addLayout(layoutH2, 1)
        lay1.addLayout(laymain)
        datos_variantes.wifi_datos_windows()
        return pagina
    def ancho_banda(self):
        self.estado_boton_actualzizar_banda = "Actualizar"
        
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)                
        titulo = QLabel("Control de Ancho de Banda")
        titulo.setFont(QFont("Arial",20))
        
        boton = QPushButton(self.estado_boton_actualzizar_banda)
        boton.setSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Preferred)
        self.tabla_dispositivos2 = QTableWidget(self)
        self.tabla_dispositivos2.setColumnCount(7)
        self.tabla_dispositivos2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_dispositivos2.setHorizontalHeaderLabels(["IP","MAC","Velocidad de Bajada","Velocidad Subida","Nombre","Total Usado","%Red"])
        
        #grafica provisional 
        self.x = list(range(60)) 
        self.y_cpu = [0] * 60     
        
        self.cpu = pg.PlotWidget(title="IP vs %Red")
        lay2 = QHBoxLayout()
        lay2.addWidget(self.cpu)
        
        lay1.addWidget(titulo)
        lay1.addWidget(self.tabla_dispositivos2,3)
        lay1.addWidget(boton)
        lay1.addLayout(lay2,2)
        lay1.setAlignment(titulo,Qt.AlignmentFlag.AlignHCenter)
        return pagina
    def reporte(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        titulo = QLabel("Reportes")
        maingrupo = QGroupBox()
        layh1 = QHBoxLayout()
        maingrupo.setLayout(layh1)
        lay1.addWidget(titulo,1)
        lay1.addWidget(maingrupo,10)
        return pagina
    def soporte(self):
        """abrir pagina de ayuda"""
        pass
    def control_parental(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        titulo = QLabel("Control Parental")
        self.lista = QListWidget()
        label1_2 = QLabel("Agregar sitio Web")
        web_bloqueo = QLineEdit()
        
        def agregar(web):
            self.lista.addItem(web)
            
        def eliminar():
            elemento = self.lista.selectedItems()
            if elemento:
                for item in elemento:
                    self.lista.takeItem(self.lista.row(item))
        
        lay2 = QHBoxLayout()
        boton_agregar = QPushButton("Agregar")
        boton_Eliminar = QPushButton("Eliminar")
        boton_agregar.clicked.connect(lambda: agregar(web_bloqueo.text()))
        boton_Eliminar.clicked.connect(eliminar)
        
        lay2.addWidget(label1_2)
        lay2.addWidget(web_bloqueo)
        titulo.setFont(QFont("Arial",20))
        lay1.addWidget(titulo)
        lay1.addWidget(self.lista)
        lay1.addLayout(lay2)
        lay1.addWidget(boton_agregar)
        lay1.addWidget(boton_Eliminar)
        
        return pagina
    
    def actualizar_tabla_dispositivos(self):
        pass
    
    def actualizador(self):
        timer = QTimer(self)
        timer.timeout.connect(self.actualizar_informacion)
        timer.timeout.connect(self.actualizar_tabla_cpu)
        timer.timeout.connect(self.actualizar_tabla_ram)
        timer.start(1000)
        
    def actualizar_informacion(self):
        mem = psutil.virtual_memory()
        self.ram_usada = round(mem.used / (1024 ** 3), 2)
        self.Ram_uso_label.setText(f"Usada: {self.ram_usada} GB")
        
        self.cpu_uso = psutil.cpu_percent(interval=0.1)
        self.Cpu_uso_label.setText(f"Uso actual: {self.cpu_uso}%")
        
        disco_total = 0
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disco_usado += usage.used
            except Exception:
                pass
        self.disco_total_label = QLabel(f"Total: {round(disco_total / (1024 ** 3), 2)} GB")
        try:
            bateria = psutil.sensors_battery()
            self.bateria_porcentaje_label.setText(f"Porcentaje: {bateria.percent}%")
            self.bateria_estado_label.setText("Cargando" if bateria.power_plugged else "No Cargando")
            self.internet_estado_label.setText("No esta Conectado\na Internet ❌")
        except Exception:
            pass
        if datos_variantes.conectado():
            self.estado_internet.setText("Esta Conectado\na internet ✅")
            self.internet_estado_label.setText("Conectado a\nInternet ✅")
        else:
            self.estado_internet.setText("No esta Conectado\na internet ❌")
            self.internet_estado_label.setText("No esta Conectado\na Internet ❌")
            
        red1 = datos_variantes.wifi_datos_windows()
        self.tabla1.setRowCount(len(red1))
        for linea, red in enumerate(red1):
            self.tabla1.setItem(linea, 0, QTableWidgetItem(red["SSID"]))
            self.tabla1.setItem(linea, 1, QTableWidgetItem(red["Intensidad"]))
            self.tabla1.setItem(linea, 2, QTableWidgetItem(red["Canal"]))
            self.tabla1.setItem(linea, 3, QTableWidgetItem(f"{red["Banda"]}GHz"))
            self.tabla1.setItem(linea, 4, QTableWidgetItem(red["Seguridad"]))
            self.tabla1.setItem(linea, 5, QTableWidgetItem(red["MAC"]))
            self.tabla1.setItem(linea, 6, QTableWidgetItem(red["Wi-fi"]))
            
        self.x1.clear()
        
        self.figura.patch.set_facecolor('black')
        self.x1.set_facecolor('black') 
        
        ssids = [red["SSID"] for red in red1]
        intensidades = [int(red["Intensidad"].replace("%", "")) for red in red1]
        
        self.x1.barh(ssids, intensidades, color='white')
        #self.x1.set_xlabel("Intensidad (%)", color='white', labelpad=30)
        
        self.x1.tick_params(axis='x', colors='white', labelsize = 10)
        self.x1.tick_params(axis='y', colors='white', labelsize = 10)
        
        self.figura.tight_layout()
        self.figura.canvas.draw()
        
        for i, v in enumerate(intensidades):
            self.x1.text(v + 1, i, f"{v}%", va='center', color='white')
        
        
    def actualizar_tabla_cpu(self):
        self.y_cpu = self.y_cpu[1:] + [self.cpu_uso]  # desliza los valores
        self.curva1.setData(self.x, self.y_cpu)
    
    def actualizar_tabla_ram(self):
        ram_usada_porcentaje = (self.ram_usada*100)/self.ram_total
        self.y_ram = self.y_ram[1:] + [ram_usada_porcentaje]  # desliza los valores
        self.curva2.setData(self.x, self.y_ram)
        
class datos_variantes:
    
    def conectado():
        try:
            salida = subprocess.run(["ping", "-n", "1", "google.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
            return salida.returncode == 0
        except Exception:
            return False  
        
    def wifi_datos_windows():
        resultado = subprocess.check_output("netsh wlan show networks mode=bssid", shell=True).decode("utf-8",errors="ignore")
        lineas_1 = resultado.split("\n")
        
        lista = []
        red = {}
        
        radio_tipos = {
        "802.11a": "Wi-Fi 1",
        "802.11b": "Wi-Fi 1",
        "802.11g": "Wi-Fi 3",
        "802.11n": "Wi-Fi 4",
        "802.11ac": "Wi-Fi 5",
        "802.11ax": "Wi-Fi 6",
        "802.11be": "Wi-Fi 7"
        }
        canales_rango_4G = {
            "1": "1 Rango(2401 MHz - 2423 MHz)",
            "2": "2 Rango(2406 MHz - 2428 MHz)",
            "3": "3 Rango(2411 MHz - 2433 MHz)",
            "4": "4 Rango(2416 MHz - 2438 MHz)",
            "5": "5 Rango(2421 MHz - 2443 MHz)",
            "6": "6 Rango(2426 MHz - 2448 MHz)",
            "7": "7 Rango(2431 MHz - 2453 MHz)",
            "8": "8 Rango(2436 MHz - 2458 MHz)",
            "9": "9 Rango(2441 MHz - 2463 MHz)",
            "10": "10 Rango(2446 MHz - 2468 MHz)",
            "11": "11 Rango(2451 MHz - 2473 MHz)",
            "12": "12 Rango(2456 MHz - 2478 MHz)",
            "13": "13 Rango(2461 MHz - 2483 MHz)",
            "14": "14 Rango(2473 MHz - 2495 MHz)"
        }

        canales_rango_5G = {
            "36": '36 Frecuencia 5180 MHz',
            "40": '40 Frecuencia 5200 MHz',
            "44": '44 Frecuencia 5220 MHz',
            "48": '48 Frecuencia 5240 MHz',
            "52": '52 Frecuencia 5260 MHz',
            "56": '56 Frecuencia 5280 MHz',
            "60": '60 Frecuencia 5300 MHz',
            "64": '64 Frecuencia 5320 MHz',
            "100": '100 Frecuencia 5500 MHz',
            "104": '104 Frecuencia 5520 MHz',
            "108": '108 Frecuencia 5540 MHz',
            "112": '112 Frecuencia 5560 MHz',
            "116": '116 Frecuencia 5580 MHz',
            "120": '120 Frecuencia 5600 MHz',
            "124": '124 Frecuencia 5620 MHz',
            "128": '128 Frecuencia 5640 MHz',
            "132": '132 Frecuencia 5660 MHz',
            "136": '136 Frecuencia 5680 MHz',
            "140": '140 Frecuencia 5700 MHz',
            "144": '144 Frecuencia 5720 MHz',
            "149": '149 Frecuencia 5745 MHz',
            "153": '153 Frecuencia 5765 MHz',
            "157": '157 Frecuencia 5785 MHz',
            "161": '161 Frecuencia 5805 MHz',
            "165": '165 Frecuencia 5825 MHz'
        }
        
        for linea in lineas_1:
            if "SSID" in linea and "BSSID" not in linea:
                if red:
                    lista.append(red)
                    red = {}
                if linea.split(":",1)[1].strip() == "":
                    red["SSID"] = "Red Oculta"
                else:
                    red["SSID"] = linea.split(":",1)[1].strip()
            elif "Signal" in linea:
                red["Intensidad"] = linea.split(":",1)[1].strip()
            elif "Channel            " in linea:
                try:
                    red["Canal"] = canales_rango_4G[str(linea.split(":",1)[1].split()[0])]
                except:
                    try:
                        red["Canal"] = canales_rango_5G[str(linea.split(":",1)[1].split()[0])]
                    except:
                        red["Canal"] = str(linea.split(":",1)[1].split()[0])
                        
            elif "Band" in linea:
                red["Banda"] = linea.split(":",1)[1].split()[0]
            elif "Authentication" in linea:
                red["Seguridad"] = linea.split(":",1)[1].split()[0]
            elif "BSSID 1" in linea:
                red["MAC"] = linea.split(":",1)[1].split()[0]
            elif "Radio type" in linea:
                try:
                    red['Wi-fi'] = radio_tipos[linea.split(":",1)[1].split()[0]]
                except Exception:
                    red["Wi-fi"] = "Error"
        if red:
            lista.append(red)
        return lista
    
    def wifi_datos_linux(self):
        pass
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = OptiNet()
    sys.exit(app.exec())
