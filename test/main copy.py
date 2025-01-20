import threading
import time
import queue
import random

# Configurações do sistema
NUM_CPUS = 4
RAM_SIZE_MB = 32 * 1024  # 32 GB em MB
QUANTUM = 4  # Unidades de tempo

# Estruturas de dados
disponibilidade_ram = RAM_SIZE_MB
fila_prontos = queue.Queue()
fila_bloqueados = queue.Queue()
fila_prontos_aux = queue.Queue()

# Lock para controle de acesso a recursos compartilhados
lock = threading.Lock()

class Processo:
    def __init__(self, id_processo, cpu1, io, cpu2, ram):
        self.id = id_processo
        self.cpu1 = cpu1
        self.io = io
        self.cpu2 = cpu2
        self.ram = ram
        self.estado = "Novo"

    def __str__(self):
        return f"[ID: {self.id}, CPU1: {self.cpu1}, IO: {self.io}, CPU2: {self.cpu2}, RAM: {self.ram}MB]"

# Função para gerenciamento de memória
def alocar_memoria(processo):
    global disponibilidade_ram
    with lock:
        if disponibilidade_ram >= processo.ram:
            disponibilidade_ram -= processo.ram
            return True
        return False

def liberar_memoria(processo):
    global disponibilidade_ram
    with lock:
        disponibilidade_ram += processo.ram

# Thread Geradora de Processos
def geradora_processos():
    processo_id = 1
    while processo_id <= 50:  # Limite de 50 processos
        cpu1 = random.randint(1, 10)
        io = random.randint(0, 5)
        cpu2 = random.randint(0, 10) if io > 0 else 0
        ram = random.randint(256, 2048)  # RAM entre 256MB e 2GB

        novo_processo = Processo(processo_id, cpu1, io, cpu2, ram)
        if alocar_memoria(novo_processo):
            novo_processo.estado = "Pronto"
            fila_prontos.put(novo_processo)
            print(f"Processo criado: {novo_processo}")
        else:
            print(f"Memória insuficiente para criar o processo {novo_processo.id}")

        processo_id += 1
        time.sleep(random.uniform(0.5, 2))  # Simula tempo variável de chegada de processos

# Thread Despachante
def despachante():
    cpus_disponiveis = [True] * NUM_CPUS  # Status das CPUs

    while True:
        if not fila_prontos.empty():
            processo = fila_prontos.get()
            processo.estado = "Executando"
            print(f"Processo {processo.id}: de Pronto para Executando")

            for i in range(NUM_CPUS):
                if cpus_disponiveis[i]:
                    cpus_disponiveis[i] = False
                    executar_processo(processo, i, cpus_disponiveis)
                    break

        time.sleep(1)

def executar_processo(processo, cpu_id, cpus_disponiveis):
    threading.Thread(target=processar, args=(processo, cpu_id, cpus_disponiveis)).start()

def processar(processo, cpu_id, cpus_disponiveis):
    # Simula a execução de CPU fase 1
    if processo.cpu1 > 0:
        tempo = min(processo.cpu1, QUANTUM)
        time.sleep(tempo)
        processo.cpu1 -= tempo

        if processo.cpu1 > 0:
            fila_prontos.put(processo)
            print(f"Processo {processo.id}: Quantum expirado, retornando à fila de prontos")
        else:
            print(f"Processo {processo.id}: Fase 1 de CPU concluída")

            if processo.io > 0:
                processo.estado = "Bloqueado"
                fila_bloqueados.put(processo)
                print(f"Processo {processo.id}: de Executando para Bloqueado (I/O)")
            elif processo.cpu2 > 0:
                processo.estado = "Pronto"
                fila_prontos_aux.put(processo)
            else:
                finalizar_processo(processo)

    cpus_disponiveis[cpu_id] = True

def finalizar_processo(processo):
    liberar_memoria(processo)
    processo.estado = "Finalizado"
    print(f"Processo {processo.id}: Finalizado e memória liberada")

# Inicialização das threads
thread_geradora = threading.Thread(target=geradora_processos)
thread_despachante = threading.Thread(target=despachante)

thread_geradora.start()
thread_despachante.start()

thread_geradora.join()
thread_despachante.join()