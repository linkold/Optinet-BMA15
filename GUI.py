import sys
import os
import webbrowser
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QSizePolicy, QFrame)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt

estado = "bet1a"
class OptiNet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"OptiNet -- {estado}")
        self.setMinimumSize(1280,800)
        self.UI()
        self.show()
    def UI(self):
        menu = self.menuBar()
        menu.setStyleSheet("background-color: black;")
        
        menu_config = menu.addMenu("Cofiguracion")
        menu_ayuda = menu.addMenu("Ayuda")
        
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        menu_config.addAction(exit_action)
        
        ayuda_action = QAction("Soporte",self)
        ayuda_action.triggered.connect(self.soporte)
        menu_ayuda.addAction(ayuda_action)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        """barra principal"""
        
        barra_lat = QVBoxLayout()
        
        def Boton(text):
            boton = QPushButton(text)
            boton.setFont(QFont("",16))
            boton.setSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Preferred)
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
        
        for pagina in [self.pagina_principal, self.pagina_trafico, self.pagina_dispositivos,self.pagina_wifi,self.pagina_ancho_banda, self.pagina_reporte,self.pagina_left]:
            self.stack.addWidget(pagina)
        
        boton_principal.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_principal))
        boton_trafico.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_trafico))
        boton_dispositivos.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_dispositivos))
        boton_wifi.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_wifi))
        boton_ancho_banda.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_ancho_banda))
        boton_reporte.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_reporte))
        boton_left.clicked.connect(lambda: self.stack.setCurrentWidget(self.pagina_left))
        
        main_layout.addLayout(barra_lat,1)
        main_layout.addWidget(self.stack,6)
        
        
        self.setCentralWidget(main_widget)
        
    def soporte(self):
        """abrir pagina de ayuda"""
        pass 
    def trafico(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        label = QLabel("")
        lay1.addWidget(label)
        return pagina
    
    def dispositivos(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        label = QLabel("hola1")
        lay1.addWidget(label)
        return pagina
    def wifi(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        label = QLabel("hola2")
        lay1.addWidget(label)
        return pagina
    def ancho_banda(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        label = QLabel("hola3")
        lay1.addWidget(label)
        return pagina
    def reporte(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        label = QLabel("hola4")
        lay1.addWidget(label)
        return pagina
    def principal(self):
        pagina = QWidget()
        lay1 = QVBoxLayout(pagina)
        label = QLabel("hola5")
        lay1.addWidget(label)
        return pagina
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = OptiNet()
    sys.exit(app.exec())
