#!/bin/bash

echo "Cliente03 iniciando o teste de trafego com socket..."

pkill -f c3_urlcc_monitor_rtt_socket.py

python3 c3_urlcc_monitor_rtt_socket.py > logs/cliente03_5002_urlcc_socket_output.txt 2>&1 &

echo "Cliente03 iniciou o teste de trafego."