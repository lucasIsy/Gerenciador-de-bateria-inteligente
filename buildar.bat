@echo off
set NETWORK=rede_iot

:: Verifica se a rede existe
docker network inspect %NETWORK% >nul 2>&1
if %errorlevel% neq 0 (
    echo Criando a rede %NETWORK%...
    docker network create %NETWORK%
) else (
    echo A rede %NETWORK% ja existe.
)

:: Sobe os servicos
echo Subindo os servicos...
docker compose -f docker-compose-data.yml up -d --build
docker compose -f docker-compose-monitoring.yml up -d --build
docker compose -f docker-compose-simuladores.yml up -d --build
docker compose -f docker-compose-alertas.yml up -d --build

echo Aguardando inicializacao do Kafka Connect...
timeout /t 15 /nobreak >nul

echo Todos os servicos e conectores foram iniciados!
pause