from setuptools import setup, find_packages

setup(
    name="transfer_info",  # Nome da biblioteca
    version="0.1.0",  # Versão atual da biblioteca
    description="Biblioteca para transferir dados do Redis ao PostGreSQL",  # Descrição breve do que a biblioteca faz
    author="Daniel, Francinaldo, Luis, Rita, Iago, Cristina",  # Lista de autores da biblioteca
    packages=find_packages(),  # Encontrar todos os pacotes da biblioteca para incluir na distribuição
    install_requires=[  # Dependências que serão instaladas automaticamente
        "redis",  # Dependência para conectar com o Redis
    ],
    python_requires=">=3.9.13",  # Especifica a versão mínima do Python necessária
)