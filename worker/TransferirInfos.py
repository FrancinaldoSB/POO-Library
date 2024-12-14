import redis           
import psycopg2         
from time import sleep  
import os               
import redis.exceptions 
import threading        
from queue import Queue 
from library.transfer_info import tranferirinfos

class Connections:
    """
    A classe Connections é responsável por gerenciar as conexões com o Redis e o PostgreSQL.
    
    Attributes:
        dbRedis (redis.Redis): Instância da conexão com o Redis.
        dbPostgre (psycopg2.connection): Instância da conexão com o PostgreSQL.
    """
    
    def __init__(self):
        """
        Inicializa as conexões com Redis e PostgreSQL. Se a conexão com PostgreSQL falhar,
        o código tenta novamente até conseguir.

        Parameters:
            None
        """
        # Conexão com Redis
        redis_host = os.getenv('HOST_TO_REDIS', 'localhost')
        self.dbRedis = redis.Redis(host=redis_host, port=6379, decode_responses=True)

        # Conexão com PostgreSQL
        while True:
            try:
                post_host = os.getenv('HOST_TO_POSTGRES', 'localhost')
                self.dbPostgre = psycopg2.connect(
                    dbname="mydatabase",
                    user="root",
                    password="root",
                    host=post_host,
                    port="5432"
                )
                print("Conexão estabelecida com PostgreSQL")
                break
            except psycopg2.OperationalError:
                print('Não foi possível conectar ao PostgreSQL, tentando novamente...')
                sleep(2)

    def fecharConexoes(self):
        """
        Fecha as conexões com o Redis e PostgreSQL.

        Parameters:
            None

        Returns:
            None
        """
        self.dbRedis.close()
        self.dbPostgre.close()


class DataTransfer:
    """
    A classe DataTransfer é responsável por transferir dados do Redis para o PostgreSQL,
    utilizando multithreading e processamento em lotes.

    Attributes:
        redis_conn (redis.Redis): Conexão com o Redis.
        postgres_conn (psycopg2.connection): Conexão com o PostgreSQL.
        num_threads (int): Número de threads a serem usadas para a transferência.
        batch_size (int): Tamanho dos lotes a serem processados em cada thread.
        task_queue (Queue): Fila de tarefas para os trabalhadores (threads).
    """

    def __init__(self, redis_conn, postgres_conn, num_threads=2, batch_size=10000):
        """
        Inicializa a transferência de dados com as conexões e configurações fornecidas.

        Parameters:
            redis_conn (redis.Redis): Conexão com o Redis.
            postgres_conn (psycopg2.connection): Conexão com o PostgreSQL.
            num_threads (int): Número de threads a serem usadas (padrão: 2).
            batch_size (int): Tamanho dos lotes a serem processados (padrão: 10000).
        """
        self.redis_conn = redis_conn
        self.postgres_conn = postgres_conn
        self.num_threads = num_threads
        self.batch_size = batch_size
        self.task_queue = Queue()

    def criarTabela(self):
        """
        Cria a tabela no PostgreSQL para armazenar os dados transferidos, caso ela ainda não exista.
        
        Parameters:
            None
        
        Returns:
            None
        """
        cursor = self.postgres_conn.cursor()

        cursor.execute("""
            DROP TABLE IF EXISTS pacotes
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacotes (
                Destino VARCHAR(50),
                Origem VARCHAR(50),
                Peso VARCHAR(50),
                Tamanho VARCHAR(50)
            )
        """)

        self.postgres_conn.commit()
        cursor.close()

    def transferirLote(self, batch_start, batch_end):
        """
        Transferir um lote de dados do Redis para o PostgreSQL.

        Parameters:
            batch_start (int): O índice inicial do lote.
            batch_end (int): O índice final do lote.

        Returns:
            None
        """
        cursor = self.postgres_conn.cursor()
        try:
            for i in range(batch_start, batch_end):
                pacote = self.redis_conn.hgetall(i)
                cursor.execute("""
                    INSERT INTO pacotes (Destino, Origem, Peso, Tamanho)
                    VALUES (%s, %s, %s, %s)
                """, (
                    pacote['Destino'],
                    pacote['Origem'],
                    pacote['Peso'],
                    pacote['Tamanho']
                ))
            self.postgres_conn.commit()
            print(f"Lote {batch_start}-{batch_end} transferido com sucesso.")
        except Exception as e:
            print(f"Erro ao transferir lote {batch_start}-{batch_end}: {e}")
            self.postgres_conn.rollback()
        finally:
            cursor.close()

    def worker(self):
        """
        Função de trabalho executada pelas threads para processar os lotes de dados.

        Parameters:
            None

        Returns:
            None
        """
        while not self.task_queue.empty():
            batch_start, batch_end = self.task_queue.get()
            print(f"Thread {threading.current_thread().name} processando lote {batch_start}-{batch_end}")
            self.transferirLote(batch_start, batch_end)
            self.task_queue.task_done()


if __name__ == "__main__":
    """
    Executa a transferência de dados do Redis para o PostgreSQL.

    Estabelece as conexões com Redis e PostgreSQL, cria a tabela no PostgreSQL e
    chama a função `tranferirinfos` para transferir os dados em lotes.

    Parameters:
        None
    
    Returns:
        None
    """
    conexoes = Connections()

    transferencia = DataTransfer(conexoes.dbRedis, conexoes.dbPostgre, num_threads=2, batch_size=10000)
    transferencia.criarTabela()

    # Passe o objeto `transferencia` corretamente
    tranferirinfos(transferencia, start=1, end=1000001)

    conexoes.fecharConexoes()
