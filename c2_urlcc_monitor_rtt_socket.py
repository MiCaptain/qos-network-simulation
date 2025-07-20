import socket
import time
import os

DEST_IP = "172.30.0.2"
DEST_PORT = 5002
INTERVAL = 1
FLAG_PATH = "logs/c2_latency_high.flag"
RECONNECT_DELAY = 5 # Segundos para esperar antes de tentar reconectar
THRESHOLD = 5 # ms
LIMITER = 15 # ms
tempo_de_amortizacao_0 = 10
tempo_de_amortizacao = 0

# Loop principal para garantir que o script continue tentando para sempre
while True:
    s = None # Garante que 's' exista para o bloco finally
    try:
        # --- 1. Tenta estabelecer a conexão ---
        print(f"Tentando conectar a {DEST_IP}:{DEST_PORT}...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # --- Parâmetros de Controle ---
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, 0xb8)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
        # ------------------------------------

        s.settimeout(10) # Timeout para a conexão inicial
        s.connect((DEST_IP, DEST_PORT))
        print("Conectado com sucesso. Iniciando monitoramento.")
        s.settimeout(5) # Timeout mais curto para as operações de send/recv

        # --- 2. Loop de comunicação enquanto conectado ---
        while True:
            start = time.time()
            s.sendall(b'x')
            resp = s.recv(1)
            if not resp: # Conexão fechada pelo outro lado
                print("Conexão fechada pelo servidor. Reconectando...")
                break
            
            latency = (time.time() - start) * 1000
            current_time = time.strftime("%H:%M:%S", time.localtime(start))
            
            # --- 3. Verifica se a latência está acima do limite ---
            if latency > LIMITER:
                latency = LIMITER
            print(f"{current_time}_{latency:.3f}", flush=True)
            if latency > THRESHOLD and tempo_de_amortizacao >= tempo_de_amortizacao_0:
                tempo_de_amortizacao = 0
                with open(FLAG_PATH, "w") as f:
                    f.write(f"latency_high {latency:.3f} ms\n")
            tempo_de_amortizacao += INTERVAL
            time.sleep(INTERVAL)

    except (socket.timeout, ConnectionRefusedError, ConnectionResetError, BrokenPipeError) as e:
        # --- 3. Lida com erros de conexão ou comunicação ---
        print(f"Erro: {e}. Tentando reconectar em {RECONNECT_DELAY} segundos...")
    
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
        break # Sai do loop principal se o usuário pressionar Ctrl+C

    finally:
        # --- 4. Garante que o socket seja fechado antes de tentar de novo ---
        if s:
            s.close()
        time.sleep(RECONNECT_DELAY)