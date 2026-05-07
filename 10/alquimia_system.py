#!/usr/bin/env python3
"""
PROJETO ALQUIMIA: MOTOR DE TRIAGEM DE DADOS
Sistema avançado de triagem massiva de ativos e transformação de dados brutos em "Néctar"
"""

import os
import shutil
import hashlib
import json
from pathlib import Path
import sqlite3
from datetime import datetime
import re
from collections import Counter
import mimetypes

class AlquimiaSystem:
    """
    Sistema avançado de triagem e processamento de dados
    Transforma arquivos brutos em "Néctar" (produtos prontos)
    """

    def __init__(self):
        self.nome = "ALQUIMIA"
        self.descricao = "Motor de Triagem de Dados e Transformação de Ativos"
        self.status = "ativo"
        self.banco_dados = None
        self.metricas = {
            'processados': 0,
            'descartados': 0,
            'transformados': 0,
            'duplicatas': 0
        }

        # Tipos de arquivos suportados
        self.tipos_suportados = {
            '.pdf': 'documentos',
            '.epub': 'ebooks',
            '.mobi': 'ebooks',
            '.txt': 'textos',
            '.doc': 'documentos',
            '.docx': 'documentos',
            '.xls': 'planilhas',
            '.xlsx': 'planilhas',
            '.csv': 'dados',
            '.json': 'dados',
            '.xml': 'dados',
            '.html': 'web',
            '.htm': 'web',
            '.py': 'codigo',
            '.js': 'codigo',
            '.css': 'codigo',
            '.sql': 'codigo'
        }

        # Palavras-chave para categorização
        self.palavras_chave = {
            'negocios': ['negocio', 'marketing', 'vendas', 'empreendedorismo', 'estrategia'],
            'tecnologia': ['python', 'programacao', 'desenvolvimento', 'ia', 'inteligencia', 'algoritmo'],
            'financas': ['financeiro', 'investimento', 'criptomoeda', 'bitcoin', 'acoes'],
            'saude': ['saude', 'medicina', 'nutricao', 'fitness', 'bem-estar'],
            'educacao': ['educacao', 'aprendizado', 'curso', 'aula', 'estudo']
        }

        # Inicializar sistema
        self.inicializar_sistema()

    def inicializar_sistema(self):
        """Inicializa o sistema Alquimia com banco de dados e estrutura"""
        print(f"[ALQUIMIA] Inicializando motor de triagem...")

        # Inicializar banco de dados
        self.banco_dados = sqlite3.connect('alquimia_triagem.db')
        cursor = self.banco_dados.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arquivos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_original TEXT NOT NULL,
                nome_limpo TEXT,
                caminho TEXT,
                tamanho INTEGER,
                tipo TEXT,
                categoria TEXT,
                hash_conteudo TEXT UNIQUE,
                duplicata INTEGER DEFAULT 0,
                qualidade REAL DEFAULT 0.0,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                palavras_chave TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metricas_triagem (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                arquivos_processados INTEGER,
                arquivos_descartados INTEGER,
                arquivos_transformados INTEGER,
                duplicatas_encontradas INTEGER
            )
        ''')

        self.banco_dados.commit()
        print(f"  [✓] Motor de triagem Alquimia inicializado")

    def calcular_hash_arquivo(self, caminho_arquivo):
        """Calcula hash SHA-256 do conteúdo do arquivo"""
        hash_sha256 = hashlib.sha256()
        with open(caminho_arquivo, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def limpar_nome_arquivo(self, nome_original):
        """Limpa e padroniza o nome do arquivo"""
        # Remover caracteres especiais e espaços extras
        nome_limpo = re.sub(r'[^\w\s.-]', '', nome_original)
        nome_limpo = re.sub(r'\s+', '_', nome_limpo)
        nome_limpo = re.sub(r'_+', '_', nome_limpo)  # Remover underscores consecutivos
        nome_limpo = nome_limpo.strip('_.')

        # Converter para minúsculas (exceto extensão)
        nome_partes = nome_limpo.rsplit('.', 1)
        if len(nome_partes) == 2:
            nome_limpo = f"{nome_partes[0].lower()}.{nome_partes[1].lower()}"

        return nome_limpo

    def detectar_categoria(self, nome_arquivo, caminho_completo=None):
        """Detecta a categoria do arquivo com base no nome e conteúdo"""
        nome_lower = nome_arquivo.lower()

        # Verificar palavras-chave no nome
        for categoria, palavras in self.palavras_chave.items():
            for palavra in palavras:
                if palavra in nome_lower:
                    return categoria

        # Detectar por extensão
        extensao = Path(nome_arquivo).suffix.lower()
        return self.tipos_suportados.get(extensao, 'outros')

    def analisar_qualidade_arquivo(self, caminho_arquivo):
        """Analisa a qualidade do arquivo com base em vários critérios"""
        tamanho = os.path.getsize(caminho_arquivo)

        # Critérios de qualidade
        qualidade = 0.0

        # Tamanho do arquivo (ajustar conforme necessário)
        if tamanho > 1024:  # Mais de 1KB
            qualidade += 0.3
        if tamanho > 1024 * 100:  # Mais de 100KB
            qualidade += 0.2

        # Tipo de arquivo
        extensao = Path(caminho_arquivo).suffix.lower()
        if extensao in ['.pdf', '.epub', '.docx', '.txt']:
            qualidade += 0.2

        # Conteúdo do arquivo (primeiros bytes)
        try:
            with open(caminho_arquivo, 'rb') as f:
                cabecalho = f.read(1024)
                # Verificar se tem conteúdo legível
                if len(cabecalho) > 0:
                    qualidade += 0.3
        except:
            pass

        return min(qualidade, 1.0)  # Limitar a 1.0

    def filtrar_por_qualidade(self, caminho_arquivo, qualidade_minima=0.5):
        """Filtra arquivo com base na qualidade"""
        qualidade = self.analisar_qualidade_arquivo(caminho_arquivo)
        return qualidade >= qualidade_minima

    def processar_arquivo(self, caminho_original, diretorio_saida=None):
        """Processa um único arquivo de acordo com os critérios do Projeto Alquimia"""
        nome_original = Path(caminho_original).name
        tamanho = os.path.getsize(caminho_original)

        print(f"  [>] Processando: {nome_original} ({tamanho} bytes)")

        # Calcular hash para detectar duplicatas
        hash_conteudo = self.calcular_hash_arquivo(caminho_original)

        # Verificar se já existe (duplicata)
        cursor = self.banco_dados.cursor()
        cursor.execute("SELECT id FROM arquivos WHERE hash_conteudo = ?", (hash_conteudo,))
        duplicata = cursor.fetchone() is not None

        if duplicata:
            print(f"    [!] Duplicata detectada: {nome_original}")
            self.metricas['duplicatas'] += 1

            # Atualizar registro existente
            cursor.execute("UPDATE arquivos SET duplicata = 1 WHERE hash_conteudo = ?", (hash_conteudo,))
            self.banco_dados.commit()
            return False

        # Analisar qualidade
        qualidade = self.analisar_qualidade_arquivo(caminho_original)

        if qualidade < 0.3:  # Limite mínimo de qualidade
            print(f"    [-] Arquivo de baixa qualidade, descartando: {nome_original}")
            self.metricas['descartados'] += 1
            return False

        # Limpar nome do arquivo
        nome_limpo = self.limpar_nome_arquivo(nome_original)

        # Detectar categoria
        categoria = self.detectar_categoria(nome_original)

        # Determinar diretório de saída com base na categoria
        if diretorio_saida:
            diretorio_categoria = os.path.join(diretorio_saida, categoria)
            os.makedirs(diretorio_categoria, exist_ok=True)
            caminho_saida = os.path.join(diretorio_categoria, nome_limpo)
        else:
            caminho_saida = os.path.join(categoria, nome_limpo)
            os.makedirs(categoria, exist_ok=True)

        # Copiar arquivo para saída
        shutil.copy2(caminho_original, caminho_saida)

        # Registrar no banco de dados
        cursor.execute('''
            INSERT INTO arquivos (nome_original, nome_limpo, caminho, tamanho, tipo, categoria, hash_conteudo, qualidade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nome_original, nome_limpo, caminho_saida, tamanho,
            Path(caminho_original).suffix.lower(), categoria, hash_conteudo, qualidade
        ))

        self.banco_dados.commit()

        print(f"    [✓] Transformado: {nome_original} -> {nome_limpo} (Qualidade: {qualidade:.2f})")
        self.metricas['transformados'] += 1
        self.metricas['processados'] += 1

        return True

    def triar_diretorio(self, diretorio_entrada, diretorio_saida=None):
        """Realiza triagem completa de um diretório"""
        print(f"[ALQUIMIA] Iniciando triagem do diretório: {diretorio_entrada}")

        if not os.path.exists(diretorio_entrada):
            print(f"  [-] Diretório não encontrado: {diretorio_entrada}")
            return False

        # Criar diretório de saída se não existir
        if diretorio_saida:
            os.makedirs(diretorio_saida, exist_ok=True)

        # Processar todos os arquivos no diretório
        arquivos_encontrados = 0
        for root, dirs, files in os.walk(diretorio_entrada):
            for file in files:
                caminho_completo = os.path.join(root, file)

                # Verificar se é arquivo suportado
                extensao = Path(file).suffix.lower()
                if extensao in self.tipos_suportados:
                    self.processar_arquivo(caminho_completo, diretorio_saida)
                    arquivos_encontrados += 1

        print(f"  [✓] Triagem concluída: {arquivos_encontrados} arquivos encontrados")
        return True

    def remover_duplicatas(self):
        """Remove arquivos duplicados com base no hash"""
        print(f"[ALQUIMIA] Removendo duplicatas...")

        cursor = self.banco_dados.cursor()
        cursor.execute("SELECT caminho FROM arquivos WHERE duplicata = 1")
        duplicatas = cursor.fetchall()

        for (caminho,) in duplicatas:
            if os.path.exists(caminho):
                os.remove(caminho)
                print(f"    [>] Duplicata removida: {caminho}")

        print(f"  [✓] {len(duplicatas)} duplicatas removidas")

    def gerar_estatisticas(self):
        """Gera estatísticas da triagem"""
        cursor = self.banco_dados.cursor()

        # Estatísticas gerais
        cursor.execute("SELECT COUNT(*), SUM(tamanho) FROM arquivos")
        total_arquivos, tamanho_total = cursor.fetchone()

        cursor.execute("SELECT categoria, COUNT(*) FROM arquivos GROUP BY categoria")
        categorias = cursor.fetchall()

        print(f"\n[ESTATÍSTICAS ALQUIMIA] - {datetime.now().strftime('%H:%M:%S')}")
        print("="*50)
        print(f"Total de arquivos: {total_arquivos or 0}")
        print(f"Tamanho total: {round((tamanho_total or 0) / 1024 / 1024, 2)} MB")
        print(f"Arquivos processados: {self.metricas['processados']}")
        print(f"Arquivos descartados: {self.metricas['descartados']}")
        print(f"Arquivos transformados: {self.metricas['transformados']}")
        print(f"Duplicatas encontradas: {self.metricas['duplicatas']}")

        print(f"\nDistribuição por categoria:")
        for categoria, quantidade in categorias:
            print(f"  {categoria}: {quantidade} arquivos")

        print("="*50)

    def exportar_catalogo(self, caminho_saida):
        """Exporta catálogo de ativos para arquivo JSON"""
        cursor = self.banco_dados.cursor()
        cursor.execute("""
            SELECT nome_original, nome_limpo, caminho, tamanho, tipo, categoria, qualidade, data_registro
            FROM arquivos ORDER BY categoria, qualidade DESC
        """)

        registros = cursor.fetchall()

        catalogo = []
        for reg in registros:
            catalogo.append({
                'nome_original': reg[0],
                'nome_limpo': reg[1],
                'caminho': reg[2],
                'tamanho': reg[3],
                'tipo': reg[4],
                'categoria': reg[5],
                'qualidade': reg[6],
                'data_registro': reg[7]
            })

        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(catalogo, f, indent=2, ensure_ascii=False)

        print(f"[ALQUIMIA] Catálogo exportado para: {caminho_saida}")

    def executar_operacao_alquimia(self, diretorio_entrada, diretorio_saida):
        """Executa operação completa do Projeto Alquimia"""
        print("\n🧪 INICIANDO OPERAÇÃO ALQUIMIA")
        print("="*60)

        # 1. Realizar triagem
        print(f"[ALQUIMIA] Iniciando triagem de: {diretorio_entrada}")
        self.triar_diretorio(diretorio_entrada, diretorio_saida)

        # 2. Remover duplicatas
        print(f"[ALQUIMIA] Removendo duplicatas...")
        self.remover_duplicatas()

        # 3. Gerar estatísticas
        self.gerar_estatisticas()

        # 4. Exportar catálogo
        self.exportar_catalogo('catalogo_alquimia.json')

        # 5. Registrar métricas
        cursor = self.banco_dados.cursor()
        cursor.execute('''
            INSERT INTO metricas_triagem
            (arquivos_processados, arquivos_descartados, arquivos_transformados, duplicatas_encontradas)
            VALUES (?, ?, ?, ?)
        ''', (
            self.metricas['processados'],
            self.metricas['descartados'],
            self.metricas['transformados'],
            self.metricas['duplicatas']
        ))
        self.banco_dados.commit()

        print("="*60)
        print("🧪 OPERAÇÃO ALQUIMIA CONCLUÍDA COM SUCESSO!")
        print("✨ Dados brutos transformados em Néctar")
        print("📊 Catálogo gerado e métricas registradas")
        print("🔒 Banco de dados atualizado")
        print("="*60)

    def fechar_conexao(self):
        """Fecha a conexão com o banco de dados"""
        if self.banco_dados:
            self.banco_dados.close()

