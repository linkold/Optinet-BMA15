from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import psutil
from Sistema_Operativo_Condicional import Datos


class PaginaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.x = list(range(60))
        self.y_cpu = [0] * 60
        self.y_ram = [0] * 60
        self.counter = 0  # contador para actualizar gráfico de disco
        self.init_ui()

    def init_ui(self):
        laymain = QVBoxLayout(self)
        lay1 = QVBoxLayout()

        label_titulo1 = QLabel("Bienvenido a Optinet")
        label_titulo1.setFont(QFont("Arial", 25))
        lay1.addWidget(label_titulo1)
        lay1.setAlignment(label_titulo1, Qt.AlignmentFlag.AlignCenter)

        # ----- GRÁFICA CPU -----
        self.fig_cpu, self.ax_cpu = plt.subplots()
        self.canvas_cpu = FigureCanvas(self.fig_cpu)
        self.line_cpu, = self.ax_cpu.plot(self.x, self.y_cpu, 'r-')
        self.ax_cpu.set_title("Uso del CPU (%)")
        self.ax_cpu.set_ylim(0, 100)
        self.fig_cpu.patch.set_facecolor('#1d1d1d')
        self.ax_cpu.set_facecolor('#1d1d1d')
        self.ax_cpu.title.set_color('white')
        self.ax_cpu.tick_params(colors='white')

        # ----- GRÁFICA RAM -----
        self.fig_ram, self.ax_ram = plt.subplots()
        self.canvas_ram = FigureCanvas(self.fig_ram)
        self.line_ram, = self.ax_ram.plot(self.x, self.y_ram, 'b-')
        self.ax_ram.set_title("Uso del RAM (%)")
        self.ax_ram.set_ylim(0, 100)
        self.fig_ram.patch.set_facecolor('#1d1d1d')
        self.ax_ram.set_facecolor('#1d1d1d')
        self.ax_ram.title.set_color('white')
        self.ax_ram.tick_params(colors='white')

        # ----- GRÁFICA DISCO -----
        self.fig_disco, self.ax_disco = plt.subplots()
        self.canvas_disco = FigureCanvas(self.fig_disco)
        self.actualizar_grafica_disco()

        # ----- INFO GENERAL -----
        self.label_info = QLabel()
        self.label_info.setFont(QFont("Arial", 14))
        lay2 = QHBoxLayout()
        lay2.addWidget(self.label_info)
        lay2.setAlignment(self.label_info, Qt.AlignmentFlag.AlignHCenter)

        # ----- INFO DETALLADA -----
        self.grupo_info = QGroupBox()
        self.layout_grupo = QVBoxLayout(self.grupo_info)
        self.label_titulos = []
        self.label_datos = []
        titulos = ["Información", "Estado", "Recomendaciones"]
        for i in range(3):
            t = QLabel(titulos[i] + ":")
            t.setFont(QFont("Arial", 14))
            d = QLabel("-")
            d.setFont(QFont("Arial", 10))
            self.layout_grupo.addWidget(t)
            self.layout_grupo.addWidget(d)
            self.label_titulos.append(t)
            self.label_datos.append(d)

        # ------- LAYOUT DE GRÁFICAS -------
        layout_graficas = QVBoxLayout()
        layout_graficas.addWidget(self.canvas_cpu)
        layout_graficas.addWidget(self.canvas_ram)

        lay_21 = QVBoxLayout()
        lay_21.addWidget(self.canvas_disco)
        lay_21.addWidget(self.grupo_info)

        layout_final = QHBoxLayout()
        layout_final.addLayout(layout_graficas)
        layout_final.addLayout(lay_21)

        laymain.addLayout(lay1)
        laymain.addLayout(lay2)
        laymain.addLayout(layout_final)

        # ------- TIMER PARA ACTUALIZACIÓN -------
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_datos)
        self.timer.start(1000)

        self.actualizar_datos()  # Primera actualización manual

    def actualizar_grafica_disco(self):
        self.ax_disco.clear()
        labels, sizes, colors, explode = [], [], [], []
        for part in psutil.disk_partitions():
            try:
                uso = psutil.disk_usage(part.mountpoint)
                usado = uso.used / (1024 ** 3)
                libre = uso.free / (1024 ** 3)
                if usado > 1:
                    labels.extend([f"{part.device} Usado", f"{part.device} Libre"])
                    sizes.extend([usado, libre])
                    colors.extend(['#ff6666', '#66cc66'])
                    explode.extend([0.05, 0])
            except:
                continue

        self.ax_disco.pie(sizes, labels=labels, autopct=lambda p: f'{p:.1f}%', startangle=90,
                          colors=colors, explode=explode, textprops={'color': 'white'})
        self.ax_disco.set_title("Uso de Almacenamiento por Partición", color='white')
        self.fig_disco.patch.set_facecolor('#1d1d1d')
        self.ax_disco.set_facecolor('#1d1d1d')
        self.canvas_disco.draw()

    def actualizar_datos(self):
        # Actualizar gráficas CPU y RAM
        self.y_cpu = self.y_cpu[1:] + [psutil.cpu_percent()]
        self.y_ram = self.y_ram[1:] + [psutil.virtual_memory().percent]
        self.line_cpu.set_ydata(self.y_cpu)
        self.line_ram.set_ydata(self.y_ram)
        self.canvas_cpu.draw()
        self.canvas_ram.draw()

        # Actualizar gráfica de disco cada 10 segundos
        if self.counter % 10 == 0:
            self.actualizar_grafica_disco()
        self.counter += 1

        # Actualizar info general
        ram = Datos.Memoria_Ram()
        ram_t = round(ram.total / (1024 ** 3), 2)
        ram_u = round(ram.used / (1024 ** 3), 2)
        cpu = Datos.CPU_porcentaje()

        disco_total = disco_usado = 0
        for part in psutil.disk_partitions():
            try:
                uso = psutil.disk_usage(part.mountpoint)
                disco_total += uso.total
                disco_usado += uso.used
            except:
                continue
        disco_t = round(disco_total / (1024 ** 3), 2)
        disco_u = round(disco_usado / (1024 ** 3), 2)

        bateria_info = Datos.Bateria()
        bateria = bateria_info[0] if bateria_info else None
        texto = f"CPU: {cpu}% | RAM: {ram_u}/{ram_t} GB | Disco: {disco_u}/{disco_t} GB"
        if bateria:
            texto += f" | Batería: {bateria}"

        if self.label_info.text() != texto:
            self.label_info.setText(texto)

        # Actualizar tabla informativa
        datos = Datos.analizar_sistema()
        for i in range(3):
            self.label_datos[i].setText(datos[i])
