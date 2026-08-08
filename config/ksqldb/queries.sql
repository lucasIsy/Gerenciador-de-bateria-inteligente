-- 0A. Captura os dados do IoT vindos do KAFKA
CREATE STREAM stream_telemetria_bruta (
    id_dispositivo VARCHAR,
    nivel_bateria DOUBLE
) WITH (
    KAFKA_TOPIC='iot_armazenamento',
    VALUE_FORMAT='JSON'
);

-- 0B. Cria o topico dos comandos que vao pros IoT
CREATE STREAM stream_comandos_finais (
    chave_unica VARCHAR KEY,
    timestamp BIGINT,
    categoria VARCHAR,
    comando VARCHAR
) WITH (
    KAFKA_TOPIC='comandos_mqtt_iot',
    VALUE_FORMAT='JSON',
    PARTITIONS=1
);

-- 1. Tabela para controlar o último comando enviado
-- Evita enviar comandos repetidos
CREATE TABLE tabela_ultimo_comando_enviado AS
SELECT 
    chave_unica,
    LATEST_BY_OFFSET(comando) AS comando
FROM stream_comandos_finais
GROUP BY chave_unica
EMIT CHANGES;

CREATE STREAM stream_telemetria_explodida WITH (KAFKA_TOPIC='telemetria_explodida') AS
SELECT 
    id_dispositivo,
    (id_dispositivo + '-' + SPLIT(CALCULAR_BATERIAS(nivel_bateria), ':')[1]) AS chave_unica,
    SPLIT(CALCULAR_BATERIAS(nivel_bateria), ':')[1] AS categoria,
    SPLIT(CALCULAR_BATERIAS(nivel_bateria), ':')[2] AS comando
FROM stream_telemetria_bruta
WHERE nivel_bateria IS NOT NULL
EMIT CHANGES;

CREATE STREAM stream_telemetria_rekeyed WITH (KAFKA_TOPIC='telemetria_rekeyed', PARTITIONS=1) AS
SELECT *
FROM stream_telemetria_explodida
PARTITION BY chave_unica
EMIT CHANGES;

INSERT INTO stream_comandos_finais
SELECT 
    s.chave_unica AS chave_unica,
    UNIX_TIMESTAMP() AS timestamp,
    s.categoria AS categoria,
    s.comando AS comando
FROM stream_telemetria_rekeyed s
LEFT JOIN tabela_ultimo_comando_enviado t ON s.chave_unica = t.chave_unica
WHERE 
    s.comando != 'MANTER' 
    AND (t.comando IS NULL OR s.comando != t.comando)
EMIT CHANGES;