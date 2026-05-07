#!/usr/bin/env python3
"""
PAINEL DE CONTROLE DO IMPÉRIO MUTANTE
Sistema central de monitoramento e coordenação de todos os componentes
"""

import os
import json
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
import sqlite3

class PainelControleImperio:
    """
    Painel de controle central do Império Mutante
    Coordena e monitora todos os sistemas
    """

    def __init__(self):
        self.nome = "PAINEL DE CONTROLE IMPÉRIO MUTANTE"
        self.descricao = "Sistema Central de Monitoramento e Coordenação"
        self.status = "ativo"
        self.sistemas = {}
        self.metricas_globais = {
            'sistemas_ativos': 0,
            'operacoes_totais': 0,
            'falhas_totais': 0,
            'uptime_total': 0
        }
        self.historico_operacoes = []

        # Inicializar sistema
        self.inicializar_painel()

    def inicializar_painel(self):
        """Inicializa o painel de controle"""
        print(f"[PAINEL] Inicializando painel de controle do Império...")

        # Criar estrutura de pastas do painel
        pastas_painel = [
            "logs_painel",
            "relatorios",
            "backup_config",
            "monitoramento"
        ]

        for pasta in pastas_painel:
            caminho = Path(pasta)
            caminho.mkdir(exist_ok=True)

        # Inicializar banco de dados de operações
        self.banco_operacoes = sqlite3.connect('operacoes_imperio.db')
        cursor = self.banco_operacoes.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sistema TEXT NOT NULL,
                operacao TEXT NOT NULL,
                status TEXT,
                inicio TIMESTAMP,
                fim TIMESTAMP,
                duracao REAL,
                resultado TEXT
            )
        ''')

        self.banco_operacoes.commit()
        print(f"[PAINEL] Painel de controle inicializado com sucesso!")

    def registrar_sistema(self, nome, descricao, script_path, versao="1.0"):
        """Registra um sistema no painel de controle"""
        self.sistemas[nome] = {
            "nome": nome,
            "descricao": descricao,
            "script_path": script_path,
            "versao": versao,
            "status": "registrado",
            "ultimo_inicio": None,
            "uptime": 0,
            "falhas": 0,
            "execucoes": 0
        }

        print(f"  [✓] Sistema registrado: {nome} - {descricao}")

    def inicializar_sistemas(self):
        """Inicializa todos os sistemas do Império"""
        print(f"\n[INICIALIZAÇÃO] Iniciando sistemas do Império...")

        # Registrar todos os sistemas do Império
        self.registrar_sistema(
            "ALQUIMIA",
            "Motor de triagem de dados",
            "py/alquimia_system.py"
        )

        self.registrar_sistema(
            "SOMBRA-V1",
            "Sistema de ofuscação e proteção",
            "py/sombra_v1_system.py"
        )

        self.registrar_sistema(
            "CAMALEÃO-V1",
            "Sistema de invisibilidade e anonimato",
            "py/camaleao_v1_system.py"
        )

        self.registrar_sistema(
            "AETHER-V1",
            "Sistema de organização e armazenamento",
            "py/aether_v1_system.py"
        )

        self.registrar_sistema(
            "UNIVERSO-X",
            "Marketplace de ativos digitais",
            "py/universo_x_marketplace.py"
        )

        self.registrar_sistema(
            "CLOUD-SEARCH",
            "Sistema de busca privada",
            "py/cloud_search_system.py"
        )

        # Atualizar métricas
        self.metricas_globais['sistemas_ativos'] = len(self.sistemas)

    def executar_sistema(self, nome_sistema, timeout=300):
        """Executa um sistema específico"""
        if nome_sistema not in self.sistemas:
            print(f"[PAINEL] Sistema {nome_sistema} não encontrado")
            return False

        sistema = self.sistemas[nome_sistema]
        print(f"[PAINEL] Executando {sistema['nome']}...")

        inicio_execucao = time.time()
        self.sistemas[nome_sistema]["ultimo_inicio"] = datetime.now()

        try:
            # Executar o script do sistema
            processo = subprocess.run([
                sys.executable, sistema['script_path']
            ], capture_output=True, text=True, timeout=timeout)

            duracao = time.time() - inicio_execucao

            # Registrar operação
            self.registrar_operacao(
                nome_sistema,
                "execucao",
                "sucesso" if processo.returncode == 0 else "falha",
                inicio_execucao,
                duracao,
                processo.stdout if processo.returncode == 0 else processo.stderr
            )

            if processo.returncode == 0:
                print(f"  [✓] {sistema['nome']} executado com sucesso")
                self.sistemas[nome_sistema]["execucoes"] += 1
                self.metricas_globais['operacoes_totais'] += 1
                return True
            else:
                print(f"  [✗] {sistema['nome']} falhou: {processo.stderr}")
                self.sistemas[nome_sistema]["falhas"] += 1
                self.metricas_globais['falhas_totais'] += 1
                return False

        except subprocess.TimeoutExpired:
            print(f"  [!] {sistema['nome']} excedeu tempo limite")
            self.registrar_operacao(
                nome_sistema,
                "execucao",
                "timeout",
                inicio_execucao,
                timeout,
                "Timeout expirado"
            )
            self.sistemas[nome_sistema]["falhas"] += 1
            self.metricas_globais['falhas_totais'] += 1
            return False
        except Exception as e:
            print(f"  [!] Erro ao executar {sistema['nome']}: {e}")
            self.registrar_operacao(
                nome_sistema,
                "execucao",
                "erro",
                inicio_execucao,
                time.time() - inicio_execucao,
                str(e)
            )
            self.sistemas[nome_sistema]["falhas"] += 1
            self.metricas_globais['falhas_totais'] += 1
            return False

    def executar_fluxo_padrao(self):
        """Executa o fluxo padrão do Império Mutante"""
        print(f"\n🔄 EXECUTANDO FLUXO PADRÃO DO IMPÉRIO")
        print("="*60)

        ordem_execucao = [
            "ALQUIMIA",      # Primeiro: triagem de dados
            "SOMBRA-V1",     # Depois: proteção e ofuscação
            "CLOUD-SEARCH",  # Depois: indexação e busca
            "AETHER-V1",     # Depois: organização
            "CAMALEÃO-V1",   # Depois: anonimato
            "UNIVERSO-X"     # Por último: comercialização
        ]

        resultados = {}
        for sistema in ordem_execucao:
            print(f"\n[>] Executando {sistema}...")
            sucesso = self.executar_sistema(sistema)
            resultados[sistema] = sucesso

            if not sucesso:
                print(f"  [!] Falha crítica em {sistema}, continuando com próximos...")

        print(f"\n{'='*60}")
        print(f"📊 RESULTADOS DO FLUXO PADRÃO:")
        for sistema, sucesso in resultados.items():
            status = "✅" if sucesso else "❌"
            print(f"  {status} {sistema}: {'Sucesso' if sucesso else 'Falha'}")

        return resultados

    def registrar_operacao(self, sistema, operacao, status, inicio, duracao, resultado):
        """Registra uma operação no banco de dados"""
        cursor = self.banco_operacoes.cursor()

        cursor.execute('''
            INSERT INTO operacoes (sistema, operacao, status, inicio, fim, duracao, resultado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            sistema,
            operacao,
            status,
            datetime.fromtimestamp(inicio).isoformat(),
            datetime.now().isoformat(),
            duracao,
            resultado[:500]  # Limitar tamanho do resultado
        ))

        self.banco_operacoes.commit()

    def monitorar_sistemas(self, intervalo=60):
        """Monitora os sistemas em loop"""
        print(f"[MONITOR] Iniciando monitoramento (intervalo: {intervalo}s)...")

        try:
            while True:
                print(f"\n[MONITOR] Status dos sistemas - {datetime.now().strftime('%H:%M:%S')}")

                for nome, info in self.sistemas.items():
                    print(f"  {nome}: {info['status']} | Execuções: {info['execucoes']} | Falhas: {info['falhas']}")

                print(f"  Métricas globais: Operações={self.metricas_globais['operacoes_totais']}, Falhas={self.metricas_globais['falhas_totais']}")

                time.sleep(intervalo)

        except KeyboardInterrupt:
            print(f"\n[MONITOR] Monitoramento interrompido pelo usuário")

    def gerar_relatorio_completo(self):
        """Gera relatório completo do Império"""
        print(f"\n[RELATÓRIO COMPLETO] - {datetime.now().strftime('%H:%M:%S')}")
        print("="*70)
        print(f"Sistema: {self.nome}")
        print(f"Status: {self.status}")
        print(f"Data de início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"\nSISTEMAS REGISTRADOS: {len(self.sistemas)}")
        for nome, info in self.sistemas.items():
            print(f"  • {nome} v{info['versao']}: {info['descricao']}")
            print(f"    Execuções: {info['execucoes']}, Falhas: {info['falhas']}")
            print(f"    Último início: {info['ultimo_inicio'].strftime('%H:%M:%S') if info['ultimo_inicio'] else 'Nunca'}")

        print(f"\nMÉTRICAS GLOBAIS:")
        print(f"  • Sistemas ativos: {self.metricas_globais['sistemas_ativos']}")
        print(f"  • Operações totais: {self.metricas_globais['operacoes_totais']}")
        print(f"  • Falhas totais: {self.metricas_globais['falhas_totais']}")
        print(f"  • Taxa de sucesso: {((self.metricas_globais['operacoes_totais'] - self.metricas_globais['falhas_totais']) / self.metricas_globais['operacoes_totais'] * 100) if self.metricas_globais['operacoes_totais'] > 0 else 0:.1f}%")

        # Estatísticas das operações recentes
        cursor = self.banco_operacoes.cursor()
        cursor.execute("SELECT sistema, status, COUNT(*) FROM operacoes GROUP BY sistema, status")
        estatisticas = cursor.fetchall()

        print(f"\nESTATÍSTICAS DAS OPERAÇÕES:")
        for sistema, status, count in estatisticas:
            print(f"  • {sistema} - {status}: {count}")

        print("="*70)

    def modo_operacao_automatica(self, intervalo_ciclo=3600):
        """Modo de operação automática contínua"""
        print(f"\n🤖 INICIANDO MODO OPERAÇÃO AUTOMÁTICA")
        print(f"Intervalo entre ciclos: {intervalo_ciclo/60:.1f} minutos")

        ciclo = 0
        try:
            while True:
                ciclo += 1
                print(f"\n[CYCLE #{ciclo}] Iniciando ciclo automático - {datetime.now().strftime('%H:%M:%S')}")

                # Executar fluxo padrão
                self.executar_fluxo_padrao()

                # Gerar relatório parcial
                print(f"[CYCLE #{ciclo}] Gerando relatório parcial...")
                self.gerar_relatorio_completo()

                print(f"[CYCLE #{ciclo}] Aguardando {intervalo_ciclo} segundos até próximo ciclo...")
                time.sleep(intervalo_ciclo)

        except KeyboardInterrupt:
            print(f"\n🤖 Modo operação automática interrompido")
            print(f"Total de ciclos executados: {ciclo}")

    def exportar_configuracao(self, caminho_saida="config_imperio.json"):
        """Exporta a configuração do painel"""
        config = {
            "nome": self.nome,
            "descricao": self.descricao,
            "sistemas": self.sistemas,
            "metricas_globais": self.metricas_globais,
            "data_exportacao": datetime.now().isoformat()
        }

        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False, default=str)

        print(f"[PAINEL] Configuração exportada para: {caminho_saida}")

    def executar_operacao_personalizada(self, sistemas_selecionados, modo_assincrono=False):
        """Executa operação personalizada com sistemas específicos"""
        print(f"\n⚙️ EXECUTANDO OPERAÇÃO PERSONALIZADA")
        print(f"Sistemas selecionados: {', '.join(sistemas_selecionados)}")
        print(f"Modo assíncrono: {modo_assincrono}")

        if modo_assincrono:
            threads = []
            for sistema in sistemas_selecionados:
                thread = threading.Thread(target=self.executar_sistema, args=(sistema,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()
        else:
            for sistema in sistemas_selecionados:
                self.executar_sistema(sistema)

    def fechar_conexao(self):
        """Fecha a conexão com bancos de dados"""
        if hasattr(self, 'banco_operacoes'):
            self.banco_operacoes.close()

def main():
    """Função principal do painel de controle"""
    print("🎛️ CONECTANDO AO PAINEL DE CONTROLE DO IMPÉRIO MUTANTE")
    print("⚡ Iniciando sistema central de monitoramento...")

    painel = PainelControleImperio()

    # Inicializar todos os sistemas
    painel.inicializar_sistemas()

    # Executar fluxo padrão
    resultados = painel.executar_fluxo_padrao()

    # Gerar relatório completo
    painel.gerar_relatorio_completo()

    # Exportar configuração
    painel.exportar_configuracao()

    print(f"\n🧠 PAINEL DE CONTROLE OPERACIONAL!")
    print(f"   - Todos os sistemas integrados e monitorados")
    print(f"   - Fluxo automático de dados estabelecido")
    print(f"   - Sistema de relatórios funcional")
    print(f"   - Banco de dados de operações ativo")
    print(f"   - Modo operação automática disponível")

    print(f"\n🔧 OPÇÕES DISPONÍVEIS:")
    print(f"   - Monitoramento contínuo: painel.monitorar_sistemas(intervalo=60)")
    print(f"   - Modo automático: painel.modo_operacao_automatica(intervalo_ciclo=3600)")
    print(f"   - Operação personalizada: painel.executar_operacao_personalizada(['ALQUIMIA', 'SOMBRA-V1'])")
    print(f"   - Relatório completo: painel.gerar_relatorio_completo()")

    # Fechar conexão
    painel.fechar_conexao()

if __name__ == "__main__":
    main()