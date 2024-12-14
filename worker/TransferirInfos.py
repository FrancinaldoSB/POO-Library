import redis           
import psycopg2         
from time import sleep  
import os               
import redis.exceptions 
import threading        
from queue import Queue 
from library.transfer_info import tranferirinfos

class Connections:
    def __init__(self):
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
        self.dbRedis.close()
        self.dbPostgre.close()

class DataTransfer:
    def __init__(self, redis_conn, postgres_conn, num_threads=2, batch_size=10000):
        self.redis_conn = redis_conn
        self.postgres_conn = postgres_conn
        self.num_threads = num_threads
        self.batch_size = batch_size
        self.task_queue = Queue()

    def criarTabela(self):
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
        while not self.task_queue.empty():
            batch_start, batch_end = self.task_queue.get()
            print(f"Thread {threading.current_thread().name} processando lote {batch_start}-{batch_end}")
            self.transferirLote(batch_start, batch_end)
            self.task_queue.task_done()


if __name__ == "__main__":
    conexoes = Connections()

    transferencia = DataTransfer(conexoes.dbRedis, conexoes.dbPostgre, num_threads=2, batch_size=10000)
    transferencia.criarTabela()

    # Passe o objeto `transferencia` corretamente
    tranferirinfos(transferencia, start=1, end=1000001)

    conexoes.fecharConexoes()
