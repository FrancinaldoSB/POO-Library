# Base image com Python
FROM python:3.10

# Instala o htop
RUN apt-get update && apt-get install -y htop && apt-get clean

# Configura o diretório de trabalho
WORKDIR /app

# Copia o código para o contêiner
COPY . .

# Instala as dependências
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Define a variável de ambiente
ENV HOST_TO_REDIS=redis

# Comando padrão para execução
CMD ["python", "PovoarRedis.py"]