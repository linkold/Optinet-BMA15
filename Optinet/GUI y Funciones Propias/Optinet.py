import sys
from PyQt6.QtWidgets import (
    QDialog, QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QStackedWidget, QSizePolicy, QMessageBox,
    QLineEdit
)
from PyQt6.QtGui import QFont,QAction
from PyQt6.QtCore import Qt
import os
import ctypes
import platform
import paramiko

## funciones propias
from Sistema_Operativo_Condicional import Datos, datos_variantes
from Trafico_Informacion import SnifferWidget
from Ancho_Banda import TablaMonitor
from Principal_Informacion import PaginaPrincipal
from Wifi import WifiWidget
from Control_Parental import ControlParentalWidget
from IPS import IPSWidget
from Seguridad import SeguridadWidget
from Reportes import ReportesWidget

rasp_datos = []

class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(300, 300)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.ip_rasp = QLineEdit("192.168.10.10")
        self.user_rasp = QLineEdit("optinet")
        self.password_rasp = QLineEdit("12345678")
        self.password_rasp.setEchoMode(QLineEdit.EchoMode.Password)

        login_button = QPushButton("Iniciar sesión")
        login_button.clicked.connect(self.check_login)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Usuario:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Contraseña:"))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("IP Raspberry"))
        layout.addWidget(self.ip_rasp)
        layout.addWidget(QLabel("Usuario Raspberry"))
        layout.addWidget(self.user_rasp)
        layout.addWidget(QLabel("Contraseña Raspberry"))
        layout.addWidget(self.password_rasp)
        layout.addWidget(login_button)

        self.setLayout(layout)
        self.login_successful = False

    def check_rasp(self):
        global rasp_datos
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ip = self.ip_rasp.text()
        user = self.user_rasp.text()
        password = self.password_rasp.text()
        try:
            ssh.connect(hostname=ip, username=user, password=password, port=22, timeout=5)
            ssh.close()
            rasp_datos = [ip, user, password]
            return True
        except paramiko.AuthenticationException:
            QMessageBox.warning(self, "Error", "Autenticación fallida. Vuelve a intentarlo.")
        except paramiko.SSHException as e:
            QMessageBox.warning(self, "Error", f"Error SSH: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error: {e}")
        return False

    def check_login(self):
        usuario = self.username_input.text()
        clave = self.password_input.text()
        if usuario == "optinet" and clave == "12345678":
            if self.check_rasp():
                self.login_successful = True
                self.accept()
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")

class OptiNet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OptiNet")
        self.setMinimumSize(800, 500)
        self.ui()
        self.show()
        self.comprobar()

    def ui(self):
        def crear_boton(texto, callback=None):
            btn = QPushButton(texto)
            btn.setFont(QFont("", 14))
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            if callback:
                btn.clicked.connect(callback)
            return btn

        def crear_menu(menu_bar, titulo, acciones):
            menu = menu_bar.addMenu(titulo)
            for nombre, funcion in acciones:
                act = QAction(nombre, menu_bar.parent())
                act.triggered.connect(funcion)
                menu.addAction(act)

        menu = self.menuBar()
        crear_menu(menu, "Configuración", [("Salir", self.close)])
        crear_menu(menu, "Ayuda", [("Soporte", self.soporte)])

        self.estado_internet = QLabel("Esta Conectado\na Internet" if datos_variantes.conectado() else "No está Conectado\na Internet")
        self.estado_internet.setFont(QFont("Arial", 14))

        botones = [
            ("Inicio", lambda: self.stack.setCurrentWidget(self.pagina_principal)),
            ("Trafico en Tiempo Real", lambda: self.stack.setCurrentWidget(self.pagina_trafico)),
            ("Wi-Fi", lambda: self.stack.setCurrentWidget(self.pagina_wifi)) if Datos.adaptador() else None,
            ("Ancho de Banda y Dispositivos", lambda: self.stack.setCurrentWidget(self.pagina_ancho_banda)),
            ("Reportes", lambda: self.stack.setCurrentWidget(self.pagina_reportes)),
            ("Control Parental", lambda: self.stack.setCurrentWidget(self.pagina_control_parental)),
            ("Seguridad", lambda: self.stack.setCurrentWidget(self.pagina_seguridad)),
            ("Monitoreo IDS/IPS", lambda: self.stack.setCurrentWidget(self.pagina_ips))
        ]

        barra_lat = QVBoxLayout()
        for item in botones:
            if item:
                barra_lat.addWidget(crear_boton(*item))
        barra_lat.addWidget(self.estado_internet)
        barra_lat.setAlignment(self.estado_internet, Qt.AlignmentFlag.AlignCenter)

        self.stack = QStackedWidget()
        self.pagina_principal = PaginaPrincipal()
        self.pagina_trafico = SnifferWidget()
        self.pagina_wifi = WifiWidget() if Datos.adaptador() else QWidget()
        self.pagina_ancho_banda = TablaMonitor()
        self.pagina_reportes = ReportesWidget()
        self.pagina_seguridad = SeguridadWidget()
        self.pagina_control_parental = ControlParentalWidget(ip=rasp_datos[0], user=rasp_datos[1], password=rasp_datos[2])
        self.pagina_ips = IPSWidget()

        for pagina in [
            self.pagina_principal, self.pagina_trafico, self.pagina_wifi,
            self.pagina_ancho_banda, self.pagina_reportes, self.pagina_seguridad,
            self.pagina_control_parental, self.pagina_ips
        ]:
            self.stack.addWidget(pagina)

        main_layout = QHBoxLayout()
        main_layout.addLayout(barra_lat, 1)
        main_layout.addWidget(self.stack, 6)

        contenedor = QWidget()
        contenedor.setLayout(main_layout)
        self.setCentralWidget(contenedor)

    def soporte(self):
        return QWidget()

    def comprobar(self):
        try:
            ruta_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Datos', 'Datos.json')
            with open(ruta_json, "r"):
                pass
        except FileNotFoundError:
            QMessageBox.critical(self, "Error Crítico", "No se encontró el archivo Datos.json", QMessageBox.StandardButton.Close)
            self.close()

        if not Datos.adaptador():
            QMessageBox.warning(self, "Advertencia", "No posee adaptador WiFi", QMessageBox.StandardButton.Ok)
        if Datos.admin() == 0:
            QMessageBox.critical(self, "Error", "No se abrió con permisos de administrador", QMessageBox.StandardButton.Close)
            self.close()

def asegurar_admin():
    if platform.system() == "Windows":
        if not Datos.admin():
            script = os.path.abspath(sys.argv[0])
            params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 1
            )
            sys.exit()
    else:
        if os.geteuid() != 0:
            os.execvp("sudo", ["sudo", "python3"] + sys.argv)

if __name__ == "__main__":
    asegurar_admin()
    app = QApplication(sys.argv)
    if Login().exec():
        ventana = OptiNet()
        sys.exit(app.exec())
