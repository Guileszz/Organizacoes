import sqlite3
import os
import shutil

# Configurações
DB_PATH = 'ledger_mutante.db'
QUARENTENA_DIR = r'D:\QUARENTENA_MUTANTE'
RUIDO = ['.DICloakCache', 'Cache_Data', 'logs', 'tmp', '.ldb']

if not os.path.exists(QUARENTENA_DIR):
    os.makedirs(QUARENTENA_DIR)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# IDENTIFICAÇÃO EM TEMPO REAL
try:
    cursor.execute("PRAGMA table_info(ativos)")
    colunas = [col[1] for col in cursor.fetchall()]
    print(f"[*] Colunas encontradas no seu Império: {colunas}")
    
    # Define as colunas de busca (Geralmente as duas primeiras são caminho e nome)
    col_1 = colunas[0]
    col_2 = colunas[1] if len(colunas) > 1 else colunas[0]

    print(f"[*] Limpando ruído nas colunas: {col_1} e {col_2}")

    for termo in RUIDO:
        # Busca dinâmica baseada nas colunas reais
        query = f"SELECT {col_1}, {col_2} FROM ativos WHERE {col_1} LIKE ? OR {col_2} LIKE ?"
        cursor.execute(query, (f'%{termo}%', f'%{termo}%'))
        rows = cursor.fetchall()
        
        for row in rows:
            val1, val2 = row
            # Tenta identificar qual dos valores é o caminho completo
            for path_candidato in [val1, val2]:
                if os.path.exists(str(path_candidato)):
                    try:
                        nome = os.path.basename(str(path_candidato))
                        destino = os.path.join(QUARENTENA_DIR, nome)
                        shutil.move(str(path_candidato), destino)
                        print(f"[V] MOVIDO: {nome}")
                    except:
                        pass

        # Deleta do banco
        cursor.execute(f"DELETE FROM ativos WHERE {col_1} LIKE ? OR {col_2} LIKE ?", (f'%{termo}%', f'%{termo}%'))

    conn.commit()
    print("\n[DONE] Operação finalizada com sucesso. DNA Purificado.")

except Exception as e:
    print(f"[!] Erro Crítico: {e}")

finally:
    conn.close()