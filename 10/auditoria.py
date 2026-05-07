import sqlite3
import os

def scan_db_bruto(arquivo):
    if not os.path.exists(arquivo):
        print(f"[-] ERRO: O arquivo {arquivo} nao foi encontrado no diretorio D:\\")
        return

    try:
        conn = sqlite3.connect(arquivo)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        
        print(f"\n[!] INVENTARIO DO IMPERIO: {len(tabelas)} TABELAS")
        
        for t in tabelas:
            tome = t[0]
            print(f"[+] TABELA: {tome}")
            cursor.execute(f"PRAGMA table_info({tome});")
            colunas = [c[1] for c in cursor.fetchall()]
            print(f"    COLUNAS: {colunas}\n")
            
        conn.close()
    except Exception as e:
        print(f"[-] FALHA NA INFILTRACAO: {e}")

if __name__ == "__main__":
    scan_db_bruto("ledger_mutante.db")
import sqlite3
import os

def scan_db_bruto(arquivo):
    if not os.path.exists(arquivo):
        print(f"[-] ERRO: O arquivo {arquivo} nao foi encontrado no diretorio D:\\")
        return

    try:
        conn = sqlite3.connect(arquivo)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        
        print(f"\n[!] INVENTARIO DO IMPERIO: {len(tabelas)} TABELAS")
        
        for t in tabelas:
            tome = t[0]
            print(f"[+] TABELA: {tome}")
            cursor.execute(f"PRAGMA table_info({tome});")
            colunas = [c[1] for c in cursor.fetchall()]
            print(f"    COLUNAS: {colunas}\n")
            
        conn.close()
    except Exception as e:
        print(f"[-] FALHA NA INFILTRACAO: {e}")

if __name__ == "__main__":
    scan_db_bruto("ledger_mutante.db")