# Scripts de Configuração de Clientes

Este diretório contém scripts shell auxiliares que são executados pelos nós clientes dentro da simulação do Containernet.

## Visão Geral

Cada script (`cXX_config_sd.sh`) é responsável por iniciar um cliente `iperf` para gerar tráfego de fundo (eMBB) em direção a um servidor na rede.

Esses scripts **não são feitos para serem executados manualmente**. Eles são chamados pelo script de simulação principal (`router_roteiro.py`) no momento apropriado.

## Scripts e Parâmetros

O principal script de cliente é o `cXX_config_sd.sh`. Ele aceita os seguintes parâmetros:

1.  `IP_DO_SERVIDOR`: O endereço IP do servidor `iperf` de destino.
2.  `DURACAO`: O tempo em segundos que o teste de tráfego deve durar.
3.  `LARGURA_BANDA`: A largura de banda a ser gerada (ex: `100M` para 100 Mbits/s).
4.  `PORTA`: A porta na qual o servidor `iperf` está escutando.

### Exemplo de Uso (dentro da simulação)

A simulação principal invoca este script da seguinte forma:

```bash
# Exemplo de como o cliente03 é instruído a iniciar o tráfego
cliente03 bash config/c03_config_sd.sh 172.31.0.2 600 100M 5001
```

## Requisitos

-   O `iperf` deve estar instalado na imagem base dos nós (o que já é o caso nos hosts padrão do Mininet).
-   Um servidor `iperf` deve estar em execução no IP e porta de destino para que o cliente possa se conectar.