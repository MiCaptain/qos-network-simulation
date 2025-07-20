import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import time

c1_urlcc_log_file = 'logs/cliente01_5002_urlcc_socket_output.txt'
c2_urlcc_log_file = 'logs/cliente02_5002_urlcc_socket_output.txt'
c3_urlcc_log_file = 'logs/cliente03_5002_urlcc_socket_output.txt'
FLAGS_LOG_FILE = 'logs/flags.txt'

def parse_time(timestr):
    # Ajuste o formato conforme o seu log (ex: "%H:%M:%S")
    try:
        return datetime.strptime(timestr, "%H:%M:%S")
    except Exception:
        return None

def read_latencies(LOG_FILE):
    times = []
    latencies = []
    try:
        with open(LOG_FILE) as f:
            for line in f:
                parts = line.strip().split('_')
                if len(parts) == 2:
                    t = parse_time(parts[0])
                    if t is not None:
                        times.append(t)
                        try:
                            latencies.append(float(parts[1]))
                        except ValueError:
                            latencies.append(None)
    except FileNotFoundError:
        pass
    return times, latencies

def read_flags():
    flags = []
    try:
        with open(FLAGS_LOG_FILE) as f:
            for line in f:
                parts = line.strip().split('_')
                if len(parts) == 3:
                    client = parts[0]
                    sig = int(parts[1])
                    t = parse_time(parts[2])
                    if t is not None:
                        flags.append((client, sig, t))
    except FileNotFoundError:
        pass
    return flags




# ... (código existente, incluindo as funções read_latencies e read_flags) ...

fig, ax = plt.subplots(figsize=(15, 8)) # Aumenta o tamanho da figura para melhor visualização
ax.set_xlabel('Tempo')
ax.set_ylabel('Latência (ms)')
ax.set_title('Latência dos Clientes e Ativação de QoS')

def update(frame):
    # 1. Lê todos os dados brutos primeiro
    c1_times, c1_latencies = read_latencies(c1_urlcc_log_file)
    c2_times, c2_latencies = read_latencies(c2_urlcc_log_file)
    c3_times, c3_latencies = read_latencies(c3_urlcc_log_file)
    flags = read_flags()

    ax.clear()

    # 2. Encontra o tempo máximo geral para criar uma janela de tempo unificada
    all_times = c1_times + c2_times + c3_times
    if not all_times:
        # Se não houver dados, não faz nada
        return

    t_max_overall = max(all_times)
    time_window = 60  # segundos
    t_min_window = t_max_overall - timedelta(seconds=time_window)

    # 3. Filtra os dados de latência de cada cliente usando a janela unificada
    def filter_by_window(times, latencies):
        filtered_t, filtered_l = [], []
        for t, lat in zip(times, latencies):
            if t >= t_min_window:
                filtered_t.append(t)
                filtered_l.append(lat)
        return filtered_t, filtered_l

    c1_filtered_times, c1_filtered_latencies = filter_by_window(c1_times, c1_latencies)
    c2_filtered_times, c2_filtered_latencies = filter_by_window(c2_times, c2_latencies)
    c3_filtered_times, c3_filtered_latencies = filter_by_window(c3_times, c3_latencies)

    # Plota os dados de latência filtrados
    ax.plot(c1_filtered_times, c1_filtered_latencies, 'b.-', label='Cliente 01 (URLLC)')
    ax.plot(c2_filtered_times, c2_filtered_latencies, 'r.-', label='Cliente 02 (URLLC)')
    ax.plot(c3_filtered_times, c3_filtered_latencies, 'g.-', label='Cliente 03 (Referencia)')

    # 4. Processa as flags para criar os períodos de ativação
    flag_periods_c1 = []
    flag_periods_c2 = []
    current_flag_c1_start = None
    current_flag_c2_start = None

    for client, sig, t in sorted(flags, key=lambda x: x[2]):
        if client == 'c1':
            if sig == 1 and current_flag_c1_start is None:
                current_flag_c1_start = t
            elif sig == 0 and current_flag_c1_start is not None:
                flag_periods_c1.append((current_flag_c1_start, t))
                current_flag_c1_start = None
        elif client == 'c2':
            if sig == 1 and current_flag_c2_start is None:
                current_flag_c2_start = t
            elif sig == 0 and current_flag_c2_start is not None:
                flag_periods_c2.append((current_flag_c2_start, t))
                current_flag_c2_start = None

    # Se uma flag foi ativada e não desativada, estende até o final da janela
    if current_flag_c1_start is not None:
        flag_periods_c1.append((current_flag_c1_start, t_max_overall))
    if current_flag_c2_start is not None:
        flag_periods_c2.append((current_flag_c2_start, t_max_overall))

    # 5. Desenha os períodos de ativação no gráfico, clipando para a janela de visualização
    # Usamos um dicionário para garantir que a legenda apareça apenas uma vez
    legend_drawn = {}
    for start, end in flag_periods_c1:
        # Ignora períodos que terminam antes da janela começar ou começam depois que ela termina
        if end < t_min_window or start > t_max_overall:
            continue
        
        # Clipa o início e o fim do período para a janela de visualização
        visible_start = max(start, t_min_window)
        visible_end = min(end, t_max_overall)

        label = 'QoS C1 Ativo' if 'qos_c1' not in legend_drawn else ""
        ax.axvspan(visible_start, visible_end, color='yellow', alpha=0.3, label=label)
        if label: legend_drawn['qos_c1'] = True
        
    for start, end in flag_periods_c2:
        # Ignora períodos que terminam antes da janela começar ou começam depois que ela termina
        if end < t_min_window or start > t_max_overall:
            continue

        # Clipa o início e o fim do período para a janela de visualização
        visible_start = max(start, t_min_window)
        visible_end = min(end, t_max_overall)

        label = 'QoS C2 Ativo' if 'qos_c2' not in legend_drawn else ""
        ax.axvspan(visible_start, visible_end, color='cyan', alpha=0.3, label=label)
        if label: legend_drawn['qos_c2'] = True


    # --- Configurações Finais do Gráfico ---
    ax.axhline(y=5, color='k', linestyle='--', label='Limite Latência (5ms)')
    ax.set_xlabel('Tempo')
    ax.set_ylabel('Latência (ms)')
    ax.set_title('Latência dos Clientes e Ativação de QoS')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()
    
    all_latencies = c1_filtered_latencies + c2_filtered_latencies + c3_filtered_latencies
    valid_latencies = [v for v in all_latencies if v is not None]
    if valid_latencies:
        ax.set_ylim(0, max(valid_latencies) * 1.1)
    else:
        ax.set_ylim(0, 10) # Padrão se não houver dados
        
    ax.legend(loc='upper left')
    plt.savefig('latency_graph_clis.png', dpi=300, bbox_inches='tight')
    time.sleep(1)

ani = animation.FuncAnimation(fig, update, interval=1000)

plt.tight_layout()
plt.show()