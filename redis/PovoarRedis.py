import redis            # Biblioteca para interação com o Redis
import redis.exceptions # Exceções relacionadas ao Redis
from time import sleep  # Função para aguardo de tentativas de conexão
import os               # Biblioteca para acesso de variáveis de ambiente

# Loop para tentar estabelecer conexão com o Redis
while True:
    try: 
        # Obtém o host do Redis de uma variável de ambiente; se não estiver definida, usa 'localhost'
        redis_host = os.getenv('HOST_TO_REDIS', 'localhost')
        # Configura a conexão com o Redis
        dbRedis = redis.Redis(
                    host=redis_host, port=6379, decode_responses=True)
        print("Conexao estabelecida")
        break # Saída do loop
   
    # Tratamento de erro de conexão
    except redis.exceptions.ConnectionError:
        print("Erro ao conectar")
        sleep(2) # Espera de 2 segundos antes de tentar novamente

# Povoamento do Redis com dados fictícios
# Estrutura: ID -> {Destino, Origem, Peso, Tamanho}
for i in range(1, 1000001):
    # i = Chave do hash no Redis
    dbRedis.hset(i, mapping={
        'Destino': i + 1, # Definição do campo 'Destino' como o ID + 1
        'Origem': i,      # Definição do campo 'Origem' como o ID atual
        'Peso': 1,        # Definição do campo 'Peso' como 1
        'Tamanho': 1      # Definição do campo 'Tamanho' como 1
    })

    