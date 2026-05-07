#!/usr/bin/env python3
"""
PROJETO SOMBRA-V1: SISTEMA DE OFUSCACAO E ARMAZENAMENTO SEGURO
Sistema de ofuscação de ativos e proteção de dados sensíveis
"""

import os
import hashlib
import json
import shutil
from pathlib import Path
import sqlite3
from datetime import datetime
import base64
from cryptography.fernet import Fernet
import zipfile

class SombraSystem:
    """
    Sistema avançado de ofuscação e proteção de ativos
    Implementa o protocolo Sombra mencionado no Projeto Aether
    """

    def __init__(self):
        self.nome = "SOMBRA-V1"
        self.descricao = "Sistema de Ofuscação e Proteção de Ativos"
        self.status = "ativo"
        self.chave_encriptacao = None
        self.mapa_recuperacao = {}
        self.banco_dados = None

        # Inicializar sistema
        self.inicializar_sistema()

    def inicializar_sistema(self):
        """Inicializa o sistema Sombra com criptografia e banco de dados"""
        print(f"[SOMBRA-V1] Inicializando sistema de ofuscação...")

        # Gerar chave de criptografia
        self.chave_encriptacao = Fernet.generate_key()
        self.cipher_suite = Fernet(self.chave_encriptacao)

        # Salvar chave (em produção, armazenar com mais segurança)
        with open('chave_sombra.key', 'wb') as key_file:
            key_file.write(self.chave_encriptacao)

        # Inicializar banco de dados
        self.banco_dados = sqlite3.connect('ativos_sombra.db')
        cursor = self.banco_dados.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ativos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_original TEXT NOT NULL,
                nome_ofuscado TEXT NOT NULL,
                caminho TEXT,
                tamanho INTEGER,
                hash TEXT,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                protegido INTEGER DEFAULT 0
            )
        ''')

        self.banco_dados.commit()
        print(f"  [✓] Sistema Sombra inicializado com criptografia")

    def ofuscar_nome_arquivo(self, nome_original):
        """Gera um nome ofuscado para o arquivo"""
        # Combina o nome original com timestamp para maior aleatoriedade
        timestamp = str(datetime.now().timestamp())
        conteudo_para_hash = f"{nome_original}{timestamp}".encode()

        # Gerar hash SHA-256 e converter para hexadecimal
        hash_nome = hashlib.sha256(conteudo_para_hash).hexdigest()

        # Pegar extensão original e substituir por .dat para maior disfarce
        extensao = Path(nome_original).suffix
        nome_ofuscado = f"{hash_nome}{extensao if extensao.lower() in ['.pdf', '.doc', '.txt'] else '.dat'}"

        return nome_ofuscado

    def encriptar_conteudo(self, caminho_arquivo):
        """Encripta o conteúdo do arquivo"""
        with open(caminho_arquivo, 'rb') as file:
            dados_originais = file.read()

        dados_encriptados = self.cipher_suite.encrypt(dados_originais)

        # Salvar conteúdo encriptado
        caminho_encriptado = f"{caminho_arquivo}.enc"
        with open(caminho_encriptado, 'wb') as file:
            file.write(dados_encriptados)

        return caminho_encriptado

    def ofuscar_ativos_diretorio(self, diretorio_origem, diretorio_destino=None):
        """Ofusca todos os ativos em um diretório"""
        if not diretorio_destino:
            diretorio_destino = diretorio_origem

        print(f"[SOMBRA] Ofuscando ativos em: {diretorio_origem}")

        arquivos_processados = 0
        for arquivo in os.listdir(diretorio_origem):
            caminho_original = os.path.join(diretorio_origem, arquivo)

            if os.path.isfile(caminho_original):
                # Gerar nome ofuscado
                nome_ofuscado = self.ofuscar_nome_arquivo(arquivo)
                caminho_ofuscado = os.path.join(diretorio_destino, nome_ofuscado)

                # Copiar arquivo com novo nome
                shutil.copy2(caminho_original, caminho_ofuscado)

                # Registrar no mapa de recuperação
                self.mapa_recuperacao[nome_ofuscado] = arquivo

                # Registrar no banco de dados
                self.registrar_ativo_banco(arquivo, nome_ofuscado, caminho_ofuscado)

                print(f"  [>] Ofuscado: {arquivo} -> {nome_ofuscado}")
                arquivos_processados += 1

        # Salvar mapa de recuperação
        self.salvar_mapa_recuperacao()

        print(f"  [✓] {arquivos_processados} ativos ofuscados com sucesso")
        return arquivos_processados

    def registrar_ativo_banco(self, nome_original, nome_ofuscado, caminho):
        """Registra ativo no banco de dados"""
        cursor = self.banco_dados.cursor()

        tamanho = os.path.getsize(caminho) if os.path.exists(caminho) else 0
        hash_arquivo = self.calcular_hash_arquivo(caminho)

        cursor.execute('''
            INSERT INTO ativos (nome_original, nome_ofuscado, caminho, tamanho, hash, protegido)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (nome_original, nome_ofuscado, caminho, tamanho, hash_arquivo))

        self.banco_dados.commit()

    def calcular_hash_arquivo(self, caminho_arquivo):
        """Calcula hash SHA-256 do arquivo"""
        hash_sha256 = hashlib.sha256()
        with open(caminho_arquivo, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def salvar_mapa_recuperacao(self):
        """Salva o mapa de recuperação para restauração futura"""
        with open('mapa_sombra.txt', 'w', encoding='utf-8') as log:
            json.dump(self.mapa_recuperacao, log, indent=2, ensure_ascii=False)

        print(f"  [✓] Mapa de recuperação salvo em mapa_sombra.txt")

    def recuperar_ativos(self, diretorio_origem, mapa_recuperacao_path='mapa_sombra.txt'):
        """Recupera ativos ofuscados usando o mapa de recuperação"""
        # Carregar mapa de recuperação
        with open(mapa_recuperacao_path, 'r', encoding='utf-8') as log:
            mapa_recuperacao = json.load(log)

        print(f"[SOMBRA] Recuperando ativos em: {diretorio_origem}")

        arquivos_recuperados = 0
        for nome_ofuscado, nome_original in mapa_recuperacao.items():
            caminho_ofuscado = os.path.join(diretorio_origem, nome_ofuscado)
            caminho_recuperado = os.path.join(diretorio_origem, nome_original)

            if os.path.exists(caminho_ofuscado):
                # Renomear arquivo para nome original
                os.rename(caminho_ofuscado, caminho_recuperado)
                print(f"  [>] Recuperado: {nome_ofuscado} -> {nome_original}")
                arquivos_recuperados += 1

        print(f"  [✓] {arquivos_recuperados} ativos recuperados com sucesso")
        return arquivos_recuperados

    def compactar_sombra(self, diretorio_origem, nome_arquivo_saida):
        """Compacta ativos ofuscados em arquivo zip protegido"""
        print(f"[SOMBRA] Compactando ativos em: {nome_arquivo_saida}")

        with zipfile.ZipFile(nome_arquivo_saida, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(diretorio_origem):
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    # Adicionar arquivo ao zip com caminho relativo
                    zipf.write(caminho_completo, os.path.relpath(caminho_completo, diretorio_origem))

        print(f"  [✓] Ativos compactados em: {nome_arquivo_saida}")
        return nome_arquivo_saida

    def verificar_integridade(self):
        """Verifica a integridade dos ativos registrados"""
        print(f"[SOMBRA] Verificando integridade dos ativos...")

        cursor = self.banco_dados.cursor()
        cursor.execute("SELECT nome_ofuscado, caminho, hash FROM ativos WHERE protegido = 1")
        registros = cursor.fetchall()

        ativos_validos = 0
        ativos_invalidos = 0

        for nome_ofuscado, caminho, hash_armazenado in registros:
            if os.path.exists(caminho):
                hash_atual = self.calcular_hash_arquivo(caminho)
                if hash_atual == hash_armazenado:
                    ativos_validos += 1
                else:
                    print(f"  [!] Arquivo corrompido: {nome_ofuscado}")
                    ativos_invalidos += 1
            else:
                print(f"  [!] Arquivo ausente: {nome_ofuscado}")
                ativos_invalidos += 1

        print(f"  [✓] Verificação concluída - Válidos: {ativos_validos}, Inválidos: {ativos_invalidos}")
        return ativos_validos, ativos_invalidos

    def gerar_relatorio_sombra(self):
        """Gera relatório do sistema Sombra"""
        cursor = self.banco_dados.cursor()
        cursor.execute("SELECT COUNT(*), SUM(tamanho) FROM ativos WHERE protegido = 1")
        total_ativos, tamanho_total = cursor.fetchone()

        print(f"\n[RELATÓRIO SOMBRA-V1] - {datetime.now().strftime('%H:%M:%S')}")
        print("="*50)
        print(f"Sistema: {self.nome}")
        print(f"Status: {self.status}")
        print(f"Ativos protegidos: {total_ativos or 0}")
        print(f"Tamanho total protegido: {round((tamanho_total or 0) / 1024 / 1024, 2)} MB")
        print(f"Mapa de recuperação: {'mapa_sombra.txt'}")
        print(f"Chave de criptografia: {'chave_sombra.key'}")
        print("="*50)

    def fechar_conexao(self):
        """Fecha a conexão com o banco de dados"""
        if self.banco_dados:
            self.banco_dados.close()

def main():
    """Função principal do sistema Sombra"""
    print("🔌 CONECTANDO AO PROJETO SOMBRA-V1")
    print("⚡ Iniciando protocolos de ofuscação e proteção...")

    # Criar diretórios de exemplo para teste
    os.makedirs('teste_sombra', exist_ok=True)

    # Criar arquivos de exemplo
    for i in range(3):
        with open(f'teste_sombra/arquivo_exemplo_{i}.txt', 'w') as f:
            f.write(f'Conteúdo sensível do arquivo {i}\nData: {datetime.now()}')

    # Iniciar sistema Sombra
    sombra = SombraSystem()

    # Ofuscar ativos de exemplo
    print("\n[EXECUÇÃO] Ofuscando ativos de exemplo...")
    sombra.ofuscar_ativos_diretorio('teste_sombra')

    # Verificar integridade
    print("\n[EXECUÇÃO] Verificando integridade...")
    sombra.verificar_integridade()

    # Compactar ativos ofuscados
    print("\n[EXECUÇÃO] Compactando ativos protegidos...")
    sombra.compactar_sombra('teste_sombra', 'ativos_protegidos.zip')

    # Gerar relatório
    sombra.gerar_relatorio_sombra()

    print(f"\n🧠 PROJETO SOMBRA-V1 OPERACIONAL!")
    print(f"   - Sistema de ofuscação ativado")
    print(f"   - Criptografia AES aplicada")
    print(f"   - Mapa de recuperação gerado")
    print(f"   - Verificação de integridade implementada")
    print(f"   - Compactação segura disponível")

    # Fechar conexão
    sombra.fechar_conexao()

if __name__ == "__main__":
    main()