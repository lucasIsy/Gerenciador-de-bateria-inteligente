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

async function run() {
    await consumer.connect();
    // Não ler alertas anteriores em caso de falha ou retry - evitar desligamentos indesejados
    await consumer.subscribe({ topic: 'comandos_mqtt_iot', fromBeginning: false });

    console.log(`[Alerta-Comandos] Escutando alertas no Kafka (${KAFKA_BROKER})`);

    await consumer.run({
        eachMessage: async ({ message }) => {
            // Lê o JSON do Kafka
            const payload = JSON.parse(message.value.toString());

            const { ID_DISPOSITIVO, CATEGORIA, COMANDO } = payload;

            if (COMANDO === 'DESLIGAR') {
                const embedDesligar = {
                    title: "⚠️ ALERTA DE BATERIA CRÍTICA",
                    description: "O nível de bateria atingiu um estado crítico e uma ação preventiva foi tomada.",
                    color: 16711680, // Código decimal para a cor Vermelha (0xFF0000)
                    fields: [
                        { name: "📱 Dispositivo", value: `\`${ID_DISPOSITIVO}\``, inline: true },
                        { name: "📋 Categoria", value: `\`${CATEGORIA}\``, inline: true },
                        { name: "🔌 Ação Automática", value: "🚨 **DESLIGADO**", inline: false }
                    ],
                    timestamp: new Date().toISOString(), // Adiciona a hora no rodape
                    footer: { text: "Sistema de Monitoramento IoT" }
                };

                console.log(`[Alerta-Discord] Enviando alerta do dispositivo ${ID_DISPOSITIVO} (${CATEGORIA}) para o Discord.`);

                try {
                    await axios.post(DISCORD_WEBHOOK_URL, { embeds: [embedDesligar] });
                    console.log(`[Alerta-Envio] Alerta enviado com sucesso!`);
                } catch (error) {
                    console.error("[Alerta-Erro-Envio-Discord] Erro ao enviar pro Discord:", error.message);
                }
            }
            else if (COMANDO === 'LIGAR') {
                const embedLigar = {
                    title: "🔋 EQUIPAMENTOS RELIGANDO",
                    description: "O sistema estabilizou e a energia foi restaurada.",
                    color: 65280,
                    fields: [
                        { name: "📱 Dispositivo", value: `\`${ID_DISPOSITIVO}\``, inline: true },
                        { name: "📋 Categoria", value: `\`${CATEGORIA}\``, inline: true },
                        { name: "🔌 Ação Automática", value: "✅ **LIGADO**", inline: false }
                    ],
                    timestamp: new Date().toISOString(),
                    footer: { text: "Sistema de Monitoramento IoT" }
                };

                console.log(`[Alerta-Discord] Enviando alerta do dispositivo ${ID_DISPOSITIVO} (${CATEGORIA}) para o Discord...`);

                try {
                    await axios.post(DISCORD_WEBHOOK_URL, { embeds: [embedLigar] });
                    console.log(`[Alerta-Envio] Alerta enviado com sucesso!`);
                } catch (error) {
                    console.error("[Alerta-Erro-Envio-Discord] Erro ao enviar pro Discord:", error.message);
                }
            }
        },
    });
}
run().catch(console.error);