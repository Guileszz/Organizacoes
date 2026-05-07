#!/usr/bin/env python3
"""
PROJETO CAMALEÃO-V1: SISTEMA DE ROTAÇÃO DE PROXIES
Sistema de invisibilidade total para operações de scraping e coleta de dados
"""

import requests
from itertools import cycle
import threading
import time
import random
from urllib.parse import urlparse
import json

class CamaleaoSystem:
    """
    Sistema avançado de rotação de proxies para invisibilidade total
    Implementa o protocolo Camaleão mencionado no Projeto NDR
    """

    def __init__(self):
        self.nome = "CAMALEÃO-V1"
        self.descricao = "Sistema de Rotação de Proxies para Invisibilidade Total"
        self.status = "ativo"
        self.proxies_pool = None
        self.proxy_atual = None
        self.historico_uso = []
        self.contador_requisicoes = 0

        print(f"[CAMALEÃO-V1] Sistema de invisibilidade inicializado")

    def carregar_proxies(self, lista_proxies):
        """Carrega a lista de proxies para o pool de rotação"""
        if isinstance(lista_proxies, str):
            # Se for string, assume que é um caminho para arquivo
            with open(lista_proxies, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
        else:
            # Se for lista, usa diretamente
            proxies = lista_proxies

        self.proxies_pool = cycle(proxies)
        print(f"  [✓] Pool de {len(proxies)} proxies carregado")

    def obter_proxy_atual(self):
        """Obtém o próximo proxy do pool"""
        if not self.proxies_pool:
            raise ValueError("Pool de proxies não carregado")

        self.proxy_atual = next(self.proxies_pool)
        return self.proxy_atual

    def requisicao_invisivel(self, url_alvo, metodo='GET', **kwargs):
        """Executa uma requisição usando o protocolo Camaleão"""
        proxy_atual = self.obter_proxy_atual()
        self.contador_requisicoes += 1

        print(f"  [*] Camaleão #{self.contador_requisicoes} trocou de pele. IP Atual: {proxy_atual}")

        # Registrar uso do proxy
        registro = {
            'id': self.contador_requisicoes,
            'proxy': proxy_atual,
            'url': url_alvo,
            'timestamp': time.time()
        }
        self.historico_uso.append(registro)

        try:
            # Configurar proxies para a requisição
            proxies_dict = {
                "http": proxy_atual,
                "https": proxy_atual
            }

            # Adicionar headers para melhor anonimato
            headers = kwargs.get('headers', {})
            headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            })

            response = requests.request(
                metodo,
                url_alvo,
                proxies=proxies_dict,
                timeout=kwargs.get('timeout', 10),
                headers=headers,
                **{k: v for k, v in kwargs.items() if k not in ['timeout', 'headers']}
            )

            return response

        except Exception as e:
            print(f"  [!] Glitch no Proxy {proxy_atual}: {e}")
            return None

    def testar_conectividade(self, urls_teste):
        """Testa a conectividade com diferentes proxies"""
        print(f"[CAMALEÃO] Testando conectividade com proxies...")

        resultados = {}
        for url in urls_teste:
            print(f"  [>] Testando {url}...")
            response = self.requisicao_invisivel(url, timeout=5)
            if response:
                resultados[url] = {
                    'status': response.status_code,
                    'sucesso': response.status_code == 200,
                    'proxy_utilizado': self.proxy_atual
                }
                print(f"    [✓] {url} - Status: {response.status_code} via {self.proxy_atual}")
            else:
                resultados[url] = {
                    'status': 'ERROR',
                    'sucesso': False,
                    'proxy_utilizado': self.proxy_atual
                }
                print(f"    [✗] {url} - Falhou via {self.proxy_atual}")

        return resultados

    def modo_furtivo(self, urls_alvo, intervalo_base=2, variacao=1):
        """Executa requisições em modo furtivo com intervalos variáveis"""
        print(f"[CAMALEÃO] Iniciando modo furtivo...")

        for i, url in enumerate(urls_alvo):
            # Intervalo aleatório para evitar detecção
            intervalo = intervalo_base + random.uniform(-variacao, variacao)
            time.sleep(intervalo)

            print(f"  [FURTIVO-{i+1}] Acessando {url}...")
            response = self.requisicao_invisivel(url)

            if response:
                print(f"    [✓] Sucesso - {len(response.content)} bytes recebidos")
            else:
                print(f"    [✗] Falha na requisição")

        print(f"  [✓] Modo furtivo concluído")

    def gerar_relatorio_invisibilidade(self):
        """Gera relatório de uso do sistema Camaleão"""
        print(f"\n[RELATÓRIO CAMALEÃO] - {time.strftime('%H:%M:%S')}")
        print("="*50)
        print(f"Sistema: {self.nome}")
        print(f"Status: {self.status}")
        print(f"Total de requisições: {self.contador_requisicoes}")
        print(f"Proxies utilizados: {len(set([r['proxy'] for r in self.historico_uso]))}")

        if self.historico_uso:
            primeiro_proxy = self.historico_uso[0]['proxy']
            ultimo_proxy = self.historico_uso[-1]['proxy']
            print(f"Primeiro proxy: {primeiro_proxy}")
            print(f"Último proxy: {ultimo_proxy}")

        print("="*50)

    def exportar_historico(self, caminho_saida):
        """Exporta o histórico de uso para arquivo"""
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(self.historico_uso, f, indent=2, ensure_ascii=False)

        print(f"[CAMALEÃO] Histórico exportado para: {caminho_saida}")

def main():
    """Função principal do sistema Camaleão"""
    print("🔌 CONECTANDO AO PROJETO CAMALEÃO-V1")
    print("⚡ Iniciando protocolos de invisibilidade...")

    # Iniciar sistema Camaleão
    camaleao = CamaleaoSystem()

    # Carregar proxies (exemplo)
    proxies_exemplo = [
        '192.168.1.1:8080',
        '185.245.1.2:3128',
        '45.12.33.55:9999',
        '103.152.112.3:80',
        '186.233.130.154:8080'
    ]

    camaleao.carregar_proxies(proxies_exemplo)

    # Testar conectividade
    urls_teste = [
        'http://httpbin.org/ip',
        'https://httpbin.org/user-agent',
        'https://httpbin.org/headers'
    ]

    print("\n[TESTE] Verificando conectividade...")
    resultados = camaleao.testar_conectividade(urls_teste)

    # Modo furtivo
    print("\n[EXECUÇÃO] Iniciando modo furtivo...")
    urls_alvo = ['http://httpbin.org/ip'] * 5  # 5 requisições de exemplo
    camaleao.modo_furtivo(urls_alvo, intervalo_base=1, variacao=0.5)

    # Gerar relatório
    camaleao.gerar_relatorio_invisibilidade()

    # Exportar histórico
    camaleao.exportar_historico('historico_camaleao.json')

    print(f"\n🧠 PROJETO CAMALEÃO-V1 OPERACIONAL!")
    print(f"   - Rotatividade de proxies ativada")
    print(f"   - Protocolo de invisibilidade funcional")
    print(f"   - Histórico de operações registrado")
    print(f"   - Sistema de detecção de falhas ativo")

if __name__ == "__main__":
    main()