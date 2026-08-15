from socket import socket
import time
import json
import os
import random
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# --- CONFIGURAÇÃO MQTT ---
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = 1883
TOPICO_COMANDOS = "comandos/#"
TOPICO_STATUS_CONEXAO = "status_conexao/dispositivos_iot"

# 1. IoTs Simulados
dispositivos = {
    "servidor": {
        "id_dispositivo": "servidor_sistema",
        "potencia_nominal": 150.0,
        "tensao_nominal": 220.0,
        "fator_potencia": 0.95,
        "tipo_comportamento": "carga_variavel",
        "ligado": True,
        "prioridade": 1,
        "categoria": "Critico",
    },
    "sensor_temperatura": {
        "id_dispositivo": "sensor_temperatura",
        "potencia_nominal": 1.5,
        "tensao_nominal": 220.0,
        "fator_potencia": 0.90,
        "tipo_comportamento": "constante",
        "ligado": True,
        "prioridade": 1,
        "categoria": "Critico",
    },
    "cameras_seguranca": {
        "id_dispositivo": "cameras_seguranca",
        "potencia_nominal": 25.0,
        "tensao_nominal": 220.0,
        "fator_potencia": 0.90,
        "tipo_comportamento": "constante",
        "ligado": True,
        "prioridade": 1,
        "categoria": "Critico",
    },
    "luzes_seguranca": {
        "id_dispositivo": "luzes_seguranca",
        "potencia_nominal": 40.0,
        "tensao_nominal": 220.0,
        "fator_potencia": 0.98,
        "tipo_comportamento": "constante",
        "ligado": True,
        "prioridade": 1,
        "categoria": "Critico",
    },
    "modem": {
        "id_dispositivo": "modem",
        "potencia_nominal": 12.0,
        "tensao_nominal": 220.0,
        "fator_potencia": 0.90,
        "tipo_comportamento": "constante",
        "ligado": True,
        "prioridade": 1,
        "categoria": "Critico",
    },
    "geladeira": {
        "id_dispositivo": "geladeira",
        "potencia_standby": 12.0,
        "potencia_compressor": 150.0,
        "tensao_nominal": 127.0,
        "fator_potencia": 0.82,
        "tipo_comportamento": "ciclico",
        "ligado": True,
        "prioridade": 2,
        "categoria": "Essencial",
    },
    "ventilador": {
        "id_dispositivo": "ventilador",
        "potencia_nominal": 65.0,
        "tensao_nominal": 127.0,
        "fator_potencia": 0.85,
        "tipo_comportamento": "constante",
        "ligado": True,
        "prioridade": 3,
        "categoria": "Importante",
    },
    "alexa": {
        "id_dispositivo": "alexa",
        "potencia_nominal": 3.0,
        "tensao_nominal": 127.0,
        "fator_potencia": 0.90,
        "tipo_comportamento": "constante",
        "ligado": True,
        "prioridade": 4,
        "categoria": "Secundario",
    },
    
    # ==========================================
    # CATEGORIA: SECUNDÁRIO (Prioridade 4)
    # ==========================================
    "tv_sala": {
        "id_dispositivo": "tv_sala",
        "potencia_nominal": 120.0,
        "tensao_nominal": 220.0,
        "fator_potencia": 0.95,
        "tipo_comportamento": "constante",
        "ligado": True,
        "prioridade": 4,
        "categoria": "Secundario",
    },
    "carregador_celular": {
        "id_dispositivo": "carregador_celular",
        "potencia_nominal": 18.0,
        "tensao_nominal": 127.0,
        "fator_potencia": 0.85,
        "tipo_comportamento": "constante",
        "ligado": True,
        "prioridade": 4,
        "categoria": "Secundario",
    },
    "home_theater": {
        "id_dispositivo": "home_theater",
        "potencia_nominal": 85.0,
        "tensao_nominal": 127.0,
        "fator_potencia": 0.90,
        "tipo_comportamento": "carga_variavel", # O som varia com as explosões do filme
        "ligado": False,
        "prioridade": 4,
        "categoria": "Secundario",
    },
    
    # ==========================================
    # CATEGORIA: SUPERFICIAL (Prioridade 5)
    # ==========================================
    "console_videogame": {
        "id_dispositivo": "console_videogame",
        "potencia_nominal": 200.0,
        "tensao_nominal": 220.0,
        "fator_potencia": 0.95,
        "tipo_comportamento": "carga_variavel",
        "ligado": False,
        "prioridade": 5,
        "categoria": "Superficial",
    },
    "fita_led_decorativa": {
        "id_dispositivo": "fita_led_decorativa",
        "potencia_nominal": 24.0,
        "tensao_nominal": 127.0,
        "fator_potencia": 0.90,
        "tipo_comportamento": "constante",
        "ligado": True,
        "prioridade": 5,
        "categoria": "Superficial",
    },
    "adega_vinhos": {
        "id_dispositivo": "adega_vinhos",
        "potencia_standby": 10.0,
        "potencia_compressor": 95.0,
        "tensao_nominal": 220.0,
        "fator_potencia": 0.82,
        "tipo_comportamento": "ciclico", # Segue o mesmo padrão da geladeira
        "ligado": True,
        "prioridade": 5,
        "categoria": "Superficial",
    },
    "robo_aspirador": {
        "id_dispositivo": "robo_aspirador",
        "potencia_nominal": 35.0,
        "tensao_nominal": 127.0,
        "fator_potencia": 0.95,
        "tipo_comportamento": "constante", # Considerando a base de carregamento
        "ligado": True,
        "prioridade": 5,
        "categoria": "Superficial",
    },
    "difusor_ar": {
        "id_dispositivo": "difusor_ar",
        "potencia_nominal": 12.0,
        "tensao_nominal": 127.0,
        "fator_potencia": 0.80,
        "tipo_comportamento": "constante",
        "ligado": False,
        "prioridade": 5,
        "categoria": "Superficial",
    }
}

