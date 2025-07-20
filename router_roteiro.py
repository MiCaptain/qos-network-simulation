from mininet.net import Mininet
from mininet.node import Node
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.log import setLogLevel, info
import time
import os
import threading


# --- Caminhos Dinâmicos ---
# Obtém o caminho absoluto do diretório onde este script está localizado.
base_dir = os.path.abspath(os.path.dirname(__file__))

# Cria o diretório de logs se ele não existir.
logs_dir = os.path.join(base_dir, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Define os caminhos para os arquivos de flag e log
FLAG_PATH_C1 = os.path.join(logs_dir, "c1_latency_high.flag")
FLAG_PATH_C2 = os.path.join(logs_dir, "c2_latency_high.flag")
FLAG_PATH_LOG = os.path.join(logs_dir, "flags.txt")

class LinuxRouter(Node):
    "Nó roteador Linux com IP forwarding habilitado."
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class NetworkTopo(Topo):
    "Topologia com Roteador e switches."
    def build(self, **_opts):

        info('*** Construindo a topologia de rede...\n')
        info('*** Cliente01 -- s3 -- r3                                       ***\n')
        info('***                       -- r2 -- s2 -- r1 -- s1 -- servidor01 ***\n')
        info('*** Cliente02 -- s4 -- r4                                       ***\n')
        info('*** Cliente03 -- -- -- s5 -- -- r5 -- -- s6 -- -- -- servidor02 ***\n')

        link_opts = {'bw': 10, 'max_queue_size': 10, 'use_htb': True} 

        # Adiciona roteadores
        r1 = self.addNode('r1', cls=LinuxRouter)
        r2 = self.addNode('r2', cls=LinuxRouter)
        r3 = self.addNode('r3', cls=LinuxRouter)
        r4 = self.addNode('r4', cls=LinuxRouter)

        r5 = self.addNode('r5', cls=LinuxRouter)  # Adiciona roteador para cliente03

        # Adiciona switches
        s1 = self.addSwitch('s1')  # servidor
        s2 = self.addSwitch('s2')  # intermediário
        s3 = self.addSwitch('s3')  # cliente01
        s4 = self.addSwitch('s4')  # cliente02

        s5 = self.addSwitch('s5')  # cliente03 intermediário
        s6 = self.addSwitch('s6')  # cliente03 servidor

        # Links entre switches e roteadores
        self.addLink(s1, r1, intfName2='s1-r1', params2={'ip': '172.30.0.1/24'})
        self.addLink(r1, s2, intfName1='r1-s2', params1={'ip': '10.0.12.1/30'})
        self.addLink(s2, r2, intfName2='s2-r2', params2={'ip': '10.0.12.2/30'})
        self.addLink(r2, r3, intfName1='r2-r3', params1={'ip': '10.0.23.1/30'}, 
                             intfName2='r3-r2', params2={'ip': '10.0.23.2/30'}, **link_opts)
        self.addLink(r3, s3, intfName1='r3-s3', params1={'ip': '172.20.0.1/24'}, **link_opts)   

        self.addLink(r2, r4, intfName1='r2-r4', params1={'ip': '10.0.24.1/30'},
                             intfName2='r4-r2', params2={'ip': '10.0.24.2/30'}, **link_opts)
        self.addLink(r4, s4, intfName1='r4-s4', params1={'ip': '172.21.0.1/24'}, **link_opts)

        # Links entre cliente03 e servidor02 (servidores puros para servir de parametro)
        self.addLink(s5, r5, intfName2='s5-r5', params2={'ip': '172.22.0.1/24'}, **link_opts)
        self.addLink(r5, s6, intfName1='r5-s6', params1={'ip': '172.31.0.1/24'}, **link_opts)

        # Adiciona clientes e servidores
        cliente01 = self.addHost('cliente01',
                               ip='172.20.0.2/16',
                               defaultRoute='via 172.20.0.1',)  

        cliente02 = self.addHost('cliente02',
                                ip='172.21.0.2/16',
                                defaultRoute='via 172.21.0.1',)
        
        cliente03 = self.addHost('cliente03',
                                ip='172.22.0.2/16',
                                defaultRoute='via 172.22.0.1',)
        
        servidor01 = self.addHost('servidor01',
                                ip='172.30.0.2/16',
                                defaultRoute='via 172.30.0.1',)
        
        servidor02 = self.addHost('servidor02',
                                ip='172.31.0.2/16',
                                defaultRoute='via 172.31.0.1',)
        
        # Ligações dos hosts aos switches
        self.addLink(cliente02, s4)
        self.addLink(cliente01, s3)
        self.addLink(servidor01, s1)

        self.addLink(cliente03, s5)  # Conecta cliente03 ao switch intermediário
        self.addLink(servidor02, s6)  # Conecta servidor02 ao switch intermediário

# Adiciona a topologia ao dicionário de topos do Mininet
topos = { 'mytopo': ( lambda: NetworkTopo() ) }

def monitorar_flag(net):

    counter = 0
    priority = False
    while True:
        if os.path.exists(FLAG_PATH_C1):
            #aplicar_qos_combinado(net, 'r3', 'r3-r2', 10)
            #aplicar_qos_combinado(net, 'r3', 'r3-s3', 10)
            configurar_qos_inicial(net, 10)
            os.remove(FLAG_PATH_C1)
            counter = 0
            priority = True
            # Escreve em flag_path_log
            start = time.time()
            current_time = time.strftime("%H:%M:%S", time.localtime(start))
            with open(FLAG_PATH_LOG, "a") as f:
                f.write(f"c1_1_{current_time}\n")
        if os.path.exists(FLAG_PATH_C2):
            #aplicar_qos_combinado(net, 'r4', 'r4-r2', 10)
            #aplicar_qos_combinado(net, 'r4', 'r4-s4', 10)
            configurar_qos_inicial(net, 10)
            os.remove(FLAG_PATH_C2)
            counter = 0
            priority = True
            # Escreve em flag_path_log
            start = time.time()
            current_time = time.strftime("%H:%M:%S", time.localtime(start))
            with open(FLAG_PATH_LOG, "a") as f:
                f.write(f"c2_1_{current_time}\n")
        if counter >= 10 and priority:  # Se não houver sinalização por 10 iterações, remove as filas
            info('*** Nenhuma sinalização recebida. Removendo prioridade e aplicando largura de banda...\n')
            limitar_largura_banda_geral(net, 10)
            priority = False
            start = time.time()
            current_time = time.strftime("%H:%M:%S", time.localtime(start))
            counter = 0
            with open(FLAG_PATH_LOG, "a") as f:
                f.write(f"c1_0_{current_time}\n")
                f.write(f"c2_0_{current_time}\n")
        time.sleep(1)
        counter += 1

def aplicar_qos_combinado(net, router, intf, largura_banda):
    """
    Aplica uma política de QoS que limita a banda total e prioriza o tráfego da porta 5002.
    Esta função combina limitação de banda (HTB) e priorização (PRIO).
    """
    
    # 1. Limpa qualquer configuração antiga para começar do zero.
    net[router].cmd(f'tc qdisc del dev {intf} root 2> /dev/null || true')
    
    # 2. Cria a qdisc HTB na raiz. O tráfego por padrão vai para a classe de baixa prioridade.
    net[router].cmd(f'tc qdisc add dev {intf} root handle 1: htb default 12')
    
    # 3. Cria a classe principal que define o limite de banda total.
    net[router].cmd(f'tc class add dev {intf} parent 1: classid 1:12 htb rate {largura_banda}mbit ceil {largura_banda}mbit')
    
    # 4. Cria as classes filhas DENTRO da classe principal.
    #    Uma para o tráfego de alta prioridade (pode ter uma taxa garantida se quisermos)
    #    e outra para o tráfego padrão.
    net[router].cmd(f'tc qdisc add dev {intf} parent 1:12 handle 10: prio bands 3')

    # 5. Cria o filtro para direcionar o tráfego da porta 5002 para a classe de alta prioridade.
    net[router].cmd(f'tc filter add dev {intf} protocol ip parent 10:0 prio 1 u32 match ip dport 5002 0xffff flowid 10:1')

def aplicar_limite_largura_banda(net, router, intf, largura_banda):

    # 1. Limpa qualquer configuração antiga para começar do zero.
    net[router].cmd(f'tc qdisc del dev {intf} root 2> /dev/null || true')
    
    # 2. Cria a qdisc HTB na raiz. O tráfego por padrão vai para a classe de baixa prioridade.
    net[router].cmd(f'tc qdisc add dev {intf} root handle 1: htb default 12')
    
    # 3. Cria a classe principal que define o limite de banda total.
    net[router].cmd(f'tc class add dev {intf} parent 1: classid 1:12 htb rate {largura_banda}mbit ceil {largura_banda}mbit')

def limitar_largura_banda_geral(net, largura_banda):
    """
    Limita a largura de banda geral de toda a rede.
    Aplica uma política de QoS que limita a banda total em todos os roteadores.
    """
    info(f'*** Limitando a largura de banda geral da rede para {largura_banda}Mbps...\n')
    
    roteadores = ['r1', 'r2', 'r3', 'r4', 'r5']
    interfaces = {
        'r1': ['s1-r1', 'r1-s2'],
        'r2': ['s2-r2', 'r2-r3', 'r2-r4'],
        'r3': ['r3-r2', 'r3-s3'],
        'r4': ['r4-r2', 'r4-s4'],
        'r5': ['s5-r5', 'r5-s6']
    }
    
    for router in roteadores:
        for intf in interfaces[router]:
            aplicar_limite_largura_banda(net, router, intf, largura_banda)


def configurar_qos_inicial(net, largura_banda):
    info(f'*** Configurando QoS inicial em toda a rede...\n')
    roteadores_e_interfaces = {
        'r1': ['s1-r1', 'r1-s2'],
        'r2': ['s2-r2', 'r2-r3', 'r2-r4'],
        'r3': ['r3-r2', 'r3-s3'],
        'r4': ['r4-r2', 'r4-s4'],
        'r5': ['s5-r5', 'r5-s6']
    }
    for router, interfaces in roteadores_e_interfaces.items():
        for intf in interfaces:
            # Aqui você pode decidir qual política aplicar.
            # Por enquanto, vamos usar a que aplica QoS combinada.
            aplicar_qos_combinado(net, router, intf, largura_banda)

def remover_filas(net):
    info('*** Removendo todas as filas do roteador...\n')
    net['r1'].cmd('tc qdisc del dev s1-r1 root')
    net['r1'].cmd('tc qdisc del dev r1-s2 root')
    net['r2'].cmd('tc qdisc del dev s2-r2 root')
    net['r2'].cmd('tc qdisc del dev r2-r3 root')
    net['r2'].cmd('tc qdisc del dev r2-r4 root')
    net['r3'].cmd('tc qdisc del dev r3-r2 root')
    net['r3'].cmd('tc qdisc del dev r3-s3 root')
    net['r4'].cmd('tc qdisc del dev r4-r2 root')
    net['r4'].cmd('tc qdisc del dev r4-s4 root')
    net['r5'].cmd('tc qdisc del dev s5-r5 root')
    net['r5'].cmd('tc qdisc del dev r5-s6 root')
    interfaces = [
    's1-r1', 'r1-s2',
    's2-r2', 'r2-r3', 'r2-r4',
    'r3-r2', 'r3-s3',
    'r4-r2', 'r4-s4',
    's5-r5', 'r5-s6']
    for r in ['r1', 'r2', 'r3', 'r4', 'r5']:
        info(f'*** Removendo filas e filtros do roteador {r}...\n')
        net[r].cmd('tc qdisc del dev lo root')
        for intf in net[r].intfNames():
            if intf in interfaces:
                net[r].cmd(f'tc qdisc del dev {intf} root')
                net[r].cmd(f'tc filter del dev {intf} root')
                net[r].cmd(f'tc filter del dev {intf} ingress')
                info(f'Fila e filtros removidos de {intf}\n')
            else:
                info(f'Fila não encontrada em {intf}\n')
    info('*** Removendo filas e filtros dos switches...\n')
    for s in ['s1', 's2', 's3', 's4', 's5', 's6']:
        net[s].cmd('tc qdisc del dev lo root')
        for intf in net[s].intfNames():
            net[s].cmd(f'tc qdisc del dev {intf} root')
            net[s].cmd(f'tc filter del dev {intf} root')
            net[s].cmd(f'tc filter del dev {intf} ingress')
            info(f'Fila e filtros removidos de {intf}\n')
    for c in ['cliente01', 'cliente02', 'cliente03', 'servidor01', 'servidor02']:
        info(f'*** Removendo filas e filtros do host {c}...\n')
        net[c].cmd('tc qdisc del dev lo root')
        net[c].cmd(f'systemctl restart networking')
        for intf in net[c].intfNames():
            net[c].cmd(f'tc qdisc del dev {intf} root')
            net[c].cmd(f'tc filter del dev {intf} root')
            net[c].cmd(f'tc filter del dev {intf} ingress')
            info(f'Fila e filtros removidos de {intf}\n')

def run():
    "Executa a topologia Mininet com hosts Docker."
    # Limpa execuções anteriores do Docker se existirem
    import os
    os.system("docker stop cliente01 cliente02 cliente03 servidor01 servidor02 && docker rm cliente01 cliente02 cliente03 servidor01 servidor02")

    topo = NetworkTopo()
    net = Mininet(topo=topo, waitConnected=True)
    net.start()

    # Permite o encaminhamento de pacotes no firewall do Docker
    info('*** Alterando a política de FORWARD do iptables para ACCEPT\n')
    os.system('sudo iptables -P FORWARD ACCEPT')

    info('*** Configurando IPs do roteador manualmente...\n')
    # r1
    net['r1'].setIP('172.30.0.1/24', intf='s1-r1')      # Para servidor
    net['r1'].setIP('10.0.12.1/30', intf='r1-s2')       # Para r2

    # r2
    net['r2'].setIP('10.0.12.2/30', intf='s2-r2')       # Para r1
    net['r2'].setIP('10.0.23.1/30', intf='r2-r3')       # Para r3
    net['r2'].setIP('10.0.24.1/30', intf='r2-r4')       # Para r4

    # r3
    net['r3'].setIP('10.0.23.2/30', intf='r3-r2')       # Para r2
    net['r3'].setIP('172.20.0.1/24', intf='r3-s3')      # Para cliente01

    # r4
    net['r4'].setIP('10.0.24.2/30', intf='r4-r2')       # Para r2
    net['r4'].setIP('172.21.0.1/24', intf='r4-s4')      # Para cliente02

    # Rotas estáticas
    # r1: para rede do cliente via r2
    net['r1'].cmd('ip route add 172.20.0.0/24 via 10.0.12.2')
    net['r1'].cmd('ip route add 172.21.0.0/24 via 10.0.12.2')

    # r2: para rede do servidor via r1, para rede do cliente via r3
    net['r2'].cmd('ip route add 172.30.0.0/24 via 10.0.12.1')
    net['r2'].cmd('ip route add 172.20.0.0/24 via 10.0.23.2')
    net['r2'].cmd('ip route add 172.21.0.0/24 via 10.0.24.2')

    # r3: para rede do servidor via r2
    net['r3'].cmd('ip route add 172.30.0.0/24 via 10.0.23.1')

    # r4: para rede do servidor via r2
    net['r4'].cmd('ip route add 172.30.0.0/24 via 10.0.24.1')

    # Configuracoes do cliente03 e servidor02
    info('*** Configurando IPs do cliente03 e servidor02 (parametros)...\n')
    net['r5'].setIP('172.22.0.1/24', intf='s5-r5')
    net['r5'].setIP('172.31.0.1/24', intf='r5-s6')

    # Rotas estaticas
    net['r5'].cmd('ip route add 172.31.0.0/24 via 172.22.0.1')
    net['r5'].cmd('ip route add 172.22.0.0/24 via 172.31.0.1')


    #info('*** Tabela de rotas no roteador:\n')
    info('*** Tabela de rotas no cliente:\n')
    info(net['cliente01'].cmd('ip route show'))
    info(net['cliente02'].cmd('ip route show'))
    info(net['cliente03'].cmd('ip route show'))
    info('*** Tabela de rotas no servidor:\n')
    info(net['servidor01'].cmd('ip route show'))
    info(net['servidor02'].cmd('ip route show'))

    # Configurando o roteador para aceitar conexões TCP SYN
    info('*** Configurando o roteador para aceitar conexões TCP SYN...\n')
    net['r1'].cmd('iptables -A INPUT -p tcp --dport 5002 -j ACCEPT')
    net['r1'].cmd('iptables -A INPUT -p tcp --dport 5001 -j ACCEPT')
    net['r2'].cmd('iptables -A INPUT -p tcp --dport 5002 -j ACCEPT')
    net['r2'].cmd('iptables -A INPUT -p tcp --dport 5001 -j ACCEPT')
    net['r3'].cmd('iptables -A INPUT -p tcp --dport 5002 -j ACCEPT')
    net['r3'].cmd('iptables -A INPUT -p tcp --dport 5001 -j ACCEPT')
    net['r4'].cmd('iptables -A INPUT -p tcp --dport 5002 -j ACCEPT')
    net['r4'].cmd('iptables -A INPUT -p tcp --dport 5001 -j ACCEPT')
    net['r5'].cmd('iptables -A INPUT -p tcp --dport 5002 -j ACCEPT')
    net['r5'].cmd('iptables -A INPUT -p tcp --dport 5001 -j ACCEPT')

    # Limita a largura de banda geral dos roteadores
    info('*** Limitando a largura de banda geral dos roteadores...\n')
    limitar_largura_banda_geral(net, 10)  # Configura QoS inicial em toda a rede

    # Iniciando configuracoes .sh
    info('*** Iniciando configuração do servidor...\n')
    net['servidor01'].cmd('bash config/s01_config_sd.sh')
    net['servidor02'].cmd('bash config/s02_config_sd.sh')
    
    info('*** Iniciando socket monitorado ***\n')
    net['cliente01'].cmd('bash config/c01_socket_sd.sh')
    net['cliente02'].cmd('bash config/c02_socket_sd.sh')
    net['cliente03'].cmd('bash config/c03_socket_sd.sh')

    # Inicia o monitoramento da flag em uma thread paralela
    info('*** Iniciando monitoramento de latência URLLC...\n')
    monitor_thread = threading.Thread(target=monitorar_flag, args=(net,), daemon=True)
    monitor_thread.start()
 
    CLI(net)
    remover_filas(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()