#!/bin/bash

echo "Cliente02 iniciando o teste de trafego com socket..."

pkill -f c2_urlcc_monitor_rtt_socket.py

python3 c2_urlcc_monitor_rtt_socket.py > logs/cliente02_5002_urlcc_socket_output.txt 2>&1 &

echo "Cliente02 iniciou o teste de trafego."