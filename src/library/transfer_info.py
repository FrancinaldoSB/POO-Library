import threading
from queue import Queue

def criarLotes(data_transfer, start, end):
    for i in range(start, end, data_transfer.batch_size):
        batch_start = i
        batch_end = min(i + data_transfer.batch_size, end)
        data_transfer.task_queue.put((batch_start, batch_end))

def tranferirinfos(data_transfer, start, end):
    criarLotes(data_transfer, start, end)
    threads = []

    for _ in range(data_transfer.num_threads):
        thread = threading.Thread(target=data_transfer.worker)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
