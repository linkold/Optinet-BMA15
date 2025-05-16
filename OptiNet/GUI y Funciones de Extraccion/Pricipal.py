import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QLabel, QStackedWidget, QSizePolicy, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QMessageBox,QGroupBox,QPlainTextEdit,QListWidget,QLineEdit,QErrorMessage)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
import json
#import platform
#import netifaces
import psutil
import subprocess
#from scapy.all import ARP, Ether, srp, get_if_list, get_if_addr
import pyqtgraph as pg
import platform

import pywifi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


import socket
import os

class Datos:
    def Memoria_Ram():
        mem = psutil.virtual_memory()
        return mem
    def CPU_porcentaje():
        cpu = psutil.cpu_percent(interval=0.1)
        return cpu
    def CPU_Nucleos():
        cpu = psutil.cpu_count(logical=True)
        return cpu
    def Bateria():
        if psutil.sensors_battery() is None:
            return False
        else:
            datos_bat = [psutil.sensors_battery().percent,psutil.sensors_battery().power_plugged]
            return datos_bat
    def analizar_sistema():
        diagnostico_total = []

        # Información del sistema
        cpu_logicos = psutil.cpu_count(logical=True)
        cpu_fisicos = psutil.cpu_count(logical=False)
        cpu_freq = psutil.cpu_freq()
        ram = psutil.virtual_memory()
        disco = psutil.disk_usage('/')
        diagnostico_1 = ""
        diagnostico_1 += f"Sistema: {platform.system()} {platform.release()}\n"
        diagnostico_1 += f"CPU: {cpu_logicos} núcleos lógicos ({cpu_fisicos} físicos)\n"
        diagnostico_1 += f"Frecuencia CPU: {cpu_freq.current:.2f} MHz\n"
        diagnostico_1 += f"RAM Total: {ram.total / (1024**3):.2f} GB\n"
        diagnostico_1 += f"Disco Total: {disco.total / (1024**3):.2f} GB"
        
        diagnostico_total.append(diagnostico_1)
        diagnostico_1 = ""
        # Estado CPU
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage < 50:
            estado_cpu = "Normal"
        elif cpu_usage < 85:
            estado_cpu = "Alto"
        else:
            estado_cpu = "Crítico"
        diagnostico_1 += f"CPU: {cpu_usage:.1f}% de uso - Estado: {estado_cpu}\n"

        # Estado RAM
        ram_percent = ram.percent
        if ram_percent < 50:
            estado_ram = "Normal"
        elif ram_percent < 85:
            estado_ram = "Alto"
        else:
            estado_ram = "Crítico"
        diagnostico_1 += f"RAM: {ram_percent:.1f}% de uso - Estado: {estado_ram}\n"

        # Estado Disco
        disco_percent = disco.percent
        if disco_percent < 70:
            estado_disco = "Normal"
        elif disco_percent < 90:
            estado_disco = "Alto"
        else:
            estado_disco = "Crítico"
        diagnostico_1 += f"Disco: {disco_percent:.1f}% de uso - Estado: {estado_disco}\n"

        diagnostico_total.append(diagnostico_1)
        diagnostico_1 = ""
        # Recomendaciones

        if cpu_usage > 85:
            diagnostico_1 += "- CPU sobrecargada. Cierra procesos pesados o revisa el uso.\n"
        if ram_percent > 85:
            diagnostico_1 += "- RAM casi llena. Considera cerrar aplicaciones o ampliar memoria.\n"
        if disco_percent > 90:
            diagnostico_1 += "- Disco casi lleno. Libera espacio para evitar errores.\n"
        if cpu_usage <= 85 and ram_percent <= 85 and disco_percent <= 90:
            diagnostico_1 += "- Todo está dentro de los parámetros normales.\n"
        diagnostico_total.append(diagnostico_1)
        
        return diagnostico_total


print(Datos.analizar_sistema()[0])
print(Datos.analizar_sistema()[1])
print(Datos.analizar_sistema()[2])
class datos_variantes:
    
    def conectado():
        try:
            salida = subprocess.run(["ping", "-n", "1", "google.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
            return salida.returncode == 0
        except Exception:
            return False  
        
    def wifi_datos_windows():
        ruta_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Datos_Configuracion', 'Datos.json')
        with open(ruta_json, "r") as file:
            datos_wifi = json.load(file)
        resultado = subprocess.check_output("netsh wlan show networks mode=bssid", shell=True).decode("utf-8",errors="ignore")
        lineas_1 = resultado.split("\n")
        lista = []
        red = {}
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        iface.scan()
        for linea in lineas_1:
            if "SSID" in linea and "BSSID" not in linea:
                if red:
                    lista.append(red)
                    red = {}
                if linea.split(":",1)[1].strip() == "":
                    red["SSID"] = "Red Oculta"
                else:
                    red["SSID"] = linea.split(":",1)[1].strip()
            elif "Signal" in linea or "Intensidad de la señal" in linea:
                red["Intensidad"] = linea.split(":",1)[1].strip()
            elif "Channel       " in linea or "Canal        " in linea:
                try:
                    red["Canal"] = datos_wifi["canales_rango_2.4G"][linea.split(":",1)[1].split()[0]]
                except:
                    try:
                        red["Canal"] = datos_wifi["canales_rango_5G"][str(linea.split(":",1)[1].split()[0])]
                    except:
                        red["Canal"] = str(linea.split(":",1)[1].split()[0])
            elif "Band" in linea or "Banda" in linea:
                red["Banda"] = str(linea.split(":",1)[1].split()[0])
            elif "Authentication" in linea or "Autenticación" in linea:
                red["Seguridad"] = linea.split(":",1)[1].split()[0]
            elif "BSSID 1" in linea:
                red["MAC"] = linea.split(":",1)[1].split()[0]
            elif "Radio type" in linea or "Tipo de radio" in linea:
                try:
                    red['Wi-fi'] = datos_wifi["radio_tipos"][linea.split(":",1)[1].split()[0]]
                except Exception:
                    red["Wi-fi"] = "Error"
        if red:
            lista.append(red)
        return lista
        

    def wifi_datos_linux(self):
        """Integracion con linux 
        el codigo previo solo sirve para windows"""
        pass
        