#!/usr/bin/env python3
"""
PROJETO CLOUD SEARCH: SISTEMA DE BUSCA PRIVADA COM ZINCSEARCH
Sistema avançado de busca e indexação de dados privados
"""

import json
import requests
import os
from datetime import datetime
from pathlib import Path
import hashlib
import threading
import time
from urllib.parse import urljoin

class CloudSearchSystem:
    """
    Sistema de busca privada baseado em ZincSearch
    Para quando você precisa de busca poderosa sem depender de serviços externos
    """

    def __init__(self, zinc_url="http://localhost:4080", username="admin", password="Complexpass#123"):
        self.nome = "CLOUD SEARCH"
        self.descricao = "Sistema de Busca Privada com ZincSearch"
        self.status = "ativo"
        self.zinc_url = zinc_url
        self.username = username
        self.password = password
        self.auth = (username, password)

        # Headers para requisições
        self.headers = {
            'Content-Type': 'application/json'
        }

        # Inicializar sistema
        self.inicializar_sistema()

    def inicializar_sistema(self):
        """Inicializa o sistema de busca"""
        print(f"[CLOUD SEARCH] Inicializando sistema de busca privada...")

        # Testar conexão com ZincSearch
        try:
            response = requests.get(
                urljoin(self.zinc_url, "/api/version"),
                auth=self.auth,
                headers=self.headers
            )

            if response.status_code == 200:
                print(f"  [✓] Conexão com ZincSearch estabelecida")
                print(f"  [✓] Versão: {response.json().get('version', 'desconhecida')}")
            else:
                print(f"  [!] Aviso: Não foi possível conectar ao ZincSearch")
                print(f"      Verifique se o ZincSearch está rodando em {self.zinc_url}")

        except requests.exceptions.ConnectionError:
            print(f"  [!] Aviso: ZincSearch não encontrado em {self.zinc_url}")
            print(f"      Esta implementação está preparada para conexão com ZincSearch")
            print(f"      Execute 'docker run -p 4080:4080 -e ROOT_USER=admin -e ROOT_PASSWORD=Complexpass#123 public.ecr.aws/zinclabs/zinc:0.4.11' para iniciar")

        print(f"[CLOUD SEARCH] Sistema de busca inicializado")

    def criar_indice(self, nome_indice, config_mapeamento=None):
        """Cria um novo índice no ZincSearch"""
        print(f"[CLOUD SEARCH] Criando índice: {nome_indice}")

        url = urljoin(self.zinc_url, f"/api/index/{nome_indice}")

        payload = {
            "name": nome_indice,
            "storage_type": "disk",
            "shard_num": 1
        }

        if config_mapeamento:
            payload["mapping"] = config_mapeamento

        try:
            response = requests.post(
                url,
                auth=self.auth,
                headers=self.headers,
                json=payload
            )

            if response.status_code in [200, 201]:
                print(f"  [✓] Índice '{nome_indice}' criado com sucesso")
                return True
            else:
                print(f"  [!] Erro ao criar índice: {response.text}")
                return False

        except Exception as e:
            print(f"  [!] Erro ao criar índice: {e}")
            return False

    def indexar_documento(self, nome_indice, doc_id, documento):
        """Indexa um documento no índice especificado"""
        print(f"[CLOUD SEARCH] Indexando documento: {doc_id} no índice {nome_indice}")

        url = urljoin(self.zinc_url, f"/api/{nome_indice}/_doc/{doc_id}")

        try:
            response = requests.put(
                url,
                auth=self.auth,
                headers=self.headers,
                json=documento
            )

            if response.status_code in [200, 201]:
                print(f"  [✓] Documento '{doc_id}' indexado com sucesso")
                return True
            else:
                print(f"  [!] Erro ao indexar documento: {response.text}")
                return False

        except Exception as e:
            print(f"  [!] Erro ao indexar documento: {e}")
            return False

    def indexar_arquivo(self, nome_indice, caminho_arquivo):
        """Indexa o conteúdo de um arquivo"""
        print(f"[CLOUD SEARCH] Indexando arquivo: {caminho_arquivo}")

        if not os.path.exists(caminho_arquivo):
            print(f"  [!] Arquivo não encontrado: {caminho_arquivo}")
            return False

        # Extrair informações do arquivo
        tamanho = os.path.getsize(caminho_arquivo)
        extensao = Path(caminho_arquivo).suffix.lower()

        # Ler conteúdo do arquivo (para textos)
        conteudo = ""
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                conteudo = f.read()[:10000]  # Limitar para 10k caracteres
        except:
            # Se não for texto, usar hash
            with open(caminho_arquivo, 'rb') as f:
                conteudo = hashlib.md5(f.read()).hexdigest()

        # Criar ID baseado no caminho
        doc_id = hashlib.sha256(caminho_arquivo.encode()).hexdigest()

        documento = {
            "nome_arquivo": Path(caminho_arquivo).name,
            "caminho_completo": caminho_arquivo,
            "conteudo": conteudo,
            "extensao": extensao,
            "tamanho_bytes": tamanho,
            "data_indexacao": datetime.now().isoformat(),
            "hash_arquivo": hashlib.sha256(open(caminho_arquivo, 'rb').read()).hexdigest()
        }

        return self.indexar_documento(nome_indice, doc_id, documento)

    def indexar_diretorio(self, nome_indice, diretorio, tipos_arquivo=None):
        """Indexa todos os arquivos de um diretório"""
        print(f"[CLOUD SEARCH] Indexando diretório: {diretorio}")

        if tipos_arquivo is None:
            tipos_arquivo = ['.txt', '.pdf', '.doc', '.docx', '.py', '.js', '.html', '.json', '.xml']

        arquivos_processados = 0
        for root, dirs, files in os.walk(diretorio):
            for file in files:
                caminho_completo = os.path.join(root, file)
                extensao = Path(file).suffix.lower()

                if extensao in tipos_arquivo:
                    if self.indexar_arquivo(nome_indice, caminho_completo):
                        arquivos_processados += 1

        print(f"  [✓] {arquivos_processados} arquivos indexados no índice '{nome_indice}'")
        return arquivos_processados

    def buscar(self, nome_indice, consulta, tamanho=10, campo_busca="conteudo"):
        """Realiza busca no índice especificado"""
        print(f"[CLOUD SEARCH] Buscando: '{consulta}' no índice {nome_indice}")

        url = urljoin(self.zinc_url, f"/api/{nome_indice}/_search")

        query_body = {
            "query": {
                "match": {
                    campo_busca: consulta
                }
            },
            "size": tamanho
        }

        try:
            response = requests.post(
                url,
                auth=self.auth,
                headers=self.headers,
                json=query_body
            )

            if response.status_code == 200:
                resultados = response.json()
                hits = resultados.get('hits', {}).get('hits', [])

                print(f"  [✓] {len(hits)} resultados encontrados")
                return hits
            else:
                print(f"  [!] Erro na busca: {response.text}")
                return []

        except Exception as e:
            print(f"  [!] Erro na busca: {e}")
            return []

    def buscar_avancada(self, nome_indice, consulta, filtros=None, tamanho=10):
        """Realiza busca avançada com filtros"""
        print(f"[CLOUD SEARCH] Busca avançada: '{consulta}'")

        url = urljoin(self.zinc_url, f"/api/{nome_indice}/_search")

        query_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "conteudo": consulta
                            }
                        },
                        {
                            "match": {
                                "nome_arquivo": consulta
                            }
                        }
                    ]
                }
            },
            "size": tamanho
        }

        if filtros:
            if "extensao" in filtros:
                query_body["query"]["bool"]["filter"] = [{
                    "term": {
                        "extensao": filtros["extensao"]
                    }
                }]

        try:
            response = requests.post(
                url,
                auth=self.auth,
                headers=self.headers,
                json=query_body
            )

            if response.status_code == 200:
                resultados = response.json()
                hits = resultados.get('hits', {}).get('hits', [])

                print(f"  [✓] {len(hits)} resultados encontrados com filtros")
                return hits
            else:
                print(f"  [!] Erro na busca avançada: {response.text}")
                return []

        except Exception as e:
            print(f"  [!] Erro na busca avançada: {e}")
            return []

    def obter_documento(self, nome_indice, doc_id):
        """Obtém um documento específico pelo ID"""
        url = urljoin(self.zinc_url, f"/api/{nome_indice}/_doc/{doc_id}")

        try:
            response = requests.get(
                url,
                auth=self.auth,
                headers=self.headers
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"  [!] Documento não encontrado: {doc_id}")
                return None

        except Exception as e:
            print(f"  [!] Erro ao obter documento: {e}")
            return None

    def listar_indices(self):
        """Lista todos os índices existentes"""
        url = urljoin(self.zinc_url, "/api/index")

        try:
            response = requests.get(
                url,
                auth=self.auth,
                headers=self.headers
            )

            if response.status_code == 200:
                indices = response.json()
                print(f"  [✓] {len(indices)} índices encontrados")
                return indices
            else:
                print(f"  [!] Erro ao listar índices: {response.text}")
                return []

        except Exception as e:
            print(f"  [!] Erro ao listar índices: {e}")
            return []

    def apagar_indice(self, nome_indice):
        """Apaga um índice existente"""
        url = urljoin(self.zinc_url, f"/api/index/{nome_indice}")

        try:
            response = requests.delete(
                url,
                auth=self.auth,
                headers=self.headers
            )

            if response.status_code == 200:
                print(f"  [✓] Índice '{nome_indice}' apagado com sucesso")
                return True
            else:
                print(f"  [!] Erro ao apagar índice: {response.text}")
                return False

        except Exception as e:
            print(f"  [!] Erro ao apagar índice: {e}")
            return False

    def gerar_relatorio_busca(self, nome_indice):
        """Gera relatório sobre o índice de busca"""
        url = urljoin(self.zinc_url, f"/api/index/{nome_indice}")

        try:
            response = requests.get(
                url,
                auth=self.auth,
                headers=self.headers
            )

            if response.status_code == 200:
                info_indice = response.json()

                print(f"\n[RELATÓRIO BUSCA] Índice: {nome_indice}")
                print("-" * 40)
                print(f"Documentos: {info_indice.get('docs_count', 0)}")
                print(f"Tamanho: {info_indice.get('storage_size', 'N/A')}")
                print(f"Criado em: {info_indice.get('created_at', 'N/A')}")

                return info_indice
            else:
                print(f"  [!] Erro ao obter informações do índice: {response.text}")
                return None

        except Exception as e:
            print(f"  [!] Erro ao gerar relatório: {e}")
            return None

    def sistema_busca_integrado(self, diretorio_fonte, nome_indice_principal="imperio_busca"):
        """Sistema integrado de busca para o Império Mutante"""
        print(f"\n🔍 INICIANDO SISTEMA INTEGRADO DE BUSCA")
        print("="*50)

        # 1. Criar índice principal
        print(f"\n[1/5] Criando índice principal: {nome_indice_principal}")
        self.criar_indice(nome_indice_principal)

        # 2. Indexar diretório de fonte
        print(f"\n[2/5] Indexando diretório: {diretorio_fonte}")
        arquivos_indexados = self.indexar_diretorio(nome_indice_principal, diretorio_fonte)

        # 3. Realizar buscas de exemplo
        print(f"\n[3/5] Realizando buscas de exemplo...")

        buscas_exemplo = [
            "python",
            "imperio",
            "automacao",
            "dados"
        ]

        for busca in buscas_exemplo:
            resultados = self.buscar(nome_indice_principal, busca, tamanho=5)
            print(f"  - Busca '{busca}': {len(resultados)} resultados")

        # 4. Busca avançada
        print(f"\n[4/5] Realizando busca avançada...")
        resultados_avancados = self.buscar_avancada(
            nome_indice_principal,
            "automacao",
            filtros={"extensao": ".py"},
            tamanho=10
        )

        # 5. Gerar relatório
        print(f"\n[5/5] Gerando relatório do índice...")
        self.gerar_relatorio_busca(nome_indice_principal)

        print(f"\n{'='*50}")
        print(f"🔍 SISTEMA DE BUSCA CONCLUÍDO!")
        print(f"   - Índice criado: {nome_indice_principal}")
        print(f"   - Arquivos indexados: {arquivos_indexados}")
        print(f"   - Buscas realizadas: {len(buscas_exemplo)}")
        print(f"   - Resultados avançados: {len(resultados_avancados)}")
        print(f"{'='*50}")

        return {
            "indice": nome_indice_principal,
            "arquivos_indexados": arquivos_indexados,
            "buscas_realizadas": len(buscas_exemplo),
            "resultados_avancados": len(resultados_avancados)
        }

