import sys
import json
import psutil
import subprocess
import pyqtgraph as pg
import platform
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import socket
import os
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

prompt = "about the beatles"
output = generator(prompt, max_length=50, num_return_sequences=1)

print(output[0]["generated_text"])


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

    def adaptador():
        try:
            salida = subprocess.check_output("nmcli device status", shell=True).decode("utf-8", errors="ignore")
            for linea in salida.splitlines():
                if "conectado" in linea.lower() or "connected" in linea.lower():
                    if "ethernet" in linea.lower():
                        return False  
                    elif "wifi" in linea.lower():
                        return True   
            return None  
        except Exception as e:
            print("Error:", e)
            return None
    def admin():
        return os.geteuid() == 0 
    
from urllib.parse import urlparse

class Control_Parental:
    def limpiar_url(self, url):
        pass
    def agregar_blacklist(self, web_url):
        pass
    def quitar_blacklist(self, web_url):
        pass

class datos_variantes:
    def conectado():
        try:
            salida = subprocess.run(["ping", "-c", "1", "google.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
            return salida.returncode == 0
        except Exception:
            return False
        
    def wifi_datos():
        import subprocess, json, os

        ruta_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Datos_Configuracion', 'Datos.json')
        with open(ruta_json, "r") as file:
            datos_wifi = json.load(file)

        try:
            salida = subprocess.check_output(
                "nmcli -t -f SSID,BSSID,SIGNAL,FREQ,CHAN,SECURITY,DEVICE dev wifi list",
                shell=True
            ).decode("utf-8", errors="ignore")
        except Exception as e:
            print("Error al ejecutar nmcli:", e)
            return []

        lineas = salida.strip().split('\n')
        lista = []

        for linea in lineas:
            if not linea.strip():
                continue

            # Primer split para separar el SSID
            ssid_split = linea.strip().split(":", 1)
            if len(ssid_split) != 2:
                continue

            ssid = ssid_split[0] if ssid_split[0] else "Red Oculta"
            resto = ssid_split[1]

        # El resto contiene: BSSID:SIGNAL:FREQ:CHAN:SECURITY:DEVICE
        # Pero BSSID tiene 5 ":" → usar rsplit desde la derecha
            partes_restantes = resto.rsplit(":", 6)
            if len(partes_restantes) != 7:
                continue

            bssid ,bssid1, signal, frecuencia ,canal, seguridad, dispositivo = partes_restantes
            try:
                canal_mapeado = datos_wifi["canales_rango_2.4G"].get(canal,
                                  datos_wifi["canales_rango_5G"].get(canal, canal))
            except:
                canal_mapeado = canal
            bssid_f = bssid + ":" + bssid1
            red = {
            "SSID": ssid,
            "MAC": bssid_f.replace(r"\:",":"),
            "Intensidad": signal + "%",
            "Canal": canal_mapeado,
            "Seguridad": seguridad,
            "Banda": "2.4G" if canal_mapeado in datos_wifi["canales_rango_2.4G"] else "5G",
            "Wi-fi": datos_wifi["radio_tipos"].get("???", "Desconocido")  # opcional si no disponible
            }

            lista.append(red)
        return lista

#print(datos_variantes.wifi_datos()
datos_variantes.wifi_datos()
print(datos_variantes.conectado())