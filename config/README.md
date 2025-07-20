# Background Traffic Scripts for Network Performance Testing

This directory contains scripts to generate background traffic using `iperf`, a tool for measuring network bandwidth.

## Overview

The `start_iperf_server.sh` script sets up an `iperf` server that listens for incoming connections from clients. This allows you to measure the bandwidth between the server and any connected clients.

The `start_iperf_client.sh` script connects to the `iperf` server and initiates a bandwidth test. This can be used to simulate network traffic and evaluate the performance of your network setup.

## Usage

1. **Starting the iperf Server:**
   - Run the `start_iperf_server.sh` script on the server container to start the `iperf` server.
   - Example command:
     ```bash
     ./start_iperf_server.sh
     ```

2. **Starting the iperf Client:**
   - Run the `start_iperf_client.sh` script on the client container to connect to the `iperf` server and start the test.
   - Example command:
     ```bash
     ./start_iperf_client.sh
     ```

## Requirements

- Ensure that `iperf` is installed on both the server and client containers.
- The server must be reachable from the client container over the network.

## Notes

- Adjust the parameters in the client script as needed to customize the bandwidth test (e.g., duration, bandwidth).
- Monitor the output of the `iperf` server to analyze the performance metrics during the test.

## Autores

*   **Adonias Junior de ALbuquerque Mattos** -
*   **Hugo Samuel Guedes de Oliveira** -
*   **Matheus Dutra Sarmento** -
*Desenvolvimento e Simulação* - [Link para seu GitHub](https://github.com/MiCaptain)

## Agradecimentos

*   Agradecimentos à comunidade Mininet/Containernet por fornecer as ferramentas de simulação.
*   Aos professores Doutores Leandro Cavalcanti de Almeida e Paulo Ditarso Maciel Júnior, docentes da PPGTI e PPGEE respectivamente.