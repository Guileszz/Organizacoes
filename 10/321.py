import sqlite3
import os

def localizar_habbo(db_file):
    if not os.path.exists(db_file):
        print(f"[-] ERRO: Banco {db_file} não encontrado.")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Busca arquivos .txt que tenham 'habbo' no nome (independente de maiúsculas)
    query = """
    SELECT nome, caminho, categoria 
    FROM ativos 
    WHERE nome LIKE '%habbo%' AND nome LIKE '%.txt%'
    """
    
    cursor.execute(query)
    resultados = cursor.fetchall()
    
    print(f"\n>>> [ ALVOS LOCALIZADOS: {len(resultados)} ] <<<\n")
    
    if resultados:
        print(f"{'NOME DO ARQUIVO':<40} | {'LOCALIZAÇÃO'}")
        print("-" * 80)
        for nome, caminho, cat in resultados:
            print(f"{nome:<40} | {caminho}")
    else:
        print("[!] Nenhum .txt com a assinatura 'Habbo' foi encontrado no Ledger.")

    conn.close()

if __name__ == "__main__":
    localizar_habbo("ledger_mutante.db")