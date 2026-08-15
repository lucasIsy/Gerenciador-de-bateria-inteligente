#!/bin/bash

CONNECT_URL="http://localhost:8083/connectors"

echo "Aguardando Kafka Connect iniciar em $CONNECT_URL..."
until curl -s -f -o /dev/null "$CONNECT_URL"; do
    echo "Ainda indisponível... tentando em 5s"
    sleep 5
done
echo "Kafka Connect pronto! Registrando conectores..."

# ==========================================
# 1. Source Connector (Mosquitto -> Kafka)
# ==========================================
# 1. Conector para o Painel Solar
echo -e "\n\nCriando/Atualizando: mqtt-source-geracao..."
curl -X PUT "http://localhost:8083/connectors/mqtt-source-geracao/config" \
  -H "Content-Type: application/json" \
  -d '{
    "connector.class": "io.confluent.connect.mqtt.MqttSourceConnector",
    "tasks.max": "1",
    "mqtt.server.uri": "tcp://mosquitto:1883",
    "mqtt.client.id": "kafka-connect-geracao",
    "mqtt.topics": "iot/geracao/#",
    "kafka.topic": "iot_geracao",
    "confluent.topic.bootstrap.servers": "kafka:9092",
    "confluent.topic.replication.factor": "1",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter":"org.apache.kafka.connect.converters.ByteArrayConverter"
}'

# 2. Conector para Armazenamento
echo -e "\n\nCriando/Atualizando: mqtt-source-armazenamento..."
curl -X PUT "http://localhost:8083/connectors/mqtt-source-armazenamento/config" \
  -H "Content-Type: application/json" \
  -d '{
    "connector.class": "io.confluent.connect.mqtt.MqttSourceConnector",
    "tasks.max": "1",
    "mqtt.server.uri": "tcp://mosquitto:1883",
    "mqtt.client.id": "kafka-connect-armazenamento",
    "mqtt.topics": "iot/armazenamento/#",
    "kafka.topic": "iot_armazenamento",
    "confluent.topic.bootstrap.servers": "kafka:9092",
    "confluent.topic.replication.factor": "1",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter":"org.apache.kafka.connect.converters.ByteArrayConverter"
}'

# 3. Conector para os Dispositivos
echo -e "\n\nCriando/Atualizando: mqtt-source-dispositivos..."
curl -X PUT "http://localhost:8083/connectors/mqtt-source-dispositivos/config" \
  -H "Content-Type: application/json" \
  -d '{
    "connector.class": "io.confluent.connect.mqtt.MqttSourceConnector",
    "tasks.max": "1",
    "mqtt.server.uri": "tcp://mosquitto:1883",
    "mqtt.client.id": "kafka-connect-dispositivos",
    "mqtt.topics": "iot/dispositivos/#",
    "kafka.topic": "iot_dispositivos",
    "confluent.topic.bootstrap.servers": "kafka:9092",
    "confluent.topic.replication.factor": "1",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.converters.ByteArrayConverter"
}'

# ==========================================
# 2. Sink Connector (Kafka -> Mosquitto)
# ==========================================
echo -e "\n\nCriando/Atualizando: mosquitto-sink-comandos..."
curl -X PUT "http://localhost:8083/connectors/mosquitto-sink-comandos/config" \
  -H "Content-Type: application/json" \
  -d '{
    "connector.class": "io.confluent.connect.mqtt.MqttSinkConnector",
    "tasks.max": "1",
    "mqtt.server.uri": "tcp://mosquitto:1883",
    "mqtt.client.id": "kafka-connect-sink-comandos",
    "topics": "comandos_mqtt_iot",
    "mqtt.topic": "comandos/#",
    "confluent.topic.bootstrap.servers": "kafka:9092",
    "confluent.topic.replication.factor": "1",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.storage.StringConverter",

    "transforms": "Mosquitto",
    "transforms.Mosquitto.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.Mosquitto.regex": "comandos_mqtt_iot",
    "transforms.Mosquitto.replacement": "comandos/"
}'

echo -e "\n\nProcesso finalizado!"