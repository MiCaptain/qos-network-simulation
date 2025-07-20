#!/bin/bash

echo "Cliente01 iniciando o teste de trafego com socket..."

pkill -f c1_urlcc_monitor_rtt_socket.py

python3 c1_urlcc_monitor_rtt_socket.py > logs/cliente01_5002_urlcc_socket_output.txt 2>&1 &

echo "Cliente01 iniciou o teste de trafego."