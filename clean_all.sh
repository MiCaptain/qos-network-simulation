#!/bin/bash
set -x

# Obtém o diretório onde o script está localizado.
# Isso torna o script portátil.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "--- Limpeza Agressiva do Ambiente Mininet/Containernet ---"

echo "1. Parando e removendo todos os containers Docker..."
# O 2>/dev/null suprime erros se não houver containers para parar/remover.
if [ -x "$(command -v docker)" ]; then
    docker stop $(docker ps -aq) 2>/dev/null
    docker rm -f $(docker ps -aq) 2>/dev/null
    docker network prune -f 2>/dev/null
fi

echo "2. Executando a limpeza padrão do Mininet..."
# mn -c é a ferramenta principal para limpar links, switches e processos.
mn -c

echo "3. Matando processos restantes (garantia)..."
pkill -f mininet
pkill -f mnexec
pkill -f ovs-vswitchd
pkill -f ovsdb-server
pkill -f controller
pkill -f ryu-manager

echo "4. Removendo arquivos e diretórios gerados..."
# Usa o caminho relativo ao script para remover a pasta de logs.
rm -rf "$SCRIPT_DIR/logs"
rm -rf /tmp/*mn*
# Limpa os arquivos de estado do Open vSwitch.
rm -f /var/run/openvswitch/*.pid
rm -f /var/run/openvswitch/*.log

echo "5. Reiniciando o serviço Open vSwitch..."
systemctl restart openvswitch-switch

echo "Pronto! Ambiente limpo para nova execução."