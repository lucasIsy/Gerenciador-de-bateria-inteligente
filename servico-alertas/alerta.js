const { Kafka } = require('kafkajs');
const axios = require('axios');

const DISCORD_WEBHOOK_URL = process.env.DISCORD_WEBHOOK_URL;
const KAFKA_BROKER = process.env.KAFKA_BROKER || 'localhost:9092';

if (!DISCORD_WEBHOOK_URL) {
    console.error("ERRO: Variável DISCORD_WEBHOOK_URL não foi definida!");
    process.exit(1);
}

const kafka = new Kafka({
    clientId: 'servico-alertas',
    brokers: [KAFKA_BROKER]
});

const consumer = kafka.consumer({ groupId: 'grupo-alertas-discord' });

let capacidadeAtual = "Desconhecido";
let autonomiaAtual = "Desconhecido";

async function run() {
    await consumer.connect();

    await consumer.subscribe({
        topics: ['comandos_mqtt_iot', 'iot_armazenamento'],
        fromBeginning: false
    });

    console.log(`[Alerta-Comandos] Escutando alertas no Kafka (${KAFKA_BROKER})`);

    await consumer.run({
        eachMessage: async ({ topic, message }) => {
            try {
                const payload = JSON.parse(message.value.toString());

                if (topic === 'iot_armazenamento') {
                    if (payload.nivel_bateria !== undefined) {
                        capacidadeAtual = payload.nivel_bateria;
                    }
                    if (payload.autonomia_estimada_horas !== undefined) {
                        autonomiaAtual = payload.autonomia_estimada_horas;
                    }
                }
                else if (topic === 'comandos_mqtt_iot') {
                    const { ID_DISPOSITIVO, CATEGORIA, COMANDO } = payload;

                    const CAPACIDADE = capacidadeAtual !== "Desconhecido"
                        ? `${Math.round(Number(capacidadeAtual))}%`
                        : "Desconhecido";

                    let DURACAO = "Desconhecido";
                    if (autonomiaAtual !== "Desconhecido") {
                        DURACAO = Number(autonomiaAtual) === -1 ? "Carregando ⚡" : `${Number(autonomiaAtual).toFixed(1)} h`;
                    }

                    if (COMANDO === 'DESLIGAR') {
                        const embedDesligar = {
                            title: "⚠️ DESLIGANDO DISPOSITIVOS",
                            description: "A produção de energia encerrou e bateria em descarregamento.",
                            color: 16711680,
                            fields: [
                                { name: "🔌 Ação Automática", value: `\` DESLIGADO \``, inline: false },
                                { name: "📋 Categoria", value: `\`${CATEGORIA}\``, inline: false },
                                { name: "Capacidade Restante", value: `\`${CAPACIDADE}\``, inline: false },
                                { name: "Duração da Bateria", value: `\`${DURACAO}\``, inline: false }
                            ],
                            timestamp: new Date().toISOString(),
                            footer: { text: "Sistema de Monitoramento IoT" }
                        };

                        console.log(`[Alerta-Discord] Enviando alerta de DESLIGAR - Dispositivo ${ID_DISPOSITIVO}.`);

                        try {
                            await axios.post(DISCORD_WEBHOOK_URL, { embeds: [embedDesligar] });
                            console.log(`[Alerta-Envio] Alerta enviado com sucesso!`);
                        } catch (error) {
                            console.error("[Alerta-Erro-Envio-Discord] Erro ao enviar pro Discord:", error.message);
                        }
                    }
                    else if (COMANDO === 'LIGAR') {
                        const embedLigar = {
                            title: "🔋 RELIGANDO DISPOSITIVOS",
                            description: "A produção de energia retornou e bateria está recarregando.",
                            color: 65280,
                            fields: [
                                { name: "🔌 Ação Automática", value: `\` RELIGANDO \``, inline: false },
                                { name: "📋 Categoria", value: `\`${CATEGORIA}\``, inline: false },
                                { name: "Capacidade Atual", value: `\`${CAPACIDADE}\``, inline: false },
                                { name: "Duração da Bateria", value: `\`${DURACAO}\``, inline: false }
                            ],
                            timestamp: new Date().toISOString(),
                            footer: { text: "Sistema de Monitoramento IoT" }
                        };

                        console.log(`[Alerta-Discord] Enviando alerta de LIGAR - Dispositivo ${ID_DISPOSITIVO}.`);

                        try {
                            await axios.post(DISCORD_WEBHOOK_URL, { embeds: [embedLigar] });
                            console.log(`[Alerta-Envio] Alerta enviado com sucesso!`);
                        } catch (error) {
                            console.error("[Alerta-Erro-Envio-Discord] Erro ao enviar pro Discord:", error.message);
                        }
                    }
                }
            } catch (err) {
                console.error("[Alerta-Erro] Falha ao processar mensagem do Kafka:", err.message);
            }
        },
    });
}

run().catch(console.error);