from mininet.net import Mininet
from mininet.node import Node
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.log import setLogLevel, info
import time
import os
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--tempo_ex', type=int, default=30, help='Valor para tempo_ex')
parser.add_argument('--bd', type=str, default='10G', help='Valor para bandwidth')
args = parser.parse_args()

duracao_blocos = args.tempo_ex
bandwidth = args.bd

base_dir = f'/home/micaptain/Desktop/_projeto_final'

# Cria o diretorio logs
if not os.path.exists(f'{base_dir}/logs'):
    os.makedirs(f'{base_dir}/logs')

FLAG_PATH_C1 = f"{base_dir}/logs/c1_latency_high.flag"
FLAG_PATH_C2 = f"{base_dir}/logs/c2_latency_high.flag"
FLAG_PATH_LOG = f"{base_dir}/logs/flags.txt"

class LinuxRouter(Node):
    "Nó roteador Linux com IP forwarding habilitado."
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class NetworkTopo(Topo):
    "Topologia com Roteador e Contêineres Docker."
    def build(self, **_opts):

        info('*** Construindo a topologia de rede...\n')
        info('*** Cliente01 -- s3 -- r3                                       ***\n')
        info('***                       -- r2 -- s2 -- r1 -- s1 -- servidor01 ***\n')
        info('*** Cliente02 -- s4 -- r4                                       ***\n')
        info('*** Cliente03 -- -- -- s5 -- -- r5 -- -- s6 -- -- -- servidor02 ***\n')
        # Adiciona roteadores

        link_opts = {'bw': 10, 'max_queue_size': 10, 'use_htb': True} 
        r5 = self.addNode('r5', cls=LinuxRouter)  # Adiciona roteador para cliente03

        # Adiciona switches

        s5 = self.addSwitch('s5')  # cliente03 intermediário
        s6 = self.addSwitch('s6')  # cliente03 servidor

        # Links entre switches e roteadores

        # Links entre cliente03 e servidor02 (servidores puros para servir de parametro)
        self.addLink(s5, r5, intfName2='s5-r5', params2={'ip': '172.22.0.1/24'}, **link_opts)
        self.addLink(r5, s6, intfName1='r5-s6', params1={'ip': '172.31.0.1/24'}, **link_opts)

        # Adiciona os contêineres Docker como hosts do Mininet
        # O Mininet irá gerenciar a conexão de rede deles
        # Define o diretório do projeto para mapear para dentro do contêiner
        project_dir = f'{base_dir}'

        # Adiciona os contêineres Docker, mapeando o diretório do projeto
        
        cliente03 = self.addHost('cliente03',
                                #cls=Docker,
                                #dimage="my-net-image",
                                ip='172.22.0.2/16',
                                defaultRoute='via 172.22.0.1',
                                #volumes=[f"{project_dir}:/mnt:rw"]
        )
        
        servidor02 = self.addHost('servidor02',
                                #cls=Docker,
                                #dimage="my-net-image",
                                ip='172.31.0.2/16',
                                defaultRoute='via 172.31.0.1',
                                #volumes=[f"{project_dir}:/mnt:rw"]
                                )
        
        # Conecta os hosts/contêineres aos switches
        # Ligações dos hosts aos switches

        self.addLink(cliente03, s5)  # Conecta cliente03 ao switch intermediário
        self.addLink(servidor02, s6)  # Conecta servidor02 ao switch intermediário

# Adiciona a topologia ao dicionário de topos do Mininet
topos = { 'mytopo': ( lambda: NetworkTopo() ) }

def priorizar_5002(net, cliente=3):
    info(f'*** Priorizando filas para percurso do cliente0{cliente}...\n')
    r5_inter = ['s5-r5', 'r5-s6']
    for intf in r5_inter:
        net['r5'].cmd(f'tc qdisc del dev {intf} root')
        net['r5'].cmd(f'tc qdisc add dev {intf} root handle 1: prio')
        net['r5'].cmd(f'tc filter add dev {intf} protocol ip parent 1:0 prio 1 u32 match ip dport 5002 0xffff flowid 1:1')
        net['r5'].cmd(f'tc qdisc show dev {intf}')
        net['r5'].cmd(f'tc filter show dev {intf}')

def priorizar_pkt_len(net, cliente=3):
    info(f'*** Priorizando pacotes pequenos ao cliente0{cliente}...\n')
    r5_inter = ['s5-r5', 'r5-s6']
    for intf in r5_inter:
        net['r5'].cmd(f'tc filter add dev {intf} protocol ip parent 1:0 prio 3 u32 match ip len 0 0x00ff flowid 1:3')
        net['r5'].cmd(f'tc qdisc show dev {intf}')
        net['r5'].cmd(f'tc filter show dev {intf}')

