# =======================================================
# Baixa o conector do kafka e o plugin mqtt
# =======================================================
FROM confluentinc/cp-kafka-connect-base:7.5.0 AS instalador
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-mqtt:latest

# =======================================================
# IMAGEM FINAL
# =======================================================
FROM confluentinc/cp-kafka-connect:7.5.0

# Copia APENAS o plugin baixado para a imagem
COPY --from=instalador /usr/share/confluent-hub-components /usr/share/confluent-hub-components