# Inicialização de variáveis de controle de tempo e energia
for dev, info in dispositivos.items():
    info["ultimo_timestamp"] = time.time()
    info["energia_economizada_total_wh"] = 0.0
    info["energia_economizada"] = 0.0

def calcular_potencia_dinamica(info, timestamp):
    if not info["ligado"]:
        return 0.0
        
    tipo = info.get("tipo_comportamento", "constante")
    
    if tipo == "ciclico":
        ciclo_ativo = (timestamp // 900) % 2 == 0
        potencia_base = info["potencia_compressor"] if ciclo_ativo else info["potencia_standby"]
        return potencia_base * random.uniform(0.95, 1.05)
        
    elif tipo == "carga_variavel":
        return info["potencia_nominal"] * random.uniform(0.8, 1.2)
        
    else:
        return info["potencia_nominal"] * random.uniform(0.97, 1.03)

def on_message(client, userdata, msg):
    global dispositivos
    try:
        raw_payload = msg.payload.decode()
        payload = json.loads(raw_payload)
        categoria_alvo = payload.get("CATEGORIA")
        comando = payload.get("COMANDO") 

        for dev_id, info in dispositivos.items():
            if info["categoria"] == categoria_alvo:
                if comando == "DESLIGAR" and info["ligado"]:
                    info["ligado"] = 0
                    info["energia_economizada"] = 0.0 # Reseta o ciclo atual
                    print(f"🛑 [IoT-Comando] Corte de Energia: Desligando {dev_id} (Categoria: {categoria_alvo}).")
                
                elif comando == "LIGAR" and not info["ligado"]:
                    info["ligado"] = 1
                    economia = info["energia_economizada"]
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
        
# Topico das ordens de desligar/ligar
client.subscribe(TOPICO_COMANDOS) 

print("[IoT-Start] Iniciando Dispositivos")

# Envia o status MQTT-Ligado 
client.publish(topic=TOPICO_STATUS_CONEXAO, payload="online", qos=1, retain=True)

try:
    while True:
        tempo_atual = time.time()
        timestamp_int = int(tempo_atual)

        for dev, info in dispositivos.items():
            # Calcula tempo exato passado desde o último ciclo
            delta_t_segundos = tempo_atual - info["ultimo_timestamp"]
            info["ultimo_timestamp"] = tempo_atual
            
            watts_calculado = calcular_potencia_dinamica(info, timestamp_int)
            tensao_base = info.get("tensao_nominal", 220.0)
            fator_p = info.get("fator_potencia", 1.0)
            
            volts = tensao_base * random.uniform(0.98, 1.02) if info["ligado"] else 0.0
            amperes = watts_calculado / (volts * fator_p) if volts > 0 else 0.0

            potencia_base = info.get("potencia_nominal", info.get("potencia_compressor", 0.0))

            # Se estiver desligado, acumula a energia que teria sido gasta
            if not info["ligado"]:
                # Se está DESLIGADO: Acumula a energia economizada
                watts_economizados = potencia_base
                energia_wh = (potencia_base * delta_t_segundos) / 3600.0
                info["energia_economizada"] += energia_wh
            else:
                # Se está LIGADO: A economia é zero (reseta)
                watts_economizados = 0.0
                info["energia_economizada"] = 0.0

            payload = {
                "id_dispositivo": info["id_dispositivo"], 
                "categoria": info["categoria"],           
                "ligado": info["ligado"],                   
                "prioridade": info["prioridade"],         
                "watts": round(watts_calculado, 2),
                "watts_economizados": round(watts_economizados, 2),
                "energia_economizada": round(info["energia_economizada"], 4),
                "volts": round(volts, 2),
                "amperes": round(amperes, 2),
                "timestamp": timestamp_int
            }

            # Monta o tópico dinâmico: iot/dispositivos/geladeira/consumo, etc.
            topico_dinamico = f"iot/dispositivos/{dev}/consumo"   
            client.publish(topico_dinamico, json.dumps(payload), qos=1, retain=False)

        time.sleep(1)

except KeyboardInterrupt:
    print("\n [IoT-Finalizado] Desligando o simulador de dispositivos...")
    client.publish(topic=TOPICO_STATUS_CONEXAO, payload="offline", qos=1, retain=True)
    client.loop_stop()
    client.disconnect()