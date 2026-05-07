import sqlite3
import os

def gerar_inventario_mutante(db_file):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Seleciona todos os ativos catalogados
        cursor.execute("SELECT nome, caminho, tamanho FROM ativos")
        linhas = cursor.fetchall()
        
        print(f"\n=== [ INVENTÁRIO DO IMPÉRIO MUTANTE ] ===")
        print(f"{'NOME DO ATIVO':<30} | {'TAMANHO (KB)':<12}")
        print("-" * 45)
        
        for nome, caminho, tamanho in linhas:
            # Converte bytes para KB para leitura rápida
            kb = round(tamanho / 1024, 2)
            print(f"{nome[:30]:<30} | {kb:<12} KB")
            
        print(f"\n[!] TOTAL DE ATIVOS IDENTIFICADOS: {len(linhas)}")
        conn.close()
    except Exception as e:
        print(f"[-] ERRO NA EXTRAÇÃO: {e}")

if __name__ == "__main__":
    gerar_inventario_mutante("ledger_mutante.db")