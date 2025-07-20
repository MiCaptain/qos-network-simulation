#!/bin/bash
# filepath: /_projeto_final/config/s01_config_sem_docker.sh

echo "Iniciando o servidor iperf e o servidor TCP simples (sem Docker)..."

# Garante que não há instâncias antigas rodando
pkill -f simple_tcp_server.py
pkill -f s01_tcp_server_5002_echo.py
pkill -f iperf

# Inicia o servidor TCP simples e salva o log
python3 s01_tcp_server_5002_echo.py > logs/server01_5002_tcp_output.txt 2>&1 &

# Inicia o servidor iperf e salva o log
iperf -s & #> logs/server01_5001_iperf_output.txt 2>&1 &

echo "Servidor iperf e servidor TCP simples iniciados (sem Docker)."