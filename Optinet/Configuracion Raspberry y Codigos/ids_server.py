# Raspberry IDS/IPS HTTP Server - servidor_ids.py

from flask import Flask, request, jsonify
from threading import Thread
from scapy.all import sniff, IP, TCP, UDP, DNS, DNSQR, ARP, Ether
import time
import json
import os
from datetime import datetime

app = Flask(__name__)

# Datos compartidos
dispositivos_detectados = {}
dispositivos_autorizados = set()
dispositivos_sospechosos = {}
alertas_ids = []

capturando = False

# Utilidades

def agregar_alerta(tipo, detalle):
    alertas_ids.append({
        "hora": datetime.now().strftime("%H:%M:%S"),
        "tipo": tipo,
        "detalle": detalle
    })
    if len(alertas_ids) > 100:
        alertas_ids.pop(0)

# Captura y analisis

def analizar_paquete(pkt):
    if ARP in pkt and pkt[ARP].op in (1, 2):  # request o reply
        ip = pkt[ARP].psrc
        mac = pkt[ARP].hwsrc
        dispositivos_detectados[ip] = mac

        if mac not in dispositivos_autorizados:
            dispositivos_sospechosos[ip] = mac
            agregar_alerta("Dispositivo Sospechoso", f"IP: {ip}, MAC: {mac}")

        # Deteccion de ARP Spoofing basica
        for known_ip, known_mac in dispositivos_detectados.items():
            if known_ip == ip and known_mac != mac:
                agregar_alerta("ARP Spoofing", f"Conflicto IP {ip} con MAC {mac} vs {known_mac}")

# Hilo de sniffing

def captura_continua():
    global capturando
    while capturando:
        sniff(filter="arp", prn=analizar_paquete, store=0, timeout=5)

@app.route("/comando", methods=["POST"])
def manejar_comando():
    global capturando
    accion = request.json.get("accion")
    if accion == "iniciar_captura":
        if not capturando:
            capturando = True
            Thread(target=captura_continua, daemon=True).start()
        return jsonify({"status": "captura iniciada"})
    elif accion == "detener_captura":
        capturando = False
        return jsonify({"status": "captura detenida"})
    return jsonify({"error": "comando no reconocido"}), 400

@app.route("/dispositivos")
def obtener_dispositivos():
    return jsonify([
        {"ip": ip, "mac": mac} for ip, mac in dispositivos_detectados.items()
    ])

@app.route("/sospechosos")
def obtener_sospechosos():
    return jsonify([
        {"ip": ip, "mac": mac} for ip, mac in dispositivos_sospechosos.items()
    ])

@app.route("/alertas")
def obtener_alertas():
    return jsonify(alertas_ids)
    
@app.route('/bloqueados', methods=['GET'])
def obtener_bloqueados():
    bloqueados = []
    try:
        with open("bloqueados.txt", "r") as f:
            for linea in f:
                bloqueados.append({"ip": linea.strip()})
    except FileNotFoundError:
        bloqueados = []
    return jsonify(bloqueados)

if __name__ == "__main__":
    print("[Raspberry] Servidor HTTP IDS escuchando en puerto 6001...")
    app.run(host="0.0.0.0", port=6001)