def main():
    """Função principal do sistema Alquimia"""
    print("🧪 CONECTANDO AO PROJETO ALQUIMIA")
    print("⚡ Iniciando motor de triagem de dados...")

    # Criar diretório de exemplo
    os.makedirs('entrada_alquimia', exist_ok=True)

    # Criar arquivos de exemplo
    for i in range(5):
        with open(f'entrada_alquimia/arquivo_negocios_{i}.txt', 'w') as f:
            f.write(f'Conteúdo de negócio do arquivo {i}\nPalavras-chave: negocio, marketing, estrategia\nData: {datetime.now()}')

    with open('entrada_alquimia/arquivo_tecnologia.txt', 'w') as f:
        f.write('Conteúdo técnico\nPython, programação, IA\nData: {datetime.now()}')

    # Iniciar sistema Alquimia
    alquimia = AlquimiaSystem()

    # Executar operação completa
    alquimia.executar_operacao_alquimia('entrada_alquimia', 'saida_alquimia')

    print(f"\n🧠 PROJETO ALQUIMIA OPERACIONAL!")
    print(f"   - Motor de triagem ativado")
    print(f"   - Sistema de categorização funcional")
    print(f"   - Detecção de duplicatas implementada")
    print(f"   - Avaliação de qualidade de ativos")
    print(f"   - Catálogo de Néctar gerado")

    # Fechar conexão
    alquimia.fechar_conexao()

if __name__ == "__main__":
    main()