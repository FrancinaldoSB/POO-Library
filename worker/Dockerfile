# Base image com Python
FROM python:3.9.13

# Instala o htop
RUN apt-get update && apt-get install -y htop && apt-get clean

# Configura o diretório de trabalho
WORKDIR /app

# Copia o conteúdo do diretório para o contêiner
COPY . .

# Instala as dependências
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install dist/transfer_infos-1.0-py3-none-any.whl

# Define variáveis de ambiente
ENV HOST_TO_REDIS=redis
ENV HOST_TO_POSTGRES=postgres

# Comando padrão para execução
CMD ["python", "TransferirInfos.py"]
