
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,QHBoxLayout, QLabel, QStackedWidget, QSizePolicy, QTableWidget,QTableWidgetItem, QHeaderView, QMessageBox,QGroupBox,QPlainTextEdit,QListWidget,QLineEdit,QErrorMessage)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
import psutil
import pyqtgraph as pg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import socket
import os

from Pricipal import Datos, datos_variantes
cantidad_dispositivos = 0
dispositivos = []  
ip_adaptador = ""
ip_escaneadas = []  # Variable global para almacenar todas las IPs escaneadas
class OptiNet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OptiNet")
        self.setMinimumSize(1280, 800)
        self.Comprobar_archivos()
        self.UI()
        self.show()
        self.Comprobar_archivos()
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
        ram_usada = round(Datos.Memoria_Ram().used / (1024 ** 3), 2)
        self.ram_total = round(Datos.Memoria_Ram().total / (1024 ** 3), 2)
        self.ram_t_2 =self.ram_total
        self.ram_u_2 = ram_usada
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
        self.Cpu_uso_label = QLabel(f"Uso actual: {Datos.CPU_porcentaje()}%")
        self.Cpu_nucleos_label = QLabel(f"Núcleos: {Datos.CPU_Nucleos()}")
        self.cpu_2 = Datos.CPU_porcentaje()
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
                disco_total += psutil.disk_usage(part.mountpoint).total
                disco_usado += psutil.disk_usage(part.mountpoint).used
            except Exception:
                pass
        self.disco_total_label = QLabel(f"Total: {round(disco_total / (1024 ** 3), 2)} GB")
        self.disco_usado_label = QLabel(f"Usado: {round(disco_usado / (1024 ** 3), 2)} GB")
        
        self.disco_u_2 = round(disco_total / (1024 ** 3), 2)
        self.disco_t_2 = round(disco_usado / (1024 ** 3), 2)

        
        self.disco_total_label.setFont(QFont(fuente_letra,tamano_letra_principal_menor))
        self.disco_usado_label.setFont(QFont(fuente_letra,tamano_letra_principal_menor))
        
        grupo3 = QGroupBox("Disco")
        grupo3.setFont(QFont(fuente_letra,tamano_letra_principal_mayor))
        grupo3_layout = QVBoxLayout()
        grupo3_layout.addWidget(self.disco_total_label)
        grupo3_layout.addWidget(self.disco_usado_label)
        grupo3.setLayout(grupo3_layout)
        ## --- Batería ---
        if Datos.Bateria():
            self.bateria_porcentaje_label = QLabel(f"Porcentaje: {Datos.Bateria()[0]}%")
            self.bateria_estado_label = QLabel("Cargando" if Datos.Bateria()[1] else "No Cargando")
            self.bateria_p_2 = Datos.Bateria()[0]
        else:
            self.bateria_porcentaje_label = QLabel("No hay Hay bateria")
            self.bateria_estado_label = QLabel("")
        self.bateria_estado_label.setFont(QFont(fuente_letra,tamano_letra_principal_menor))
        self.bateria_porcentaje_label.setFont(QFont(fuente_letra,tamano_letra_principal_menor))
        grupo4 = QGroupBox("Batería")
        grupo4.setFont(QFont(fuente_letra,tamano_letra_principal_mayor))
        grupo4_layout = QVBoxLayout()
        grupo4_layout.addWidget(self.bateria_porcentaje_label)
        grupo4_layout.addWidget(self.bateria_estado_label)
        grupo4.setLayout(grupo4_layout)
        # Crear contenedor principal (puedes meterlo en un layout donde quieras)
        
        layout_grafica_disco = QHBoxLayout()

        # Crear figura y eje
        fig, ax = plt.subplots()
        canvas = FigureCanvas(fig)

        labels = []
        sizes = []
        colors = []
        explode = []

        color_usado = '#ff6666'
        color_libre = '#66cc66'

        for part in psutil.disk_partitions():
            try:
                uso = psutil.disk_usage(part.mountpoint)
                usado = uso.used / (1024**3)
                libre = uso.free / (1024**3)
                if usado > 1:
                    labels.extend([f"{part.device} Usado", f"{part.device} Libre"])
                    sizes.extend([usado, libre])
                    colors.extend([color_usado, color_libre])
                    explode.extend([0.05, 0])
            except:
                continue
        grupo_info = QGroupBox()
        layout_grupo = QVBoxLayout(grupo_info)
        self.label_titulo = QLabel("Estado y Recomendaciones:")
        self.label_titulo_0 = QLabel("Informacion:")
        self.label_titulo_0.setFont(QFont("Arial",14))
        self.label_titulo.setFont(QFont("Arial",14))
        self.label_info = QLabel(Datos.analizar_sistema()[0])
        self.label_info.setFont(QFont("Arial",10))
        self.label_titulo_1 = QLabel("Estado:")
        self.label_titulo_1.setFont(QFont("Arial",14))
        self.label_info_1 = QLabel(Datos.analizar_sistema()[1])
        self.label_info_1.setFont(QFont("Arial",10))
        self.label_titulo_2 = QLabel("Recomendaciones:")
        self.label_titulo_2.setFont(QFont("Arial",14))
        self.label_info_2 = QLabel(Datos.analizar_sistema()[2])
        self.label_info_2.setFont(QFont("Arial",10))
        
        layout_grupo.addWidget(self.label_titulo)
        layout_grupo.addWidget(self.label_titulo_0)
        layout_grupo.addWidget(self.label_info)
        layout_grupo.addWidget(self.label_titulo_1)
        layout_grupo.addWidget(self.label_info_1)
        layout_grupo.addWidget(self.label_titulo_2)
        layout_grupo.addWidget(self.label_info_2)
        grupo_info.setSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Preferred)
        # Dibujar gráfica
        ax.pie(
        sizes,
        labels=labels,
        autopct=lambda p: f'{p:.1f}%',
        startangle=90,
        colors=colors,
        explode=explode,
        textprops={'color': 'white'}
        )
        ax.set_title("Uso de Almacenamiento por Partición", color='white')
        fig.patch.set_facecolor('#1d1d1d')
        ax.set_facecolor('#1d1d1d')
    
        layout_grafica_disco.addWidget(canvas)
        #       contenedor
        #--- Conectividad ---
        self.internet_estado_label = QLabel("Espere...")
        self.internet_2 = ""
        self.internet_estado_label.setFont(QFont("",tamano_letra_principal_menor))
        
        grupo5 = QGroupBox("Conectividad")
        grupo5.setFont(QFont(fuente_letra,tamano_letra_principal_mayor))
        grupo5_layout = QVBoxLayout()
        grupo5_layout.addWidget(self.internet_estado_label)
        
        grupo5.setLayout(grupo5_layout)
        
        #Principal 2
        lay2 = QHBoxLayout()
        self.informacion = QLabel(f"CPU: {self.cpu_2} | RAM: {self.ram_u_2}/{self.ram_t_2} | Disco :{self.disco_u_2}/{self.disco_t_2} | Bateria: {self.bateria_p_2} | Internet: {self.internet_2}")
        self.informacion.setFont(QFont("Arial",14))
        
        lay2.addWidget(self.informacion)
        lay2.setAlignment(self.informacion,Qt.AlignmentFlag.AlignHCenter)
        
        #Grafica
        self.x = list(range(60)) 
        self.y_cpu = [0] * 60    
        self.y_ram = [0] * 60    
        plt.style.use("bmh")
        
        self.fig_cpu, self.ax_cpu = plt.subplots()
        self.canvas_cpu = FigureCanvas(self.fig_cpu)
        self.line_cpu, = self.ax_cpu.plot(self.x, self.y_cpu, 'r-')
        self.ax_cpu.set_title("Uso del CPU (%)")
        self.ax_cpu.set_xlabel("Tiempo (s)",color = "white")
        self.ax_cpu.set_ylabel("Porcenjate %",color = "white")
        self.ax_cpu.set_ylim(0, 100)
        
        self.fig_cpu.patch.set_facecolor('#1d1d1d')
        self.ax_cpu.set_facecolor('#1d1d1d')
        self.ax_cpu.title.set_color('white')     
        self.ax_cpu.tick_params(colors='white')     

        # (mantén lo demás igual)

        self.fig_ram, self.ax_ram = plt.subplots()
        self.canvas_ram = FigureCanvas(self.fig_ram)
        self.line_ram, = self.ax_ram.plot(self.x, self.y_ram, 'b-')
        self.ax_ram.set_title("Uso del RAM (%)")
        self.ax_ram.set_xlabel("Tiempo (s)",color = "white")
        self.ax_ram.set_ylabel("Porcenjate %",color = "white")
        self.ax_ram.set_ylim(0, 100)
        
        self.fig_ram.patch.set_facecolor('#1d1d1d')
        self.ax_ram.set_facecolor('#1d1d1d')
        self.ax_ram.title.set_color('white')     
        self.ax_ram.tick_params(colors='white')     
        # (mantén lo demás igual)
        # Añadir todos los cuadros al layout principal
        layout_info.addWidget(grupo1)
        layout_info.addWidget(grupo2)
        layout_info.addWidget(grupo3)
        layout_info.addWidget(grupo4)
        layout_info.addWidget(grupo5)
        layout_graficas_1 = QHBoxLayout()
        layout_graficas = QVBoxLayout()
        layout_graficas_2 = QVBoxLayout()
        layout_graficas_2.addLayout(layout_grafica_disco)
        layout_graficas_2.addWidget(grupo_info)
        layout_graficas_1.addLayout(layout_graficas)
        layout_graficas_1.addLayout(layout_graficas_2)
        layout_graficas.addWidget(self.canvas_cpu)
        layout_graficas.addWidget(self.canvas_ram)
        
        laymain.addLayout(lay1, 1)
        #laymain.addLayout(layout_info, 3)
        #laymain.addLayout(layout_graficas,5)
        laymain.addLayout(lay2, 2)
        laymain.addLayout(layout_graficas_1,20)
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
        self.cantidad_2_4g = 0
        self.cantidad_5g = 0
        self.wifi_5_6 = 0
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        self.tabla1 = QTableWidget(self)
        self.tabla1.setColumnCount(7)
        self.tabla1.setHorizontalHeaderLabels(["SSID","Intensidad de señal","Canal","Banda","Tipo de Seguridad","Direccion MAC","tipo Wi-Fi"])

        red1 = datos_variantes.wifi_datos_windows()
        self.tabla1.setRowCount(len(red1))
        for linea, red in enumerate(red1):
            self.tabla1.setItem(linea, 0, QTableWidgetItem(red.get("SSID", "Desconocido")))
            self.tabla1.setItem(linea, 1, QTableWidgetItem(str(red.get("Intensidad", "N/A"))))
            self.tabla1.setItem(linea, 2, QTableWidgetItem(red.get("Canal", "-")))
            self.tabla1.setItem(linea, 3, QTableWidgetItem(f"{red.get('Banda', '?')}GHz"))
            self.tabla1.setItem(linea, 4, QTableWidgetItem(red.get("Seguridad", "¿?")))
            self.tabla1.setItem(linea, 5, QTableWidgetItem(red.get("MAC", "¿?")))
            self.tabla1.setItem(linea, 6, QTableWidgetItem(red.get("Wi-fi", "¿?")))

            if str(red["Canal"]) == "5GHz":
                self.cantidad_5g +=1
            if str(red["Canal"]) == "2.4GHz":
                self.cantidad_2_4g += 1
            if str(red["Wi-fi"]) == "Wi-Fi 5" or "Wi-Fi 6":
                self.wifi_5_6 += 1
            
        self.figura, self.x1 = plt.subplots()
        self.canvas = FigureCanvas(self.figura)
        self.figura.patch.set_facecolor('black')
        self.x1.set_facecolor('black')           
        ssids = [red["SSID"] for red in red1]
        
        intensidades = [int(red.get("Intensidad", "0%").replace("%", "")) for red in red1]
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
        self.label1_1 = QLabel(f"Redes Detectadas: {len(red1)}")
        self.label1_2 = QLabel(f"Redes En 2.4GHz: {self.cantidad_2_4g}")
        self.label1_3 = QLabel(f"Redes En 5GHz: {self.cantidad_5g}")
        self.label1_4 = QLabel(f"Redes con Wifi 5/6: {self.wifi_5_6}")
        #label1_2 = QLabel("Sugerencias\t\t\t")
        lay.addWidget(self.label1_1)
        lay.addWidget(self.label1_2)
        lay.addWidget(self.label1_3)
        lay.addWidget(self.label1_4)
        #lay.addWidget(label1_2)
        label.setLayout(lay)
        self.tabla1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layoutH2.addWidget(self.canvas)
        layoutH2.addWidget(label)
        
        laymain = QVBoxLayout()
        laymain.addLayout(layoutH1,3)
        laymain.addLayout(layoutH2, 2)
        lay1.addLayout(laymain)
        return pagina
    
    def ancho_banda(self):
        pagina = QWidget()
        layout_principal = QVBoxLayout(pagina)

        titulo = QLabel("Monitoreo de Ancho de Banda")
        titulo.setFont(QFont("Arial", 20))
        layout_principal.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignCenter)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["IP", "MAC", "Velocidad de Bajada", "Velocidad de Subida", "Nombre", "Total Usado", "%Red"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout_principal.addWidget(self.tabla)

        boton = QPushButton("Actualizar")
        boton.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        boton.clicked.connect(self.actualizar_datos_ancho_banda)
        layout_principal.addWidget(boton)

        self.grafico = pg.PlotWidget(title="Uso de Red (%)")
        self.grafico.setBackground('k')
        self.grafico.showGrid(x=True, y=True)
        self.grafico.setYRange(0, 100)
        self.grafico.setXRange(0, 2)
        layout_principal.addWidget(self.grafico)
        return pagina
    def medir_ancho_banda(self, intervalo=1.0):
        net1 = psutil.net_io_counters()
        enviados_antes = net1.bytes_sent
        recibidos_antes = net1.bytes_recv
        import time
        time.sleep(intervalo)
        net2 = psutil.net_io_counters()
        enviados_despues = net2.bytes_sent
        recibidos_despues = net2.bytes_recv
        subida = (enviados_despues - enviados_antes) * 8 / intervalo / 1024  # kbps
        bajada = (recibidos_despues - recibidos_antes) * 8 / intervalo / 1024  # kbps
        return round(bajada, 2), round(subida, 2)
    def actualizar_datos_ancho_banda(self):
        bajada, subida = self.medir_ancho_banda()
        ip = socket.gethostbyname(socket.gethostname())
        nombre = socket.gethostname()
        self.tabla.setRowCount(1)
        self.tabla.setItem(0, 0, QTableWidgetItem(ip))
        self.tabla.setItem(0, 1, QTableWidgetItem("00:00:00:00:00:00"))
        self.tabla.setItem(0, 2, QTableWidgetItem(f"{bajada} kbps"))
        self.tabla.setItem(0, 3, QTableWidgetItem(f"{subida} kbps"))
        self.tabla.setItem(0, 4, QTableWidgetItem(nombre))
        self.tabla.setItem(0, 5, QTableWidgetItem(f"{bajada + subida:.2f} kbps"))
        self.tabla.setItem(0, 6, QTableWidgetItem("100%"))
        self.grafico.clear()
        self.grafico.plot([0, 1], [0, 100], pen=None, symbol='o', symbolBrush='g')
        self.grafico.setTitle("Uso de Red (%)", color='w')
        self.grafico.getAxis("bottom").setPen(pg.mkPen(color='w'))
        self.grafico.getAxis("left").setPen(pg.mkPen(color='w'))
        self.grafico.getAxis("left").setTextPen(pg.mkPen(color='w'))
        self.grafico.getAxis("bottom").setTextPen(pg.mkPen(color='w'))
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
        timer.start(1700)
    def actualizar_informacion(self):
        ##############Informacion
        self.label_info.setText(Datos.analizar_sistema()[0])
        self.label_info_1.setText(Datos.analizar_sistema()[1])
        self.label_info_2.setText(Datos.analizar_sistema()[2])
        ###########################################  Memoria Ram  #####################################################################
        self.ram_usada = round(Datos.Memoria_Ram().used / (1024 ** 3), 2)
        self.Ram_uso_label.setText(f"Usada: {self.ram_usada} GB")
        self.ram_u_2 = self.ram_usada
        #############################################  CPU  ###########################################################################
        self.Cpu_uso_label.setText(f"Uso actual: {Datos.CPU_porcentaje()}%")
        self.cpu_2 = Datos.CPU_porcentaje()
        #########################################  Bateria  ##########################################################################
        self.bateria_porcentaje_label.setText(f"Porcentaje: {Datos.Bateria()[0]}%")
        self.bateria_estado_label.setText("Cargando" if Datos.Bateria()[1] else "No Cargando")
        self.bateria_p_2 = Datos.Bateria()[0]
        #######################################  Conectividad  ########################################################################
        if datos_variantes.conectado():
            self.estado_internet.setText("Esta Conectado\na internet ✅")
            self.internet_estado_label.setText("Conectado a\nInternet ✅")
            self.internet_2 = "✅"
        else:
            self.estado_internet.setText("No esta Conectado\na internet ❌")
            self.internet_estado_label.setText("No esta Conectado\na Internet ❌")
            self.internet_2 = "❌"
        ###########################################  WiFI  ############################################################################
        red1 = datos_variantes.wifi_datos_windows()
        self.tabla1.setRowCount(len(red1))
        self.cantidad_2_4g = self.cantidad_5g = self.wifi_5_6 = 0
        for linea, red in enumerate(red1):
            self.tabla1.setItem(linea, 0, QTableWidgetItem(red.get("SSID", "Desconocido")))
            self.tabla1.setItem(linea, 1, QTableWidgetItem(str(red.get("Intensidad", "N/A"))))
            self.tabla1.setItem(linea, 2, QTableWidgetItem(red.get("Canal", "-")))
            self.tabla1.setItem(linea, 3, QTableWidgetItem(f"{red.get('Banda', '?')}GHz"))
            self.tabla1.setItem(linea, 4, QTableWidgetItem(red.get("Seguridad", "¿?")))
            self.tabla1.setItem(linea, 5, QTableWidgetItem(red.get("MAC", "¿?")))
            self.tabla1.setItem(linea, 6, QTableWidgetItem(red.get("Wi-fi", "¿?")))
            if red["Banda"] == "5":
                self.cantidad_5g +=1
            if red["Banda"] == "2.4":
                self.cantidad_2_4g += 1
            if red["Wi-fi"] in ["Wi-Fi 5", "Wi-Fi 6"]:
                self.wifi_5_6 += 1
                
        self.label1_2.setText(f"Redes En 2.4GHz: {self.cantidad_2_4g}")
        self.label1_3.setText(f"Redes En 5GHz: {self.cantidad_5g}")
        self.label1_4.setText(f"Redes con Wifi 5/6: {self.wifi_5_6}")
        
        self.x1.clear()
        
        self.figura.patch.set_facecolor('black')
        self.x1.set_facecolor('black') 
        
        ssids = [red["SSID"] for red in red1]
        intensidades = [int(red["Intensidad"].replace("%", "")) for red in red1]
        
        self.x1.barh(ssids, intensidades, color='white')
        
        self.x1.tick_params(axis='x', colors='white', labelsize = 10)
        self.x1.tick_params(axis='y', colors='white', labelsize = 10)
        
        self.figura.tight_layout()
        self.figura.canvas.draw()
        
        for i, v in enumerate(intensidades):
            self.x1.text(v + 1, i, f"{v}%", va='center', color='white')
        self.label1_1.setText(f"Redes Detectadas: {len(red1)}")
        ############################################################  Grafica CPU  ####################################################
        # Actualizar listas
        self.y_cpu = self.y_cpu[1:] + [Datos.CPU_porcentaje()]
        self.y_ram = self.y_ram[1:] + [Datos.Memoria_Ram().percent]

        # Actualizar gráfico CPU
        self.line_cpu.set_ydata(self.y_cpu)
        self.canvas_cpu.draw()

        # Actualizar gráfico RAM
        self.line_ram.set_ydata(self.y_ram)
        self.canvas_ram.draw()
        ###############################################################################################################################
        self.informacion.setText(f"CPU: {self.cpu_2}%    |     RAM: {self.ram_u_2}/{self.ram_t_2}     |     Disco :{self.disco_u_2}/{self.disco_t_2}     |     Bateria: {self.bateria_p_2}%     |     Internet: {self.internet_2}")
    def Comprobar_archivos(self):
        try:
            ruta_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Datos_Configuracion', 'Datos.json')
            with open(ruta_json, "r"):
                pass
        except FileNotFoundError:
            error_dialog = QErrorMessage(self)
            error_dialog.showMessage("¡Ocurrió un error! No se encontró el archivo.\nFalta el archivo Datos.json todavia no subido al git :3")
            error_dialog.exec()
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = OptiNet()
    sys.exit(app.exec())