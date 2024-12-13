def tranferirinfos(self) -> None:

    '''
    summary
        Transfere os dados armazenados no Redis para a tabela `pacotes` no PostgreSQL.
        Cada registro no Redis é inserido na tabela utilizando um loop iterativo.
        Em caso de erro, a transação é revertida.
    
    parameters
        None
        
    return
        None
    '''

    cursor = self.dbPostgre.cursor()
    try:
        for i in range(1, 1000001):
            pacote = self.dbRedis.hgetall(i)
            cursor.execute("""
                INSERT INTO pacotes (Destino, Origem, Peso, Tamanho)
                VALUES (%s, %s, %s, %s)
            """, (
                pacote['Destino'], 
                pacote['Origem'],  
                pacote['Peso'],   
                pacote['Tamanho'] 
            ))
            
            
            self.dbPostgre.commit()
            print(f"{i} registros transferidos.")
        
        self.dbPostgre.commit() 
        print("Transferência concluída com sucesso.")
        
    except Exception as e:
        print(f"Erro durante a transferência de dados: {e}")
        self.dbPostgre.rollback()
    finally:
        cursor.close() 