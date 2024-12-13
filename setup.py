from setuptools import setup, find_packages

setup(
    name="transfer_info",
    version="0.1.0",
    description="Biblioteca para transferir dados do Redis ao PostGreSQL",
    author="Daniel, Francinaldo, Luis, Rita, Iago, Cristina",
    packages=find_packages(),
    install_requires=[
        "redis",
        
    ],
    python_requires=">=3.9.13",
)