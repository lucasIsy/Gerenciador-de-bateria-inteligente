from socket import socket
import time
import json
import os
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# --- CONFIGURAÇÃO MQTT ---
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = 1883
# Chega do kafka
TOPICO_COMANDOS = "comandos/#"

# 1. IoTs Simulados
dispositivos = {
    "servidor": {
        "id_dispositivo": "servidor_sistema",
        "watts": 150.0,
        "ligado": True,
        "prioridade": 1,
        "categoria": "Critico",
    },
    "sensor_temperatura": {
        "id_dispositivo": "sensor_temperatura",
        "watts": 1.5,
        "ligado": True,
        "prioridade": 1,
        "categoria": "Critico",
    },
    "cameras_seguranca": {
        "id_dispositivo": "cameras_seguranca",
        "watts": 25.0,
        "ligado": True,
        "prioridade": 1,
        "categoria": "Critico",
    },
    "luzes_seguranca": {
        "id_dispositivo": "luzes_seguranca",
        "watts": 40.0,
        "ligado": True,
        "prioridade": 1,
        "categoria": "Critico",
    },
    "modem": {
        "id_dispositivo": "modem",
        "watts": 12.0,
        "ligado": True,
        "prioridade": 1,
        "categoria": "Critico",
    },
    "geladeira": {
        "id_dispositivo": "geladeira",
        "watts": 150.0,
        "ligado": True,
        "prioridade": 2,
        "categoria": "Essencial",
    },
    "ventilador": {
        "id_dispositivo": "ventilador",
        "watts": 65.0,
        "ligado": True,
        "prioridade": 3,
        "categoria": "Importante",
    },
    "alexa": {
        "id_dispositivo": "alexa",
        "watts": 3.0,
        "ligado": True,
        "prioridade": 4,
        "categoria": "Secundario",
    },
}

# Dicionário de backup para saber quanta potência restaurar quando o dispositivo for religado
POTENCIAS_ORIGINAIS = {k: v["watts"] for k, v in dispositivos.items()}

def on_message(client, userdata, msg):
    global dispositivos
    try:
        raw_payload = msg.payload.decode()
        payload = json.loads(raw_payload)
        categoria_alvo = payload.get("CATEGORIA")
        comando = payload.get("COMANDO") 

        for dev_id, info in dispositivos.items():
            if info["categoria"] == categoria_alvo:
                encontrou_alguem = True
                if comando == "DESLIGAR" and info["ligado"]:
                    info["ligado"] = 0
                    print(f"🛑 [IoT-Comando] Corte de Energia: Desligando {dev_id} (Categoria: {categoria_alvo}).")
                elif comando == "LIGAR" and not info["ligado"]:
                    info["ligado"] = 1
                    print(f"🟢 [IoT-Comando] Energia Restaurada: Religando {dev_id} (Categoria: {categoria_alvo}).")
                
    except Exception as e:
        print(f"[IoT-Comando] Erro ao processar comando recebido: {e}")

# Inicializa o cliente MQTT
client = mqtt.Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id="Dispositivos_IoT"
)

client.on_message = on_message
conectado = False
while not conectado:
    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        conectado = True
        print("Conexão com o broker MQTT concluída.")
    except (socket.gaierror, ConnectionRefusedError) as e:
        print(f"Broker MQTT indisponível ({e}). Tentando novamente em 5 segundos...")
        time.sleep(5)
        
# Topico das ordens de desligar/ligar
client.subscribe(TOPICO_COMANDOS) 
client.loop_start()

print("[IoT-Start] Iniciando Dispositivos")

try:
    while True:
        timestamp_atual = int(time.time())

        # Publica o consumo de cada dispositivo no seu respectivo tópico
        for dev, info in dispositivos.items():

            # Se o dispositivo estiver ativo, envia a potência real. Se não, envia 0W.
            consumo_atual = info["watts"] if info["ligado"] else 0.0
            payload = {
                "id_dispositivo": info["id_dispositivo"], 
                "categoria": info["categoria"],           
                "ligado": info["ligado"],                   
                "prioridade": info["prioridade"],         
                "watts": consumo_atual,
                "timestamp": timestamp_atual
            }

            # Monta o tópico dinâmico: iot/dispositivos/geladeira/consumo, etc.
            topico_dinamico = f"iot/dispositivos/{dev}/consumo"   
            client.publish(topico_dinamico, json.dumps(payload))

        time.sleep(1)

except KeyboardInterrupt:
    print("\n [IoT-Finalizado] Desligando o simulador de dispositivos...")
    client.loop_stop()
    client.disconnect()