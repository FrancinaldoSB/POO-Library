import redis  
import redis.exceptions  
from time import sleep  
import os  
import threading  
from queue import Queue  

class RedisConnector:
    def __init__(self):
        self.redis_host = os.getenv('HOST_TO_REDIS', 'localhost')
        self.db_redis = self.connect_to_redis()

    def connect_to_redis(self):
        while True:
            try:
                db_redis = redis.Redis(
                    host=self.redis_host, port=6379, decode_responses=True
                )
                print("Conexão estabelecida com Redis")
                return db_redis
            except redis.exceptions.ConnectionError:
                print("Erro ao conectar ao Redis, tentando novamente...")
                sleep(2)

class RedisPopulator:
    def __init__(self, redis_conn, num_threads=2, batch_size=10000):
        self.redis_conn = redis_conn
        self.num_threads = num_threads
        self.batch_size = batch_size
        self.task_queue = Queue()

    def create_batches(self, start, end):
        for i in range(start, end, self.batch_size):
            batch_start = i
            batch_end = min(i + self.batch_size, end)
            self.task_queue.put((batch_start, batch_end))

    def populate_batch(self, batch_start, batch_end):
        for i in range(batch_start, batch_end):
            self.redis_conn.hset(i, mapping={
                'Destino': i + 1,
                'Origem': i,
                'Peso': 1,
                'Tamanho': 1
            })

    def worker(self):
        while not self.task_queue.empty():
            batch_start, batch_end = self.task_queue.get()
            print(f"Thread {threading.current_thread().name} processando lote {batch_start}-{batch_end}")
            self.populate_batch(batch_start, batch_end)
            self.task_queue.task_done()

    def run(self, start, end):
        self.create_batches(start, end)
        threads = []

        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

if __name__ == "__main__":
    # Configuração de conexão ao Redis
    redis_connector = RedisConnector()
    redis_conn = redis_connector.db_redis

    # Configuração do populador com multithreading
    populator = RedisPopulator(redis_conn, num_threads=2, batch_size=10000)
    populator.run(start=1, end=1000001)
