import redis  
import redis.exceptions  
from time import sleep  
import os  
import threading  
from queue import Queue  

class RedisConnector:
    """
    A classe RedisConnector é responsável por estabelecer a conexão com o Redis. Se a conexão falhar,
    ela tenta reconectar até que uma conexão seja estabelecida com sucesso.

    Attributes:
        redis_host (str): O endereço do host Redis, que pode ser configurado via variável de ambiente.
        db_redis (redis.Redis): Instância de conexão com o banco de dados Redis.
    """

    def __init__(self):
        """
        Inicializa a conexão com o Redis, utilizando a variável de ambiente 'HOST_TO_REDIS' ou 'localhost' como valor padrão.

        Parameters:
            None
        """
        self.redis_host = os.getenv('HOST_TO_REDIS', 'localhost')
        self.db_redis = self.connect_to_redis()

    def connect_to_redis(self):
        """
        Tenta estabelecer uma conexão com o Redis, tentando novamente caso ocorra algum erro de conexão.

        Parameters:
            None
        
        Returns:
            redis.Redis: Instância da conexão Redis.
        """
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
    """
    A classe RedisPopulator é responsável por popular o Redis com dados em lotes, utilizando múltiplas threads para processar os dados em paralelo.

    Attributes:
        redis_conn (redis.Redis): Instância da conexão com o Redis.
        num_threads (int): Número de threads a serem utilizadas para processar os lotes.
        batch_size (int): Tamanho do lote de dados a ser processado por thread.
        task_queue (Queue): Fila de tarefas que armazena os intervalos dos lotes a serem processados.
    """

    def __init__(self, redis_conn, num_threads=2, batch_size=10000):
        """
        Inicializa a configuração para o processo de popular o Redis com dados em lotes.

        Parameters:
            redis_conn (redis.Redis): Instância da conexão com o Redis.
            num_threads (int): Número de threads a serem usadas (padrão: 2).
            batch_size (int): Tamanho dos lotes a serem processados (padrão: 10000).
        """
        self.redis_conn = redis_conn
        self.num_threads = num_threads
        self.batch_size = batch_size
        self.task_queue = Queue()

    def create_batches(self, start, end):
        """
        Cria os lotes de dados a serem processados, dividindo o intervalo de dados de acordo com o tamanho do lote.

        Parameters:
            start (int): O índice inicial dos dados.
            end (int): O índice final dos dados.

        Returns:
            None
        """
        for i in range(start, end, self.batch_size):
            batch_start = i
            batch_end = min(i + self.batch_size, end)
            self.task_queue.put((batch_start, batch_end))

    def populate_batch(self, batch_start, batch_end):
        """
        Popula o Redis com dados para um determinado intervalo de lote.

        Parameters:
            batch_start (int): O índice inicial do lote.
            batch_end (int): O índice final do lote.

        Returns:
            None
        """
        for i in range(batch_start, batch_end):
            self.redis_conn.hset(i, mapping={
                'Destino': i + 1,
                'Origem': i,
                'Peso': 1,
                'Tamanho': 1
            })

    def worker(self):
        """
        Função do trabalhador que processa os lotes de dados em paralelo. Cada thread retira um lote da fila e processa os dados.

        Parameters:
            None

        Returns:
            None
        """
        while not self.task_queue.empty():
            batch_start, batch_end = self.task_queue.get()
            print(f"Thread {threading.current_thread().name} processando lote {batch_start}-{batch_end}")
            self.populate_batch(batch_start, batch_end)
            self.task_queue.task_done()

    def run(self, start, end):
        """
        Inicia o processo de popular o Redis com dados utilizando múltiplas threads. Divida os dados em lotes e distribua
        entre as threads para processamento paralelo.

        Parameters:
            start (int): O índice inicial dos dados.
            end (int): O índice final dos dados.

        Returns:
            None
        """
        self.create_batches(start, end)
        threads = []

        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()


if __name__ == "__main__":
    """
    Inicia a configuração de conexão com o Redis e a população de dados no Redis utilizando múltiplas threads.

    Parameters:
        None

    Returns:
        None
    """
    # Configuração de conexão ao Redis
    redis_connector = RedisConnector()
    redis_conn = redis_connector.db_redis

    # Configuração do populador com multithreading
    populator = RedisPopulator(redis_conn, num_threads=2, batch_size=10000)
    populator.run(start=1, end=1000001)
