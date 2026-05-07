import sqlite3
import os

def rastrear():
    # Caminho do seu banco de dados organizado
    db = "ledger_mutante.db"
    
    if not os.path.exists(db):
        print(f"[-] Erro: O arquivo {db} nao foi encontrado na pasta atual.")
        return

    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    # Busca por arquivos .txt que tenham 'habbo' no nome
    # O comando LOWER garante que pegue 'Habbo', 'HABBO' ou 'habbo'
    query = """
    SELECT nome, caminho 
    FROM ativos 
    WHERE LOWER(nome) LIKE '%habbo%' AND nome LIKE '%.txt%'
    """
    
    cursor.execute(query)
    alvos = cursor.fetchall()
    
    print(f"\n>>> [ ALVOS LOCALIZADOS: {len(alvos)} ] <<<\n")
    
    for nome, caminho in alvos:
        print(f"ARQUIVO: {nome}")
        print(f"CAMINHO: {caminho}")
        print("-" * 60)
    
    conn.close()

if __name__ == "__main__":
    rastrear()