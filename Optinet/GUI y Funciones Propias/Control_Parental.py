from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QMessageBox, QSizePolicy
)
from PyQt6.QtGui import QFont
from Sistema_Operativo_Condicional import Control_Parental
import paramiko

class ControlParentalWidget(QWidget):
    def __init__(self,ip,user,password, parent=None):
        super().__init__(parent)
        self.ip = ip
        self.user = user
        self.password = password
        self.control = Control_Parental()
        self.init_ui()

    def init_ui(self):
        layout_main = QVBoxLayout(self)

        titulo = QLabel("Control Parental")
        titulo.setFont(QFont("Arial", 20))
        layout_main.addWidget(titulo, 1)

        self.lista = QListWidget()
        layout_main.addWidget(self.lista, 9)

        # Sección de entrada y botones
        input_layout = QHBoxLayout()
        label_input = QLabel("Agregar sitio Web")
        self.input_web = QLineEdit()
        input_layout.addWidget(label_input)
        input_layout.addWidget(self.input_web)
        layout_main.addLayout(input_layout, 2)

        button_layout = QHBoxLayout()
        boton_agregar = QPushButton("Agregar")
        boton_eliminar = QPushButton("Eliminar")

        boton_agregar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        boton_eliminar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        button_layout.addWidget(boton_agregar)
        button_layout.addWidget(boton_eliminar)
        layout_main.addLayout(button_layout, 1)

        # Conectar botones
        boton_agregar.clicked.connect(self.agregar_sitio)
        boton_eliminar.clicked.connect(self.eliminar_sitio)

    def agregar_sitio(self):
        web = self.input_web.text().strip()
        if web:
            self.lista.addItem(web)
            self.control.agregar_blacklist(web)
            consola = paramiko.SSHClient()
            consola.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            consola.connect(self.ip,username=self.user,password=self.password)
            _, stdout, _ = consola.exec_command(f"sudo pihole deny {web} --regex")
            if "[✓] Added 1 domain(s):" in stdout.read().decode():
                QMessageBox.information(self, "Éxito", "Sitio bloqueado correctamente.")
            else:
                QMessageBox.information(self, "Error", "Vuelva a intentarlo o verifique que\tel dominio ya este en la lista")
            self.input_web.clear()
            consola.close()
        else:
            QMessageBox.warning(self, "Advertencia", "Ingrese un sitio válido.")

    def eliminar_sitio(self):
        elementos = self.lista.selectedItems()
        if elementos:
            for item in elementos:
                web = item.text()
                self.lista.takeItem(self.lista.row(item))
                consola = paramiko.SSHClient()
                consola.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                consola.connect(self.ip,username=self.user,password=self.password)
                _, stdout, _ = consola.exec_command(f"sudo pihole --regex -d facebook.com")
                if "[✓] Domain(s) removed from" in stdout.read().decode() or "[✓] Requested domain(s)" in stdout.read().decode():
                    QMessageBox.information(self, "Éxito", "Sitio desbloqueado correctamente.")
                    self.input_web.clear()
                    consola.close() 
                    self.control.quitar_blacklist(web)
                else:
                    QMessageBox.information(self, "Error", "Vuelva a intentarlo")
                    
