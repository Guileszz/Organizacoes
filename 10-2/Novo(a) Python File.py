import os
import shutil

# CONFIGURAÇÃO DO NÚCLEO
pasta_destino = r'C:\IMPÉRIO_MUTANTE_ATIVOS'
diretorios_garimpo = [
    os.path.join(os.environ['USERPROFILE'], 'Downloads'),
    os.path.join(os.environ['USERPROFILE'], 'Pictures'),
    os.path.join(os.environ['USERPROFILE'], 'Desktop')
]

if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)
    print(f"[+] Diretório de Soberania criado: {pasta_destino}")

def consolidar_ativos():
    print("[!] Iniciando extração e movimentação...")
    for raiz in diretorios_garimpo:
        for root, dirs, files in os.walk(raiz):
            for file in files:
                if file.endswith('.txt'):
                    caminho_origem = os.path.join(root, file)
                    caminho_destino = os.path.join(pasta_destino, file)
                    
                    # Evita sobrescrever se o nome for igual (adiciona sufixo)
                    if os.path.exists(caminho_destino):
                        base, ext = os.path.splitext(file)
                        caminho_destino = os.path.join(pasta_destino, f"{base}_CLONADO{ext}")
                    
                    try:
                        shutil.move(caminho_origem, caminho_destino)
                        print(f"[OK] Movido: {file}")
                    except Exception as e:
                        print(f"[ERRO] Falha ao mover {file}: {e}")

if __name__ == "__main__":
    consolidar_ativos()
    print("\n[+] Operação Concluída. Todos os .txt agora estão no QG: C:\IMPÉRIO_MUTANTE_ATIVOS")