def main():
    """Função principal do sistema de busca"""
    print("🔍 CONECTANDO AO PROJETO CLOUD SEARCH")
    print("⚡ Iniciando sistema de busca privada...")

    # Criar diretório de exemplo
    os.makedirs('exemplo_busca', exist_ok=True)

    # Criar arquivos de exemplo
    with open('exemplo_busca/automacao_python.txt', 'w') as f:
        f.write('Sistema de automação com Python e IA\nEste é um exemplo de conteúdo para busca\nAutomação de processos e tarefas repetitivas')

    with open('exemplo_busca/imperio_mutante.txt', 'w') as f:
        f.write('Império Mutante - Sistema de dominação digital\nEstratégias avançadas de automação\nNéctar de conhecimento digital')

    with open('exemplo_busca/script_busca.py', 'w') as f:
        f.write('# Script de exemplo para busca\nimport os\n# Sistema de busca avançada\nprint("Busca em execução")')

    # Iniciar sistema de busca
    cloud_search = CloudSearchSystem()

    # Executar sistema integrado
    resultado = cloud_search.sistema_busca_integrado('exemplo_busca', 'busca_imperio_mutante')

    print(f"\n🧠 PROJETO CLOUD SEARCH OPERACIONAL!")
    print(f"   - Sistema de busca privada ativado")
    print(f"   - Indexação automática implementada")
    print(f"   - Busca avançada com filtros funcional")
    print(f"   - Integração com ZincSearch preparada")
    print(f"   - Sistema de relatórios operacional")

if __name__ == "__main__":
    main()