def direcionar_5001(net, cliente=3):
    info(f'*** redirecionado trafego da porta 5001 para baixa prioridade cliente0{cliente}...\n')
    r5_inter = ['s5-r5', 'r5-s6']
    for intf in r5_inter:
        net['r5'].cmd(f'tc filter add dev {intf} protocol ip parent 1:0 prio 4 u32 match ip dport 5001 0xffff flowid 1:3')
        net['r5'].cmd(f'tc qdisc show dev {intf}')
        net['r5'].cmd(f'tc filter show dev {intf}')

def remover_filas(net):
    info('*** Removendo todas as filas do roteador...\n')
    r5_inter = ['s5-r5', 'r5-s6']
    for intf in r5_inter:   
        net['r5'].cmd(f'tc qdisc del dev {intf} root')

def run():
    "Executa a topologia Mininet com hosts Docker."
    # Limpa execuções anteriores do Docker se existirem
    # net.stop() em um try/finally seria mais robusto, mas isso funciona.
    import os
    os.system("docker stop cliente01 cliente02 cliente03 servidor01 && docker rm cliente01 cliente02 cliente03 servidor01 servidor02")

    topo = NetworkTopo()
    net = Mininet(topo=topo, waitConnected=True)
    net.start()

    # Permite o encaminhamento de pacotes no firewall do Docker
    info('*** Alterando a política de FORWARD do iptables para ACCEPT\n')
    os.system('sudo iptables -P FORWARD ACCEPT')

    info('*** Configurando IPs do roteador manualmente...\n')
    # Configuracoes do cliente03 e servidor02
    info('*** Configurando IPs do cliente03 e servidor02 (parametros)...\n')
    net['r5'].setIP('172.22.0.1/24', intf='s5-r5')
    net['r5'].setIP('172.31.0.1/24', intf='r5-s6')

    # Rotas estaticas
    net['r5'].cmd('ip route add 172.31.0.0/24 via 172.22.0.1')
    net['r5'].cmd('ip route add 172.22.0.0/24 via 172.31.0.1')


    #info('*** Tabela de rotas no roteador:\n')
    #info(net['r1'].cmd('ip route show'))
    info('*** Tabela de rotas no cliente:\n')
    info(net['cliente03'].cmd('ip route show'))
    info('*** Tabela de rotas no servidor:\n')
    info(net['servidor02'].cmd('ip route show'))

    # Configurando o roteador para aceitar conexões TCP SYN
    info('*** Configurando o roteador para aceitar conexões TCP SYN...\n')
    net['r5'].cmd('iptables -A INPUT -p tcp --dport 5002 -j ACCEPT')
    net['r5'].cmd('iptables -A INPUT -p tcp --dport 5001 -j ACCEPT')


    # Iniciando configuracoes .sh
    info('*** Iniciando configuração do servidor...\n')
    #net['servidor02'].cmd('bash /mnt/config/s02_config.sh')

    info('*** Iniciando trafego de fundo dos clientes...\n')
    #net['cliente01'].cmd('bash /mnt/config/c01_config.sh') # cliente01 bash /mnt/config/c01_config.sh
    #net['cliente02'].cmd('bash /mnt/config/c02_config.sh')
    #net['cliente03'].cmd('bash /mnt/config/c03_config.sh')  # Inicia o cliente03 com o script de configuração


    info('*** Iniciando monitoramento com socket ***\n')
    #net['cliente03'].cmd('bash /mnt/config/c03_socket.sh')  # Inicia o monitoramento do cliente03
    
    # Bandwidth para o iperf vem pelo arg
    # duracao_blocos vem pelo arg
    duration = f'{duracao_blocos}'  # Duração do teste em segundos
    tempo_ex = duracao_blocos  # segundos

    '''
    info('*** Iniciando o experimento...\n')
    
    info(f'*** {tempo_ex} segundos apenas socket. \n')
    time.sleep(tempo_ex)  # Espera o tempo de monitoramento

    info(f'*** Iniciando iperf porta 5001 no cliente03 por {tempo_ex} segundos.\n')
    net['cliente03'].cmd(f'bash /mnt/config/c03_config.sh 172.31.0.2 {duration} {bandwidth}')
    time.sleep(tempo_ex)

    info(f'*** Priorizando cliente03 na porta 5002 por {tempo_ex} segundos. (sem iperf)\n')
    priorizar_5002(net, 3)  # Prioriza o cliente03
    time.sleep(tempo_ex)

    info(f'*** Iniciando iperf porta 5001 no cliente03 por {tempo_ex} segundos.\n')
    net['cliente03'].cmd(f'bash /mnt/config/c03_config.sh 172.31.0.2 {duration} {bandwidth}')
    time.sleep(tempo_ex)

    info(f'*** Removendo filas e testando por {tempo_ex} segundos.\n')
    remover_filas(net)  # Remove as filas do roteador
    time.sleep(tempo_ex)
    '''
    
    

    info('*** Removendo filas do roteador e encerrando o experimento...\n')
    CLI(net)  # Ativa a interface de linha de comando do Mininet
    remover_filas(net)  # Chama a função para remover filas
    net.stop()  # Para a rede Mininet



if __name__ == '__main__':
    setLogLevel('info')
    run()