import socket
import threading

HOST = ''
PORT = 5002

def handle_client(conn, addr):
    print(f"Conexao de {addr}", flush=True)
    with conn:
        while True:
            data = conn.recv(1)
            if not data:
                break
            conn.sendall(data)
    print(f"Conexao encerrada {addr}", flush=True)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(10)
    print("Servidor escutando na porta", PORT, flush=True)
    # Aceita conexões de forma concorrente
    # Isso permite que multiplos clientes se conectem ao mesmo tempo
    print("Aguardando conexoes...", flush=True)
    s.settimeout(10)  # Define um timeout para evitar bloqueios indefinidos
    while True:
        try:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except socket.timeout:
            continue