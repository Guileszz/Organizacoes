import sqlite3
import os

# Alvo: Banco de Dados no Disco D
db_path = "D:\\ledger_mutante.db"

if not os.path.exists(db_path):
    print(f"[-] Erro: {db_path} nao encontrado.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Busca simplificada: .txt + habbo
    cmd = "SELECT nome, caminho FROM ativos WHERE nome LIKE '%habbo%' AND nome LIKE '%.txt%'"
    
    cursor.execute(cmd)
    itens = cursor.fetchall()
    
    print(f"\n>>> [ NÉCTAR ENCONTRADO: {len(itens)} ARQUIVOS ] <<<\n")
    for nome, path in itens:
        print(f"ARQUIVO: {nome}")
        print(f"LOCAL:   {path}")
        print("-" * 50)
    
    conn.close()