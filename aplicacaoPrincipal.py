import psycopg2 as pg
from psycopg2 import OperationalError

class Postgre:
    """
    summary
        Classe responsável por gerenciar a conexão e operações no banco de dados PostgreSQL.
    
    methods
        CriarTabela()
            Cria a tabela 'pacotes' no banco de dados.
        inserirPacote(destino, origem, peso, tamanho)
            Insere um novo pacote na tabela 'pacotes'.
        consultarPacotes()
            Retorna todos os pacotes armazenados no banco de dados.
        atualizarPacote(destino, peso_novo, tamanho_novo)
            Atualiza o peso e tamanho de um pacote com base no destino.
        deletarPacote(destino)
            Remove um pacote da tabela com base no destino.
        fecharConexao()
            Fecha a conexão com o banco de dados PostgreSQL.
    """
    def __init__(self) -> None:
        """
        summary
            Inicializa a conexão com o banco de dados PostgreSQL.
        
        parameters
            None
        """
        self.dbPostgre = self.connect_to_db()

    def connect_to_db(self):
        """
        Estabelece a conexão com o banco de dados e lida com falhas.
        """
        try:
            return pg.connect(
                dbname="mydatabase",  # Nome do banco de dados
                user="root",          # Usuário do banco de dados
                password="root",      # Senha do banco de dados
                host="localhost",     # Host onde o banco está rodando
                port="5432"           # Porta de conexão do PostgreSQL
            )
        except OperationalError as e:
            print(f"Erro de conexão com o banco de dados: {e}")
            return None

    def garantir_conexao(self):
        """
        Garante que a conexão com o banco de dados esteja ativa. Se não, tenta reconectar.
        """
        if self.dbPostgre is None or self.dbPostgre.closed:
            print("Tentando reconectar ao banco de dados...")
            self.dbPostgre = self.connect_to_db()

    def CriarTabela(self) -> None:
        """
        summary
            Cria a tabela 'pacotes' no banco de dados, caso não exista.
        
        parameters
            None
        
        return
            None
        """
        self.garantir_conexao()  # Garante que a conexão está ativa
        cursor = self.dbPostgre.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacotes (
                Destino VARCHAR(50),
                Origem VARCHAR(50),
                Peso VARCHAR(50),
                Tamanho VARCHAR(50)
            )
        """)
        self.dbPostgre.commit()
        cursor.close()

    def inserirPacote(self, destino, origem, peso, tamanho) -> None:
        """
        summary
            Insere um novo pacote no banco de dados.
        
        parameters
            destino : str
                Destino do pacote.
            origem : str
                Origem do pacote.
            peso : str
                Peso do pacote.
            tamanho : str
                Tamanho do pacote.
        
        return
            None
        """
        self.garantir_conexao()  # Garante que a conexão está ativa
        cursor = self.dbPostgre.cursor()
        try:
            cursor.execute("""
                INSERT INTO pacotes (Destino, Origem, Peso, Tamanho) 
                VALUES (%s, %s, %s, %s)
            """, (destino, origem, peso, tamanho))
            self.dbPostgre.commit()
        except Exception as e:
            print(f"Erro ao inserir pacote: {e}")
            self.dbPostgre.rollback()
        finally:
            cursor.close()

    def consultarPacotes(self) -> list:
        """
        summary
            Consulta e retorna todos os pacotes cadastrados na tabela.
        
        parameters
            None
        
        return
            list
                Lista com os pacotes cadastrados.
        """
        self.garantir_conexao()  # Garante que a conexão está ativa
        cursor = self.dbPostgre.cursor()
        cursor.execute("SELECT * FROM pacotes")
        pacotes = cursor.fetchall()
        cursor.close()
        return pacotes

    def atualizarPacote(self, destino, peso_novo=None, tamanho_novo=None, origem_nova=None) -> None:
        """
        summary
            Atualiza o peso e tamanho de um pacote com base no destino.
        
        parameters
            destino : str
                Destino do pacote a ser atualizado.
            peso_novo : str
                Novo peso do pacote.
            tamanho_novo : str
                Novo tamanho do pacote.
            origem_nova : str
                Parâmetro opcional para atualizar a origem
        return
            None
        """
        self.garantir_conexao()  # Garante que a conexão está ativa
        cursor = self.dbPostgre.cursor()
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
            
            self.dbPostgre.commit()
            print("Pacote atualizado com sucesso.")
        except Exception as e:
            print(f"Erro ao atualizar pacote: {e}")
            self.dbPostgre.rollback()
        finally:
            cursor.close()

    def deletarPacote(self, destino) -> None:
        """
        summary
            Remove um pacote da tabela com base no destino.
        
        parameters
            destino : str
                Destino do pacote a ser deletado.
        
        return
            None
        """
        self.garantir_conexao()  # Garante que a conexão está ativa
        cursor = self.dbPostgre.cursor()
        try:
            cursor.execute("""
                DELETE FROM pacotes 
                WHERE Destino = %s
            """, (destino,))
            self.dbPostgre.commit()
            print("Pacote deletado com sucesso!")
        except Exception as e:
            print(f"Erro ao deletar pacote: {e}")
            self.dbPostgre.rollback()
        finally:
            cursor.close()

    def fecharConexao(self) -> None:
        """
        summary
            Fecha a conexão com o banco de dados PostgreSQL.
        
        parameters
            None
        
        return
            None
        """
        if self.dbPostgre:
            self.dbPostgre.close()

def exibir_menu() -> None:
    """
    summary
        Exibe o menu principal do sistema para o usuário.
    
    parameters
        None
    
    return
        None
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
    summary
        Função principal do programa. Controla o fluxo do sistema de pacotes.
    
    parameters
        None
    
    return
        None
    """
    db = Postgre()
    db.CriarTabela()  # Garante que a tabela exista no banco
    
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1': # Inserir pacote
            destino = input("Digite o destino do pacote: ")
            origem = input("Digite a origem do pacote: ")
            peso = input("Digite o peso do pacote: ")
            tamanho = input("Digite o tamanho do pacote: ")
            db.inserirPacote(destino, origem, peso, tamanho)
            print("Pacote inserido com sucesso!")

        elif opcao == '2': # Consultar pacotes
            pacotes = db.consultarPacotes()
            if pacotes:
                print("Pacotes cadastrados:")
                for pacote in pacotes:
                    if (int(pacote[0]) % 1000 == 0):
                        print(f"Destino: {pacote[0]}, Origem: {pacote[1]}, Peso: {pacote[2]}, Tamanho: {pacote[3]}")
            else:
                print("Nenhum pacote encontrado.")
                
        elif opcao == '3': # Atualizar pacote
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

            # Atualiza os campos de acordo com a escolha do usuário
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
            
            db.atualizarPacote(destino, peso_novo, tamanho_novo, origem_nova)

        elif opcao == '4': # Deletar pacote
            destino = input("Digite o destino do pacote a ser deletado: ")
            db.deletarPacote(destino)
            print("Pacote deletado com sucesso!")

        elif opcao == '5': # Sair
            db.fecharConexao()
            print("Conexão encerrada. Saindo do sistema...")
            break

        else: # Opção inválida
            print("Opção inválida. Tente novamente.")

# Executa a função principal
if __name__ == "__main__":
    main()