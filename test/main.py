import threading
import time
from tabulate import tabulate
import queue

# Configurações do sistema
NUM_CPUS = 4
RAM_SIZE_MB = 32 * 1024  # 32 GB em MB
QUANTUM = 4  # Unidades de tempo

# Estruturas de dados
disponibilidade_ram = RAM_SIZE_MB
fila_prontos = queue.Queue()
fila_bloqueados = queue.Queue()
tabela_memoria = {}  # Tabela para mapear processos e blocos de memória

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
    global disponibilidade_ram, tabela_memoria
    with lock:
        if disponibilidade_ram >= processo.ram:
            tabela_memoria[processo.id] = processo.ram
            disponibilidade_ram -= processo.ram
            return True
        return False

def liberar_memoria(processo):
    global disponibilidade_ram, tabela_memoria
    with lock:
        if processo.id in tabela_memoria:
            disponibilidade_ram += tabela_memoria.pop(processo.id)

# Função para exibir a tabela de memória
def exibir_tabela_memoria(processos_na_memoria):
    print("\n=== Tabela de Memória ===")
    if not processos_na_memoria:
        print("Nenhum processo está ocupando a memória.\n")
        return

    tabela = []
    for processo_id in processos_na_memoria:
        ram = tabela_memoria.get(processo_id, "Desconhecido")
        tabela.append([
            processo_id,
            ram,
        ])
    print(tabulate(tabela, headers=["ID do Processo", "Memória Ocupada (MB)"], tablefmt="fancy_grid"))
    print("\n")

# Função para leitura de processos de um arquivo
def ler_processos_de_arquivo(caminho_arquivo):
    processo_id = 1
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if not linha:
                    continue  # Ignora linhas vazias
                try:
                    cpu1, io, cpu2, ram = map(int, linha.split())
                    novo_processo = Processo(processo_id, cpu1, io, cpu2, ram)

                    if alocar_memoria(novo_processo):
                        novo_processo.estado = "Pronto"
                        fila_prontos.put(novo_processo)
                        print(f"Processo criado: {novo_processo}")
                    else:
                        print(f"Memória insuficiente para criar o processo {novo_processo.id}")

                    processo_id += 1
                    exibir_tabela_memoria(list(tabela_memoria.keys()))  # Passa os IDs dos processos na memória
                except ValueError:
                    print(f"Erro na linha '{linha}': formato inválido. Ignorando...")
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")

# Thread Despachante
def despachante():
    cpus_disponiveis = [True] * NUM_CPUS

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

def gerenciar_io():
    while True:
        if not fila_bloqueados.empty():
            processo = fila_bloqueados.get()
            time.sleep(processo.io)  # Simula o tempo necessário para concluir o I/O
            processo.io = 0
            processo.estado = "Pronto"
            fila_prontos.put(processo)
            print(f"Processo {processo.id}: de Bloqueado para Pronto após conclusão do I/O")
        time.sleep(1)  # Intervalo para evitar alto uso de CPU


def processar(processo, cpu_id, cpus_disponiveis):
    global lock

    with lock:
        # Fase 1: Execução da CPU1
        if processo.cpu1 > 0:
            tempo = min(processo.cpu1, QUANTUM)
            time.sleep(tempo)
            processo.cpu1 -= tempo

            if processo.cpu1 > 0:
                # Quantum expirado
                fila_prontos.put(processo)
                print(f"Processo {processo.id}: Quantum expirado, retornando à fila de prontos")
            else:
                print(f"Processo {processo.id}: Fase 1 de CPU concluída")

                if processo.io > 0:
                    # Bloqueia para I/O
                    processo.estado = "Bloqueado"
                    fila_bloqueados.put(processo)
                    print(f"Processo {processo.id}: de Executando para Bloqueado (I/O)")
                elif processo.cpu2 > 0:
                    processo.estado = "Pronto"
                    fila_prontos.put(processo)
                else:
                    # Processo finalizado
                    finalizar_processo(processo)

        cpus_disponiveis[cpu_id] = True


def gerenciar_io():
    while True:
        if not fila_bloqueados.empty():
            with lock:
                processo = fila_bloqueados.get()
            time.sleep(processo.io)  # Simula o tempo necessário para concluir o I/O
            processo.io = 0
            processo.estado = "Pronto"
            fila_prontos.put(processo)
            print(f"Processo {processo.id}: de Bloqueado para Pronto após conclusão do I/O")
        time.sleep(1)  # Intervalo para evitar alto uso de CPU


def finalizar_processo(processo):
    liberar_memoria(processo)
    processo.estado = "Finalizado"
    print(f"Processo {processo.id}: Finalizado e memória liberada")
    exibir_tabela_memoria(list(tabela_memoria.keys()))  # Mostra a tabela de memória após a liberação

    # Verifica se todas as filas estão vazias para encerrar o programa
    if fila_prontos.empty() and fila_bloqueados.empty():
        print("Todos os processos foram concluídos. Encerrando o programa.")
        exit(0)  # Encerra o programa


# Inicialização das threads
thread_despachante = threading.Thread(target=despachante)
thread_io = threading.Thread(target=gerenciar_io)

# Executar entrada de processos por arquivo
thread_io.start()
thread_despachante.start()
ler_processos_de_arquivo('test/processes.txt')
thread_despachante.join()
