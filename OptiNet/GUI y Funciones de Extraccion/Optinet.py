import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,QHBoxLayout, QLabel, QStackedWidget, QSizePolicy, QTableWidget,QTableWidgetItem, QHeaderView, QMessageBox,QGroupBox,QPlainTextEdit,QListWidget,QLineEdit,QErrorMessage)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
import psutil
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
## funciones propias
from Cond import Datos, Control_Parental, datos_variantes
from Trafico import SnifferWidget
from IDS import RedMonitorWidget
import ctypes
import platform

class OptiNet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OptiNet")
        self.setMinimumSize(640, 400)
        
        self.ui()
        self.show()
        self.comprobar()

        self.actualizador()
    def ui(self):
        menu = self.menuBar()
        menu.setStyleSheet("background-color:white;")

        menu_ayuda = menu.addMenu("Ayuda")
        menu_config = menu.addMenu("Configuracion")

        
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
            self.estado_internet.setText("Esta Conectado\na internet")
        else:
            self.estado_internet.setText("No esta Conectado\na internet")
        
        boton_principal = Boton("Inicio")
        boton_trafico = Boton("Trafico en Tiempo Real")
        boton_dispositivos = Boton("Dispositivos")
        boton_wifi = Boton("Wi-Fi")
        boton_ancho_banda = Boton("Ancho de Banda")
        boton_reporte = Boton("Reportes")
        boton_control_parental = Boton("Control Parental")
        boton_seguridad = Boton("Seguridad")
        
        barra_lat.addWidget(boton_principal)
        barra_lat.addWidget(boton_trafico)
        barra_lat.addWidget(boton_dispositivos)
        if Datos.adaptador():
            barra_lat.addWidget(boton_wifi)
        barra_lat.addWidget(boton_ancho_banda)
        barra_lat.addWidget(boton_reporte)
        barra_lat.addWidget(boton_control_parental)
        barra_lat.addWidget(boton_seguridad)
        barra_lat.addWidget(self.estado_internet)
        barra_lat.setAlignment(self.estado_internet,Qt.AlignmentFlag.AlignCenter)
        self.stack = QStackedWidget()
        self.pagina_principal = self.principal()
        self.pagina_trafico = self.trafico()
        self.pagina_dispositivos = self.dispositivos()
        if Datos.adaptador():
            self.pagina_wifi = self.wifi()
        else:
            self.pagina_wifi = QWidget()
        self.pagina_ancho_banda = self.ancho_banda()
        self.pagina_reporte = self.reporte()
        self.pagina_control_parental = self.control_parental()
        self.pagina_segurirad = self.seguridad()
        for pagina in [self.pagina_principal, self.pagina_trafico, self.pagina_dispositivos, self.pagina_wifi, self.pagina_ancho_banda, self.pagina_reporte, self.pagina_control_parental,self.pagina_segurirad]:
            self.stack.addWidget(pagina)
        
        boton_principal.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_principal))
        boton_trafico.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_trafico))
        boton_dispositivos.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_dispositivos))
        if Datos.adaptador():
            boton_wifi.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_wifi))
        boton_ancho_banda.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_ancho_banda))
        boton_reporte.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_reporte))
        boton_control_parental.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_control_parental))
        boton_seguridad.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_segurirad))
        
        main_layout.addLayout(barra_lat, 1)
        main_layout.addWidget(self.stack, 6)
        
        self.setCentralWidget(main_widget)
    def principal(self):
        pagina = QWidget()
        laymain = QVBoxLayout(pagina)
        lay1 = QVBoxLayout()
        # Título
        label_titulo1 = QLabel("Bienvenido a Optinet")
        label_titulo1.setFont(QFont("Arial", 25))
        lay1.addWidget(label_titulo1)
        lay1.setAlignment(label_titulo1, Qt.AlignmentFlag.AlignCenter)
        # --- RAM ---
        self.ram_t_2 = round(Datos.Memoria_Ram().total / (1024 ** 3), 2)
        self.ram_u_2 = round(Datos.Memoria_Ram().used / (1024 ** 3), 2)
        # --- CPU ---
        self.cpu_2 = Datos.CPU_porcentaje()
        # --- Disco ---
        disco_total = disco_usado = 0
        for part in psutil.disk_partitions():
            try:
                disco_total += psutil.disk_usage(part.mountpoint).total
                disco_usado += psutil.disk_usage(part.mountpoint).used
            except Exception:
                pass
        self.disco_u_2 = round(disco_total / (1024 ** 3), 2)
        self.disco_t_2 = round(disco_usado / (1024 ** 3), 2)
        if Datos.Bateria():
            self.bateria_p_2 = Datos.Bateria()[0]
        else:
            self.bateria_p_2 = None
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
        ax.pie(sizes,labels=labels,autopct=lambda p: f'{p:.1f}%',startangle=90,colors=colors,explode=explode,textprops={'color': 'white'})
        ax.set_title("Uso de Almacenamiento por Partición", color='white')
        fig.patch.set_facecolor('#1d1d1d')
        ax.set_facecolor('#1d1d1d')
        layout_grafica_disco.addWidget(canvas)

        #Principal 2

        info_general = f"CPU: {self.cpu_2} | RAM: {self.ram_u_2}/{self.ram_t_2} | Disco :{self.disco_u_2}/{self.disco_t_2}"
        if Datos.Bateria():
            info_general += f"  | Bateria: {self.bateria_p_2}"

        lay2 = QHBoxLayout()
        self.informacion = QLabel(info_general)
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
        self.ax_cpu.set_ylabel("Porcenjate %",color = "white")
        self.ax_cpu.set_ylim(0, 100)
        
        self.fig_cpu.patch.set_facecolor('#1d1d1d')
        self.ax_cpu.set_facecolor('#1d1d1d')
        self.ax_cpu.title.set_color('white')     
        self.ax_cpu.tick_params(colors='white')     

        self.fig_ram, self.ax_ram = plt.subplots()
        self.canvas_ram = FigureCanvas(self.fig_ram)
        self.line_ram, = self.ax_ram.plot(self.x, self.y_ram, 'b-')
        self.ax_ram.set_title("Uso del RAM (%)")
        self.ax_ram.set_ylabel("Porcenjate %",color = "white")
        self.ax_ram.set_ylim(0, 100)
        
        self.fig_ram.patch.set_facecolor('#1d1d1d')
        self.ax_ram.set_facecolor('#1d1d1d')
        self.ax_ram.title.set_color('white')     
        self.ax_ram.tick_params(colors='white')     

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
        laymain.addLayout(lay2, 2)
        laymain.addLayout(layout_graficas_1,20)
        return pagina
    def trafico(self):
        return SnifferWidget()
    def dispositivos(self):
        pagina = QWidget()
        return pagina
    def seguridad(self):
        return RedMonitorWidget()

    def wifi(self):
        self.cantidad_2_4g = 0
        self.cantidad_5g = 0
        self.wifi_5_6 = 0
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        self.tabla1 = QTableWidget(self)
        self.tabla1.setColumnCount(7)
        self.tabla1.setHorizontalHeaderLabels(["SSID","Intensidad de señal","Canal","Banda","Tipo de Seguridad","Direccion MAC","tipo Wi-Fi"])

        red1 = datos_variantes.wifi_datos()
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
        lay.addWidget(self.label1_1)
        lay.addWidget(self.label1_2)
        lay.addWidget(self.label1_3)
        lay.addWidget(self.label1_4)
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
        return pagina
    def reporte(self):
        pagina = QWidget()
        return pagina
    def control_parental(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        titulo = QLabel("Control Parental")
        lay3 = QHBoxLayout()
        
        self.lista = QListWidget()
        label1_2 = QLabel("Agregar sitio Web")
        web_bloqueo = QLineEdit()
        control = Control_Parental()
        
        def agregar(web):
            if web.strip() != "":
                self.lista.addItem(web)
                control.agregar_blacklist(web)
                QMessageBox.information(self, "Éxito", "Sitio bloqueado correctamente.")
            else:
                QMessageBox.warning(self, "Advertencia", "Ingrese un sitio válido.")
        
        def eliminar():
            elementos = self.lista.selectedItems()
            if elementos:
                for item in elementos:
                    web = item.text()
                    self.lista.takeItem(self.lista.row(item))
                    control.quitar_blacklist(web)
                QMessageBox.information(self, "Éxito", "Sitio(s) desbloqueado(s) correctamente.")
        
        lay2 = QHBoxLayout()
        boton_Agregar = QPushButton("Agregar")
        boton_Eliminar = QPushButton("Eliminar")
        boton_Agregar.clicked.connect(lambda: agregar(web_bloqueo.text()))
        boton_Eliminar.clicked.connect(eliminar)
        
        lay3.addWidget(boton_Agregar)
        lay3.addWidget(boton_Eliminar)
        boton_Agregar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        boton_Eliminar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        lay2.addWidget(label1_2)
        lay2.addWidget(web_bloqueo)
        titulo.setFont(QFont("Arial", 20))
        
        lay1.addWidget(titulo, 1)
        lay1.addWidget(self.lista, 9)
        lay1.addLayout(lay2, 2)
        lay1.addLayout(lay3, 1)
        
        return pagina

    def soporte(self):
        pagina = QWidget()
        return pagina
    def comprobar(self):
        try:
            ruta_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Datos_Configuracion', 'Datos.json')
            with open(ruta_json, "r"):
                pass
        except FileNotFoundError:
            QMessageBox.critical(self,"Error Critico","¡Ocurrió un error! No se encontró el archivo.",QMessageBox.StandardButton.Close)
            self.close()
        if Datos.adaptador():
            pass
        else:
            QMessageBox.warning(self,"Advertencia","No posee adaptador wifi",QMessageBox.StandardButton.Ok)
        if Datos.admin() == 0:
            QMessageBox.critical(self,"Error","No se abrio con permisos",QMessageBox.StandardButton.Close)
            self.close()
            
    def actualizador(self):
        pass
def asegurar_admin():
    if platform.system() == "Windows":
        if not Datos.admin():
            # Relanzar el script como administrador
            script = os.path.abspath(sys.argv[0])
            params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 1
            )
            sys.exit()
    else:
        if os.geteuid() != 0:
            print("Este script necesita permisos de administrador. Reintentando con sudo...")
            try:
                os.execvp("sudo", ["sudo"] + ["python3"] + sys.argv)
            except Exception as e:
                print("Error al intentar ejecutar con sudo:", e)
                sys.exit(1)

if __name__ == '__main__':
    asegurar_admin()
    app = QApplication(sys.argv)
    ventana = OptiNet()
    sys.exit(app.exec())

Datos.Memoria_Ram().total / (1024 ** 3), 2