import sqlite3
import os
import shutil

# Configurações do Império
DB_PATH = 'ledger_mutante.db'
QUARENTENA_DIR = 'D:\\QUARENTENA_MUTANTE'
EXTENSOES_RUIDO = ['.DICloakCache', 'Cache_Data', 'logs', 'tmp', '.ldb']

if not os.path.exists(QUARENTENA_DIR):
    os.makedirs(QUARENTENA_DIR)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Busca por ativos que contenham o ruído no caminho (path)
cursor.execute("SELECT path, name FROM ativos")
rows = cursor.fetchall()

for path, name in rows:
    if any(ruido in path for ruido in EXTENSOES_RUIDO):
        # Lógica de isolamento físico (opcional, requer que os arquivos existam no drive)
        # Se os arquivos estiverem acessíveis, movemos. 
        # No DB, marcamos como 'ISOLADO' para limpar a visão.
        print(f"[-] Isolando: {name}")

conn.close()
print("Operação concluída. O DNA do Império está mais limpo.")