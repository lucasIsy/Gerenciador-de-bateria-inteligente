# ====================================================================
# [ATENCAO] Os IoTs foram criados utilizando o gemini pro 3.1.
# O objetivo é criar um dispositivo que se aproximasse da realidade.
# ====================================================================
import time
import json
import random
import math
import os
import socket
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# --- CONFIGURAÇÃO MQTT ---
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = 1883
TOPICO = "iot/geracao/painel"
TOPICO_STATUS_CONEXAO = "status_conexao/painel_solar"

# --- CONFIGURAÇÃO DO PAINEL ---
POTENCIA_PICO = 4 * 545  # 4 painéis de 545W

# Inicializa o cliente MQTT
client = mqtt.Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id="Painel_solar"
)

conectado = False

# Envia o status MQTT-desligado
client.will_set(topic=TOPICO_STATUS_CONEXAO, payload="offline", qos=1, retain=True)

while not conectado:
    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        conectado = True
        client.loop_start()
        print("Conexão com o broker MQTT concluída.")
    except (socket.gaierror, ConnectionRefusedError) as e:
        print(f"Broker MQTT indisponível ({e}). Tentando novamente em 5 segundos...")
        time.sleep(5)

# Variáveis da simulação de tempo
hora_atual = 5.5
passo_tempo_horas = 0.1 # cada execução do loop passa 6 minutos -> 6 / 60 minutos = 0.1

print("[IoT-Painel] Iniciando Painel Solar\n")

# Envia o status MQTT-Ligado 
client.publish(topic=TOPICO_STATUS_CONEXAO, payload="online", qos=1, retain=True)

try:
    while True:
        if 6.0 <= hora_atual <= 18.0:
            angulo = (hora_atual - 6.0) * math.pi / 12.0
            intensidade_solar = math.sin(angulo)
            fator_clima = random.uniform(0.95, 1)
            potencia = POTENCIA_PICO * intensidade_solar * fator_clima
            irradiacao = 1000.0 * intensidade_solar * fator_clima
            temperatura = 20.0 + (15.0 * intensidade_solar) + random.uniform(-1, 1)
        else:
            potencia = 0.0
            irradiacao = 0.0
            temperatura = 20.0 + random.uniform(-1.0, 1.0)

        # 2. Estruturação do Payload JSON
        payload = {
            "id_dispositivo": "painel_solar",
            "categoria": "Geracao",
            "timestamp": int(time.time()),
            "hora_simulada": round(hora_atual, 2),
            "irradiacao": round(irradiacao, 1),
            "temperatura": round(temperatura, 1),
            "potencia_gerada": round(potencia, 2),
            "status": "GERANDO" if potencia > 0 else "STANDBY"
        }
        # DEBUG
        # print(f"Tempo: {int(hora_atual):02d}:{int((hora_atual%1)*60):02d} | Potência: {payload['potencia_gerada']} W | Status: {payload['status']}")
        client.publish(TOPICO, json.dumps(payload), qos=1, retain=False)
        # 4. Avanço do tempo e loop
        hora_atual += passo_tempo_horas
        if hora_atual >= 24.0: 
            hora_atual = 0.0  # Vira o dia
            
        time.sleep(1)  # Aguarda 1 segundo real antes do próximo envio

except KeyboardInterrupt:
    print("\nSimulador interrompido pelo usuário. Desconectando...")
    client.publish(topic=TOPICO_STATUS_CONEXAO, payload="offline", qos=1, retain=True)
    client.loop_stop()
    client.disconnect()