#!/bin/bash

# Inicia o cliente iperf e conecta ao servidor iperf
# Substitua <SERVER_IP> pelo endereço IP do servidor iperf
SERVER_IP="${1:-172.30.0.2}"
DURATION="${2:-100}"  # Se não passar, usa 100
BANDWIDTH="${3:-100M}"  # Se não passar, usa 100M
PORT="${4:-5001}"  # Se não passar, usa 5001

pkill -f "iperf -c $SERVER_IP -p $PORT" 2>/dev/null

echo "Iniciando trafego de fundo no cliente 01 para $SERVER_IP, porta $PORT, duracao $DURATION segundos, banda $BANDWIDTH..."

iperf -c $SERVER_IP -p $PORT -t $DURATION -b $BANDWIDTH -i 1 -u > logs/cliente01_${PORT}_iperf_bt.txt &

# Exemplo de uso:

#cliente0x bash config/c01_config_sd.sh 172.30.0.2 100 100M 5001
#ou 
#cliente0x bash config/c01_config_sd.sh
