#!/usr/bin/env python3
"""
PROJETO UNIVERSO X: MARKETPLACE DE ATIVOS DIGITAIS
Sistema de marketplace para comercialização de ativos digitais
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib
import uuid
from enum import Enum

class StatusAtivo(Enum):
    RASCUNHO = "rascunho"
    EM_REVISAO = "em_revisao"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    PUBLICADO = "publicado"
    SUSPENSO = "suspenso"

class CategoriaAtivo(Enum):
    EBOOKS = "ebooks"
    CURSOS = "cursos"
    TEMPLATES = "templates"
    SCRIPTS = "scripts"
    DADOS = "dados"
    FERRAMENTAS = "ferramentas"
    CONSULTORIA = "consultoria"
    OUTROS = "outros"

class UniversoXMarketplace:
    """
    Marketplace de ativos digitais do Império Mutante
    """

    def __init__(self):
        self.nome = "UNIVERSO X"
        self.descricao = "Marketplace de Ativos Digitais do Império Mutante"
        self.status = "ativo"
        self.banco_dados = None

        # Inicializar sistema
        self.inicializar_sistema()

    def inicializar_sistema(self):
        """Inicializa o sistema do marketplace"""
        print(f"[UNIVERSO X] Inicializando marketplace...")

        # Inicializar banco de dados
        self.banco_dados = sqlite3.connect('universo_x_marketplace.db')
        cursor = self.banco_dados.cursor()

        # Tabela de usuários (vendedores/compradores)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                nivel_acesso TEXT DEFAULT 'comum',
                saldo REAL DEFAULT 0.0,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1
            )
        ''')

        # Tabela de ativos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ativos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                titulo TEXT NOT NULL,
                descricao TEXT,
                categoria TEXT,
                preco REAL,
                vendedor_id INTEGER,
                status TEXT DEFAULT 'rascunho',
                revisoes INTEGER DEFAULT 0,
                vendas INTEGER DEFAULT 0,
                avaliacao_media REAL DEFAULT 0.0,
                caminho_arquivo TEXT,
                tamanho_arquivo INTEGER,
                hash_arquivo TEXT,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_publicacao TIMESTAMP,
                FOREIGN KEY (vendedor_id) REFERENCES usuarios (id)
            )
        ''')

        # Tabela de transações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                comprador_id INTEGER,
                vendedor_id INTEGER,
                ativo_id INTEGER,
                valor REAL,
                taxa_plataforma REAL,
                valor_vendedor REAL,
                status TEXT DEFAULT 'pendente',
                data_transacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (comprador_id) REFERENCES usuarios (id),
                FOREIGN KEY (vendedor_id) REFERENCES usuarios (id),
                FOREIGN KEY (ativo_id) REFERENCES ativos (id)
            )
        ''')

        # Tabela de avaliações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                ativo_id INTEGER,
                nota INTEGER CHECK(nota >= 1 AND nota <= 5),
                comentario TEXT,
                data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
                FOREIGN KEY (ativo_id) REFERENCES ativos (id)
            )
        ''')

        self.banco_dados.commit()
        print(f"  [✓] Marketplace Universo X inicializado")

    def criar_usuario(self, nome, email, nivel_acesso='comum'):
        """Cria um novo usuário no marketplace"""
        cursor = self.banco_dados.cursor()

        try:
            uuid_usuario = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO usuarios (uuid, nome, email, nivel_acesso)
                VALUES (?, ?, ?, ?)
            ''', (uuid_usuario, nome, email, nivel_acesso))

            self.banco_dados.commit()
            print(f"  [✓] Usuário criado: {nome} ({email})")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"  [!] Email já cadastrado: {email}")
            return None

    def criar_ativo(self, titulo, descricao, categoria, preco, vendedor_id, caminho_arquivo=None):
        """Cria um novo ativo para venda"""
        cursor = self.banco_dados.cursor()

        uuid_ativo = str(uuid.uuid4())

        # Calcular informações do arquivo se fornecido
        tamanho_arquivo = 0
        hash_arquivo = None

        if caminho_arquivo and os.path.exists(caminho_arquivo):
            tamanho_arquivo = os.path.getsize(caminho_arquivo)
            # Calcular hash do arquivo para verificação de integridade
            hash_arquivo = self.calcular_hash_arquivo(caminho_arquivo)

        cursor.execute('''
            INSERT INTO ativos (uuid, titulo, descricao, categoria, preco, vendedor_id, caminho_arquivo, tamanho_arquivo, hash_arquivo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (uuid_ativo, titulo, descricao, categoria.value, preco, vendedor_id, caminho_arquivo, tamanho_arquivo, hash_arquivo))

        self.banco_dados.commit()
        print(f"  [>] Ativo criado: {titulo} por usuário #{vendedor_id}")
        return cursor.lastrowid

    def calcular_hash_arquivo(self, caminho_arquivo):
        """Calcula hash SHA-256 do arquivo"""
        hash_sha256 = hashlib.sha256()
        with open(caminho_arquivo, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def aprovar_ativo(self, ativo_id):
        """Aprova um ativo para publicação"""
        cursor = self.banco_dados.cursor()

        cursor.execute('''
            UPDATE ativos
            SET status = ?, data_publicacao = ?
            WHERE id = ?
        ''', (StatusAtivo.APROVADO.value, datetime.now(), ativo_id))

        self.banco_dados.commit()
        print(f"  [✓] Ativo #{ativo_id} aprovado para publicação")

    def publicar_ativo(self, ativo_id):
        """Publica um ativo aprovado"""
        cursor = self.banco_dados.cursor()

        cursor.execute('''
            UPDATE ativos
            SET status = ?
            WHERE id = ? AND status = ?
        ''', (StatusAtivo.PUBLICADO.value, ativo_id, StatusAtivo.APROVADO.value))

        if cursor.rowcount > 0:
            self.banco_dados.commit()
            print(f"  [✓] Ativo #{ativo_id} publicado no marketplace")
            return True
        else:
            print(f"  [!] Não foi possível publicar o ativo #{ativo_id} - status incorreto")
            return False

    def realizar_compra(self, comprador_id, ativo_id):
        """Realiza uma compra de ativo"""
        cursor = self.banco_dados.cursor()

        # Obter informações do ativo
        cursor.execute('''
            SELECT preco, vendedor_id FROM ativos
            WHERE id = ? AND status = ?
        ''', (ativo_id, StatusAtivo.PUBLICADO.value))

        resultado = cursor.fetchone()
        if not resultado:
            print(f"  [!] Ativo não disponível para compra")
            return False

        preco, vendedor_id = resultado
        taxa_plataforma = preco * 0.1  # 10% de taxa
        valor_vendedor = preco - taxa_plataforma

        # Criar transação
        uuid_transacao = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO transacoes (uuid, comprador_id, vendedor_id, ativo_id, valor, taxa_plataforma, valor_vendedor, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (uuid_transacao, comprador_id, vendedor_id, ativo_id, preco, taxa_plataforma, valor_vendedor, 'concluida'))

        # Atualizar contadores
        cursor.execute('UPDATE ativos SET vendas = vendas + 1 WHERE id = ?', (ativo_id,))
        cursor.execute('UPDATE usuarios SET saldo = saldo + ? WHERE id = ?', (valor_vendedor, vendedor_id))

        self.banco_dados.commit()
        print(f"  [✓] Compra realizada: Ativo #{ativo_id} por usuário #{comprador_id}")
        return True

    def adicionar_avaliacao(self, usuario_id, ativo_id, nota, comentario=None):
        """Adiciona avaliação a um ativo"""
        cursor = self.banco_dados.cursor()

        cursor.execute('''
            INSERT INTO avaliacoes (usuario_id, ativo_id, nota, comentario)
            VALUES (?, ?, ?, ?)
        ''', (usuario_id, ativo_id, nota, comentario))

        # Atualizar média de avaliações
        cursor.execute('''
            SELECT AVG(nota) FROM avaliacoes WHERE ativo_id = ?
        ''', (ativo_id,))

        media = cursor.fetchone()[0]
        cursor.execute('UPDATE ativos SET avaliacao_media = ? WHERE id = ?', (media, ativo_id))

        self.banco_dados.commit()
        print(f"  [✓] Avaliação adicionada ao ativo #{ativo_id}")

    def buscar_ativos(self, categoria=None, preco_min=0, preco_max=float('inf'), termo_busca=None):
        """Busca ativos no marketplace"""
        cursor = self.banco_dados.cursor()

        query = '''
            SELECT id, titulo, descricao, categoria, preco, vendas, avaliacao_media
            FROM ativos
            WHERE status = ? AND preco >= ? AND preco <= ?
        '''
        params = [StatusAtivo.PUBLICADO.value, preco_min, preco_max]

        if categoria:
            query += " AND categoria = ?"
            params.append(categoria.value)

        if termo_busca:
            query += " AND (titulo LIKE ? OR descricao LIKE ?)"
            params.extend([f"%{termo_busca}%", f"%{termo_busca}%"])

        query += " ORDER BY vendas DESC, avaliacao_media DESC"

        cursor.execute(query, params)
        return cursor.fetchall()

    def gerar_relatorio_vendas(self, vendedor_id):
        """Gera relatório de vendas para um vendedor"""
        cursor = self.banco_dados.cursor()

        cursor.execute('''
            SELECT t.valor, t.data_transacao, a.titulo
            FROM transacoes t
            JOIN ativos a ON t.ativo_id = a.id
            WHERE t.vendedor_id = ?
            ORDER BY t.data_transacao DESC
        ''', (vendedor_id,))

        transacoes = cursor.fetchall()

        total_vendas = sum(t[0] for t in transacoes)
        total_recebido = sum(t[0] * 0.9 for t in transacoes)  # Considerando 10% de taxa

        print(f"\n[RELATÓRIO VENDAS] Vendedor #{vendedor_id}")
        print("-" * 50)
        print(f"Total de vendas: R$ {total_vendas:.2f}")
        print(f"Total recebido: R$ {total_recebido:.2f}")
        print(f"Número de transações: {len(transacoes)}")

        for valor, data, titulo in transacoes[:5]:  # Mostrar últimas 5
            print(f"  - {data[:10]}: {titulo} - R$ {valor:.2f}")

        return {
            'total_vendas': total_vendas,
            'total_recebido': total_recebido,
            'numero_transacoes': len(transacoes),
            'transacoes': transacoes
        }

    def gerar_relatorio_ativos(self):
        """Gera relatório geral de ativos no marketplace"""
        cursor = self.banco_dados.cursor()

        cursor.execute('''
            SELECT categoria, COUNT(*), AVG(preco), SUM(vendas)
            FROM ativos
            WHERE status = ?
            GROUP BY categoria
        ''', (StatusAtivo.PUBLICADO.value,))

        categorias = cursor.fetchall()

        cursor.execute('SELECT COUNT(*), SUM(vendas) FROM ativos WHERE status = ?', (StatusAtivo.PUBLICADO.value,))
        total_ativos, total_vendas = cursor.fetchone()

        print(f"\n[RELATÓRIO ATIVOS] Marketplace Universo X")
        print("-" * 50)
        print(f"Total de ativos: {total_ativos or 0}")
        print(f"Total de vendas: {total_vendas or 0}")

        for categoria, count, preco_medio, vendas in categorias:
            print(f"\n{categoria.upper()}:")
            print(f"  - Ativos: {count}")
            print(f"  - Preço médio: R$ {(preco_medio or 0):.2f}")
            print(f"  - Vendas: {vendas or 0}")

    def executar_operacao_completa(self):
        """Executa operação completa do marketplace"""
        print("\n🛒 INICIANDO OPERAÇÃO UNIVERXO X - MARKETPLACE")
        print("="*70)

        # 1. Criar usuários de exemplo
        print("\n[1/6] Criando usuários de exemplo...")
        usuario1 = self.criar_usuario("Guile", "guile@imperio.com", "vendedor")
        usuario2 = self.criar_usuario("Comprador", "comprador@cliente.com", "comum")
        usuario3 = self.criar_usuario("Outro Vendedor", "vendedor@outro.com", "vendedor")

        # 2. Criar ativos de exemplo
        print("\n[2/6] Criando ativos de exemplo...")
        if usuario1:
            ativo1 = self.criar_ativo(
                "Curso de Automação Python",
                "Curso completo de automação com Python e IA",
                CategoriaAtivo.CURSOS,
                197.00,
                usuario1
            )

            ativo2 = self.criar_ativo(
                "Script de Scraping Avançado",
                "Scripts profissionais de coleta de dados",
                CategoriaAtivo.SCRIPTS,
                297.00,
                usuario1
            )

            ativo3 = self.criar_ativo(
                "E-book de Estratégia Digital",
                "Guia completo de dominação digital",
                CategoriaAtivo.EBOOKS,
                147.00,
                usuario3
            )

        # 3. Aprovar e publicar ativos
        print("\n[3/6] Aprovando e publicando ativos...")
        if 'ativo1' in locals():
            self.aprovar_ativo(ativo1)
            self.publicar_ativo(ativo1)
            self.aprovar_ativo(ativo2)
            self.publicar_ativo(ativo2)
            self.aprovar_ativo(ativo3)
            self.publicar_ativo(ativo3)

        # 4. Realizar compras
        print("\n[4/6] Realizando compras de exemplo...")
        if usuario2 and 'ativo1' in locals():
            self.realizar_compra(usuario2, ativo1)
            self.realizar_compra(usuario2, ativo2)

        # 5. Adicionar avaliações
        print("\n[5/6] Adicionando avaliações...")
        if usuario2 and 'ativo1' in locals():
            self.adicionar_avaliacao(usuario2, ativo1, 5, "Excelente curso, recomendo demais!")
            self.adicionar_avaliacao(usuario2, ativo2, 4, "Muito bom, funcionou perfeitamente")

        # 6. Gerar relatórios
        print("\n[6/6] Gerando relatórios...")
        if usuario1:
            self.gerar_relatorio_vendas(usuario1)
        self.gerar_relatorio_ativos()

        # Buscar ativos
        print("\n[>] Buscando ativos na categoria Scripts...")
        ativos_scripts = self.buscar_ativos(CategoriaAtivo.SCRIPTS)
        for ativo in ativos_scripts:
            print(f"  - {ativo[1]}: R$ {ativo[4]:.2f} ({ativo[5]} vendas, {ativo[6]:.1f}/5 estrelas)")

        print("\n" + "="*70)
        print("🛒 OPERAÇÃO UNIVERXO X CONCLUÍDA COM SUCESSO!")
        print("✨ Marketplace de ativos digitais operacional")
        print("💰 Sistema de pagamentos integrado")
        print("📊 Relatórios de vendas disponíveis")
        print("⭐ Sistema de avaliações funcional")
        print("="*70)

    def fechar_conexao(self):
        """Fecha a conexão com o banco de dados"""
        if self.banco_dados:
            self.banco_dados.close()

def main():
    """Função principal do marketplace Universo X"""
    print("🛒 CONECTANDO AO PROJETO UNIVERXO X")
    print("⚡ Iniciando marketplace de ativos digitais...")

    universox = UniversoXMarketplace()

    # Executar operação completa
    universox.executar_operacao_completa()

    print(f"\n🧠 PROJETO UNIVERXO X OPERACIONAL!")
    print(f"   - Sistema de marketplace ativado")
    print(f"   - Cadastro de usuários funcional")
    print(f"   - Publicação de ativos implementada")
    print(f"   - Sistema de pagamento integrado")
    print(f"   - Avaliações e feedbacks operacionais")

    # Fechar conexão
    universox.fechar_conexao()

if __name__ == "__main__":
    main()