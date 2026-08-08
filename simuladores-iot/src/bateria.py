# ====================================================================
# [ATENCAO] Os IoTs foram criados utilizando o gemini pro 3.1.
# O objetivo é criar um dispositivo que se aproximasse da realidade.
# ====================================================================

import time
import json
import os
import socket
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# --- CONFIGURAÇÕES DA BATERIA ---
BATERIA_MAX_WH = 1000.0
bateria_atual_wh = 1000.0
geracao_solar_atual = 0.0
consumo_iot_atual = 0.0

# Dicionário para rastrear o consumo individual de cada dispositivo IoT
consumos_por_dispositivo = {}

# Configuração de tempo para o teste correr mais rápido
# 1 segundo real vai simular 5 minutos
FATOR_TEMPO_HORAS = 5 / 60 

# --- CONFIGURAÇÃO MQTT ---
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = 1883
TOPICO_GERACAO = "iot/geracao/painel"
TOPICO_STATUS_BATERIA = "iot/armazenamento/bateria"
TOPICO_CONSUMO = "iot/dispositivos/+/consumo"

def on_message(client, userdata, msg):
    global geracao_solar_atual, consumo_iot_atual, consumos_por_dispositivo
    
    try:
        payload = json.loads(msg.payload.decode())
        
        if msg.topic == TOPICO_GERACAO:
            geracao_solar_atual = float(payload.get("potencia_gerada", 0.0))
            
        elif msg.topic.startswith("iot/dispositivos/") and msg.topic.endswith("/consumo"):
            partes_topico = msg.topic.split("/")
            device_id = partes_topico[2]
            watts = float(payload.get("watts", 0.0))
            consumos_por_dispositivo[device_id] = watts
            consumo_iot_atual = sum(consumos_por_dispositivo.values())
    
    except Exception as e:
        print(f"[MQTT-Dispositivos] Erro ao processar mensagem MQTT: {e}")

# Inicializa o cliente MQTT
client = mqtt.Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id="Bateria_Central"
)

client.on_message = on_message
conectado = False
while not conectado:
    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        conectado = True
        print("Conectado ao broker MQTT com sucesso!")
    except (socket.gaierror, ConnectionRefusedError) as e:
        print(f"Broker MQTT indisponível ({e}). Tentando novamente em 5 segundos...")
        time.sleep(5)

# Se inscreve nos topico de geracao e dispositivos para realizar o calculo
# Bateria = Bateria + (geracao - consumo(dispositivos IoT)
client.subscribe([(TOPICO_GERACAO, 0), (TOPICO_CONSUMO, 0)])
client.loop_start()

print("[IoT-Bateria] Inicializada a 100%.")

try:
    while True:
        # 1. Calcula o Saldo Liquido de Energia (Input - Output)
        saldo_watts = geracao_solar_atual - consumo_iot_atual
        
        # 2. Converte a potência instantânea (W) em energia (Wh)
        variacao_energia = saldo_watts * FATOR_TEMPO_HORAS
        
        # 3. Aplica a variação ao valor atual
        bateria_atual_wh += variacao_energia
        
        # 4. Evita o acumulo de saldo negativo na bateria
        if bateria_atual_wh < 0.0:
            bateria_atual_wh = 0.0

        # Evita que ela passe do limite máximo (100%)
        elif bateria_atual_wh > BATERIA_MAX_WH:
            bateria_atual_wh = BATERIA_MAX_WH
            
        # 5. Converte para percentagem
        porcentagem_bateria = (bateria_atual_wh / BATERIA_MAX_WH) * 100.0
        
        # 6. Prepara o payload para enviar ao mosquitto
        payload_status = {
            "id_dispositivo": "bateria_principal",
            "categoria": "Bateria",
            "nivel_bateria": round(porcentagem_bateria, 2),
            "saldo_watts": round(saldo_watts, 1),
            "consumo_total_iot": round(consumo_iot_atual, 1),
            "timestamp": int(time.time())
        }
        
        # 7. Publica o status final no MQTT para o ecossistema Kafka
        client.publish(TOPICO_STATUS_BATERIA, json.dumps(payload_status))
        
        time.sleep(1) # Ciclo de atualização de 1 segundo

except KeyboardInterrupt:
    print("\n🔌 A desligar o simulador da bateria...")
    client.loop_stop()
    client.disconnect()