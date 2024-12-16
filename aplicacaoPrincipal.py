import psycopg2 as pg
from psycopg2 import OperationalError

class Postgre:
    """
    summary
        Classe responsável por gerenciar a conexão e operações no banco de dados PostgreSQL.
    
    methods
        criar_tabela()
            Cria a tabela 'pacotes' no banco de dados.
        inserir_pacote(destino, origem, peso, tamanho)
            Insere um novo pacote na tabela 'pacotes'.
        consultar_pacotes()
            Retorna todos os pacotes armazenados no banco de dados.
        atualizar_pacote(destino, peso_novo, tamanho_novo)
            Atualiza o peso e tamanho de um pacote com base no destino.
        deletar_pacote(destino)
            Remove um pacote da tabela com base no destino.
        fechar_conexao()
            Fecha a conexão com o banco de dados PostgreSQL.
    """
    def __init__(self) -> None:
        """
        summary
            Inicializa a conexão com o banco de dados PostgreSQL.
        
        parameters
            None
        """
        self.db_postgre = self.connect_to_db()

    def connect_to_db(self):
        """
        Estabelece a conexão com o banco de dados e lida com falhas.
        """
        try:
            return pg.connect(
                dbname="mydatabase",
                user="root",
                password="root",
                host="localhost",
                port="5432"
            )
        except OperationalError as e:
            print(f"Erro de conexão com o banco de dados: {e}")
            return None

    def garantir_conexao(self):
        """
        Garante que a conexão com o banco de dados esteja ativa. Se não, tenta reconectar.
        """
        if self.db_postgre is None or self.db_postgre.closed:
            print("Tentando reconectar ao banco de dados...")
            self.db_postgre = self.connect_to_db()

    def criar_tabela(self) -> None:
        """
        Cria a tabela 'pacotes' no banco de dados, caso não exista.
        """
        self.garantir_conexao()
        cursor = self.db_postgre.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacotes (
                Destino VARCHAR(50),
                Origem VARCHAR(50),
                Peso VARCHAR(50),
                Tamanho VARCHAR(50)
            )
        """)
        self.db_postgre.commit()
        cursor.close()

    def inserir_pacote(self, destino, origem, peso, tamanho) -> None:
        """
        Insere um novo pacote no banco de dados.
        """
        self.garantir_conexao()
        cursor = self.db_postgre.cursor()
        try:
            cursor.execute("""
                INSERT INTO pacotes (Destino, Origem, Peso, Tamanho) 
                VALUES (%s, %s, %s, %s)
            """, (destino, origem, peso, tamanho))
            self.db_postgre.commit()
        except Exception as e:
            print(f"Erro ao inserir pacote: {e}")
            self.db_postgre.rollback()
        finally:
            cursor.close()

    def consultar_pacotes(self) -> list:
        """
        Consulta e retorna todos os pacotes cadastrados na tabela.
        """
        self.garantir_conexao()
        cursor = self.db_postgre.cursor()
        cursor.execute("SELECT * FROM pacotes")
        pacotes = cursor.fetchall()
        cursor.close()
        return pacotes

    def atualizar_pacote(self, destino, peso_novo=None, tamanho_novo=None, origem_nova=None) -> None:
        """
        Atualiza as informações de um pacote com base no destino.
        """
        self.garantir_conexao()
        cursor = self.db_postgre.cursor()
        try:
            cursor.execute("SELECT * FROM pacotes WHERE Destino = %s", (destino,))
            pacote = cursor.fetchone()

            if not pacote:
                print("Pacote não encontrado.")
                cursor.close()
                return

            if peso_novo is not None:
                cursor.execute("UPDATE pacotes SET Peso = %s WHERE Destino = %s", (peso_novo, destino))
            if tamanho_novo is not None:
                cursor.execute("UPDATE pacotes SET Tamanho = %s WHERE Destino = %s", (tamanho_novo, destino))
            if origem_nova is not None:
                cursor.execute("UPDATE pacotes SET Origem = %s WHERE Destino = %s", (origem_nova, destino))
            
            self.db_postgre.commit()
            print("Pacote atualizado com sucesso.")
        except Exception as e:
            print(f"Erro ao atualizar pacote: {e}")
            self.db_postgre.rollback()
        finally:
            cursor.close()

    def deletar_pacote(self, destino) -> None:
        """
        Remove um pacote da tabela com base no destino.
        """
        self.garantir_conexao()
        cursor = self.db_postgre.cursor()
        try:
            cursor.execute("DELETE FROM pacotes WHERE Destino = %s", (destino,))
            self.db_postgre.commit()
            print("Pacote deletado com sucesso!")
        except Exception as e:
            print(f"Erro ao deletar pacote: {e}")
            self.db_postgre.rollback()
        finally:
            cursor.close()

    def fechar_conexao(self) -> None:
        """
        Fecha a conexão com o banco de dados PostgreSQL.
        """
        if self.db_postgre:
            self.db_postgre.close()


def exibir_menu() -> None:
    """
    Exibe o menu principal do sistema para o usuário.
    """
    print("\n")
    print("=====================================")
    print("         Sistema de Pacotes")
    print("=====================================")
    print("1. Inserir Pacote")
    print("2. Consultar Pacotes")
    print("3. Atualizar Pacote")
    print("4. Deletar Pacote")
    print("5. Sair")
    print("=====================================")


def main() -> None:
    """
    Função principal do programa. Controla o fluxo do sistema de pacotes.
    """
    db = Postgre()
    db.criar_tabela()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':  # Inserir pacote
            destino = input("Digite o destino do pacote: ")
            origem = input("Digite a origem do pacote: ")
            peso = input("Digite o peso do pacote: ")
            tamanho = input("Digite o tamanho do pacote: ")
            db.inserir_pacote(destino, origem, peso, tamanho)
            print("Pacote inserido com sucesso!")

        elif opcao == '2':  # Consultar pacotes
            pacotes = db.consultar_pacotes()
            if pacotes:
                print("Pacotes cadastrados:")
                for pacote in pacotes:
                    print(f"Destino: {pacote[0]}, Origem: {pacote[1]}, Peso: {pacote[2]}, Tamanho: {pacote[3]}")
            else:
                print("Nenhum pacote encontrado.")

        elif opcao == '3':  # Atualizar pacote
            destino = input("Digite o destino do pacote a ser atualizado: ")
            print("Escolha o que deseja atualizar:")
            print("1. Peso")
            print("2. Tamanho")
            print("3. Origem")
            print("4. Peso e Tamanho")
            print("5. Origem e Peso")
            print("6. Origem e Tamanho")
            print("7. Todos")
            escolha = input("Escolha uma opção: ")

            peso_novo = tamanho_novo = origem_nova = None

            if escolha == '1':
                peso_novo = input("Digite o novo peso do pacote: ")
            elif escolha == '2':
                tamanho_novo = input("Digite o novo tamanho do pacote: ")
            elif escolha == '3':
                origem_nova = input("Digite a nova origem do pacote: ")
            elif escolha == '4':
                peso_novo = input("Digite o novo peso do pacote: ")
                tamanho_novo = input("Digite o novo tamanho do pacote: ")
            elif escolha == '5':
                origem_nova = input("Digite a nova origem do pacote: ")
                peso_novo = input("Digite o novo peso do pacote: ")
            elif escolha == '6':
                origem_nova = input("Digite a nova origem do pacote: ")
                tamanho_novo = input("Digite o novo tamanho do pacote: ")
            elif escolha == '7':
                origem_nova = input("Digite a nova origem do pacote: ")
                peso_novo = input("Digite o novo peso do pacote: ")
                tamanho_novo = input("Digite o novo tamanho do pacote: ")
            else:
                print("Opção inválida. Tente novamente.")
                continue
            
            db.atualizar_pacote(destino, peso_novo, tamanho_novo, origem_nova)

        elif opcao == '4':  # Deletar pacote
            destino = input("Digite o destino do pacote a ser deletado: ")
            db.deletar_pacote(destino)
            print("Pacote deletado com sucesso!")

        elif opcao == '5':  # Sair
            db.fechar_conexao()
            print("Conexão encerrada. Saindo do sistema...")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
