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

É **crucial** usar a flag `--recurse-submodules` para baixar também a dependência do Containernet.

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
sudo docker.io # Se houver conflito, deve haver, ignore.
```
## Execução

Após a instalação, o ambiente está pronto.

1.  Certifique-se de que seu ambiente virtual está ativo (`source venv/bin/activate`).
2.  Abra o arquivo `runner.ipynb`.
3.  Clique em select kernel, python environments, venv (Python 3.XX.X).
4.  Execute as células do notebook para iniciar as simulações. As células são autoexplicativas e permitem rodar o cenário simples ou o cenário completo com QoS dinâmico.

## Autores

*   **Adonias Junior de Albuquerque Mattos** - *Desenvolvimento e Simulação* - [MiCaptain](https://github.com/MiCaptain)
*   **Hugo Samuel Guedes de Oliveira** -
*   **Matheus Dutra Sarmento** -


## Agradecimentos

*   Agradecimentos à comunidade Mininet/Containernet por fornecer as ferramentas de simulação.
*   Aos professores Doutores Leandro Cavalcanti de Almeida e Paulo Ditarso Maciel Júnior, docentes da IFPB/ PPGTI e PPGEE respectivamente.
