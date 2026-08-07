# Usa uma imagem oficial e leve do Node.js
FROM node:20-alpine

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia apenas o package.json primeiro (aproveita o cache do Docker)
COPY package*.json ./

# Instala as dependências (axios e kafkajs)
RUN npm install

# Copia o restante dos arquivos do seu projeto (o alerta.js)
COPY . .

# Comando para rodar a aplicação
CMD ["npm", "start"]