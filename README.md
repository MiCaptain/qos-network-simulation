# Projeto de Simulação de Rede com QoS Dinâmico

Este projeto utiliza Containernet para simular uma topologia de rede com múltiplos clientes e tipos de tráfego (eMBB e URLLC). Um sistema de monitoramento detecta altas latências no tráfego URLLC e aplica dinamicamente políticas de QoS (Qualidade de Serviço) nos roteadores para priorizar pacotes e garantir baixa latência.

## Requisitos

*   Git
*   Python 3.8+ e `venv`
*   Open vSwitch
*   Ansible (para instalação do Containernet)

## Instalação

Siga estes passos para configurar o ambiente de simulação.

### 1. Clonar o Repositório

Usar a flag `--recurse-submodules` para baixar também a dependência do Containernet.

```bash
git clone --recurse-submodules https://github.com/MiCaptain/qos-network-simulation.git
cd qos-network-simulation
``` 
> **Nota:** Se você já clonou o repositório sem a flag, execute `git submodule update --init --recursive` de dentro do diretório do projeto.

### 2. Configurar o Ambiente Python

Usamos um ambiente virtual para isolar as dependências do Python.

```bash

# Instalar venv
sudo apt install python3.12-venv

# Criar o ambiente virtual
python3 -m venv venv

# Ativar o ambiente
source venv/bin/activate

# Instalar os pacotes necessários
pip install -r requirements.txt
```

### 3. Instalar Dependências do Containernet e Sistema

O Containernet utiliza um script Ansible para instalar suas próprias dependências no sistema.

```bash
sudo apt install ansible-core
cd containernet/ansible
sudo ansible-playbook -i "localhost," -c local install.yml
cd ../..

# Instalar dependencias do sistema
sudo apt install mininet openvswitch-switch openvswitch-testcontroller python3-tk
sudo docker.io - Se houver conflito, deve haver, ignore.
```
## Execução

Após a instalação, o ambiente está pronto.

1.  Certifique-se de que seu ambiente virtual está ativo (`source venv/bin/activate`).
2.  Abra o arquivo `runner.ipynb`.
3.  Clique em select kernel, python environments, venv (Python 3.XX.X).
4.  Execute as células do notebook para iniciar as simulações. As células são autoexplicativas e permitem rodar o cenário simples ou o cenário completo com QoS dinâmico.
5.  A configuração inicial força uma largura de banda de 10M em todos os roteadores, então qualquer valor proximo ou acima disso deve gerar aumento significativo na latencia.
6.  cliente01 bash config/c01_config_sd.sh 172.30.0.2 30 10M 5001 - IP Duração Banda Porta

## Resultado esperado

Ao aplicar uma banda de 10M do cliente01 sentido servidor01 os roteadores ficam saturados, oque dispara uma flag monitorada, essa ação por sua vez ativa a priorização da porta 5002,
por aonde passa o trafego urllc e gera a diminuição da latencia.

![Logo Mininet](https://github.com/MiCaptain/qos-network-simulation/blob/main/latency_graph_10M_bt.png)



## Autores - Discentes do programa de Mestrado da PPGEE IFPB Campus João Pessoa

*   **Adonias Junior de Albuquerque Mattos** - *Desenvolvimento e Simulação* - [MiCaptain](https://github.com/MiCaptain)
*   **Hugo Samuel Guedes de Oliveira** -
*   **Matheus Dutra Sarmento** -


## Agradecimentos

*   Agradecimentos à comunidade Mininet/Containernet por fornecer as ferramentas de simulação.
*   Aos professores Doutores Leandro Cavalcanti de Almeida e Paulo Ditarso Maciel Júnior, docentes da IFPB/ PPGTI e PPGEE respectivamente.
