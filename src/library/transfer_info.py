import threading
from queue import Queue

def criarLotes(data_transfer, start, end):
    """
    summary
        Cria lotes de dados para transferência e os coloca na fila de tarefas.

    parameters
        data_transfer : object
            Objeto que contém o tamanho do lote (`batch_size`) e a fila de tarefas (`task_queue`).
        start : int
            Índice inicial para a criação dos lotes.
        end : int
            Índice final para a criação dos lotes.

    return
        None
    """
    for i in range(start, end, data_transfer.batch_size):
        batch_start = i  # Início do lote
        batch_end = min(i + data_transfer.batch_size, end)  # Fim do lote, respeitando o limite 'end'
        data_transfer.task_queue.put((batch_start, batch_end))  # Coloca o lote na fila de tarefas.

def tranferirinfos(data_transfer, start, end):
    """
    summary
        Inicia o processo de transferência de dados com múltiplas threads.

    parameters
        data_transfer : object
            Objeto que contém a configuração da transferência, como o número de threads e a fila de tarefas.
        start : int
            Índice inicial da transferência de dados.
        end : int
            Índice final da transferência de dados.

    return
        None
    """
    criarLotes(data_transfer, start, end)  # Cria os lotes e os coloca na fila.
    threads = []  # Lista para armazenar as threads.

    # Cria e inicia as threads
    for _ in range(data_transfer.num_threads):  # Cria o número de threads definido
        thread = threading.Thread(target=data_transfer.worker)  # Cada thread executa a função 'worker'
        threads.append(thread)  # Adiciona a thread à lista
        thread.start()  # Inicia a execução da thread

    # Aguarda todas as threads terminarem
    for thread in threads:
        thread.join()  # Espera a thread terminar sua execução