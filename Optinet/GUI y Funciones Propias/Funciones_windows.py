import json
import psutil
import subprocess
import platform
import os
from urllib.parse import urlparse
import ctypes

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
        salida = subprocess.check_output("netsh interface show interface", shell=True).decode("utf-8",errors="ignore")
        linea1 = salida.split('\n')
        supuesto = False
        for linea in linea1:
            if "Conectado" in linea or "Connected" in linea:
                if "Wi-Fi" in linea:
                    return True
                if "Ethernet" in linea:
                    pass
        return False
    def admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
        
    
class Control_Parental:
    def __init__(self):
        self.Web_whitelist = []
        self.Web_blacklist = []
        self.hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        self.redirect_ip = "127.0.0.1"
    def limpiar_url(self, url):
        """Extrae el dominio de la URL y lo normaliza."""
        parsed = urlparse(url)
        dominio = parsed.netloc or parsed.path
        return dominio.strip().lower().replace('/', '')

    def agregar_blacklist(self, web_url):
        dominio = self.limpiar_url(web_url)
        if dominio not in self.Web_blacklist:
            self.Web_blacklist.append(dominio)
            try:
                with open(self.hosts_path, "r+") as file:
                    contenido = file.read()
                    if dominio not in contenido:
                        file.write(f"{self.redirect_ip} {dominio}\n")
            except PermissionError:
                print("Permiso denegado: ejecuta como administrador.")
            except Exception as e:
                print(f"Error al bloquear: {e}")
    def quitar_blacklist(self, web_url):
        dominio = self.limpiar_url(web_url)
        try:
            if dominio in self.Web_blacklist:
                self.Web_blacklist.remove(dominio)

            with open(self.hosts_path, 'r+') as file:
                lineas = file.readlines()
                file.seek(0)
                for linea in lineas:
                    if dominio not in linea:
                        file.write(linea)
                file.truncate()
        except PermissionError:
            print("Permiso denegado: ejecuta como administrador.")
        except Exception as e:
            print(f"Error al desbloquear: {e}")

class datos_variantes:
    def conectado():
        try:
            salida = subprocess.run(["ping", "-n", "1", "google.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
            return salida.returncode == 0
        except Exception:
            return False
    def wifi_datos():
        ruta_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Datos_Configuracion', 'Datos.json')
        with open(ruta_json, "r") as file:
            datos_wifi = json.load(file)
        resultado = subprocess.check_output("netsh wlan show networks mode=bssid", shell=True).decode("utf-8",errors="ignore")
        lineas_1 = resultado.split("\n")
        lista = []
        red = {}

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
