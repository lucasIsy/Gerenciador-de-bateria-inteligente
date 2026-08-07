.PHONY: setup up down build

# Nome da rede compartilhada
NETWORK_NAME = rede_iot

# Comando padrão que prepara a rede e sobe tudo
up: setup
	docker compose -f docker-compose-data.yml up -d --build
	docker compose -f docker-compose-monitoring.yml up -d --build
	docker compose -f docker-compose-simuladores.yml up -d --build
	docker compose -f docker-compose-alertas.yml up -d --build

# Cria a rede automaticamente apenas se ela NÃO existir
setup:
	@docker network inspect $(NETWORK_NAME) >/dev/null 2>&1 || \
		(echo "Criando a rede $(NETWORK_NAME)..." && docker network create $(NETWORK_NAME))

# Para e remove todos os servicos de todos os arquivos
down:
	docker compose -f docker-compose-simuladores.yml down
	docker compose -f docker-compose-data.yml down
	docker compose -f docker-compose-monitoring.yml down
	docker compose -f docker-compose-alertas.yml down