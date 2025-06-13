from scapy.all import sniff, IP, get_if_list
from collections import defaultdict
from datetime import datetime
import subprocess
import pickle
class Banda:
    def ip(self):
        salida = subprocess.check_output("sudo arp-scan --interface=wlan0 --localnet", shell=True).decode("utf-8", errors="ignore").split('\n')
        informacion = []
        for linea in salida:
            linea = linea.split("\t")
            if len(linea) == 3:
                informacion.append([linea[0], linea[1]])
        return informacion

    def captura_trafico_por_ip(self, ip_objetivos, duracion=0.1):
        trafico_por_ip = defaultdict(int)

        def procesar_paquete(paquete):
            if IP in paquete:
                ip_origen = paquete[IP].src
                if ip_origen in ip_objetivos:
                    trafico_por_ip[ip_origen] += len(paquete)

        interfaces = get_if_list()
        sniff(iface=interfaces, prn=procesar_paquete, store=False, timeout=duracion)

        datos = {}
        for ip in ip_objetivos:
            total_bytes = trafico_por_ip[ip]
            kbps = (total_bytes * 8) / 1024 / duracion
            datos[ip] = f"{kbps:.2f}"
        return datos

    def obtener_tiempos_conexion(self):
        salida = subprocess.check_output("iw dev wlan0 station dump", shell=True).decode("utf-8", errors="ignore")
        bloques = salida.split("Station")[1:]  # Ignora el primer bloque va
        tiempos = {}

        for bloque in bloques:
            lineas = bloque.strip().split("\n")
            mac = lineas[0].split()[0]
            tiempo = "NA"
            for linea in lineas:
                if "connected time:" in linea:
                    # Maneja espacios m
                    partes = linea.strip().split()
                    if len(partes) >= 3:
                        tiempo = partes[2]
                    break
            tiempos[mac] = tiempo
        return tiempos

    def estado(self):
        lista_dispositivos = self.ip()
        lista_ip = [x[0] for x in lista_dispositivos]
        trafico = self.captura_trafico_por_ip(lista_ip, duracion=0.5)
        tiempos_conexion = self.obtener_tiempos_conexion()
        datos_finales = []

        for ip, mac in lista_dispositivos:
            # Verificar conectividad con ping
            try:
                salida = subprocess.check_output(f"ping -c 1 -W 1 {ip}", shell=True).decode("utf-8", errors="ignore")
                estado = "Conectado" if "0% packet loss" in salida else "Desconectado"
            except Exception:
                estado = "Desconectado"

            tiempo = tiempos_conexion.get(mac, "NA")
            trafico_ip = trafico.get(ip, "0.00")

            datos_finales.append([ip, mac, estado, tiempo, trafico_ip])
            
        with open("datos_Banda.pkl","wb") as file:
            pickle.dump(datos_finales,file)
        return (datos_finales)

# Ejecutar
pack = Banda()
print(pack.estado())
