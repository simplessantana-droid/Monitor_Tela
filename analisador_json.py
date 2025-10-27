#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador de Relatórios JSON - OTIMIZADO
Sistema de análise de relatórios de monitoramento de tela
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
from detector_avancado import DetectorAvancado

class AnalisadorRelatorioJSON:
    def __init__(self):
        """Inicializa o analisador - OTIMIZADO"""
        self.detector = DetectorAvancado()
        self._cache_relatorios = {}
        self._cache_estatisticas = {}
        
        # Configurações otimizadas para gráficos
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        plt.rcParams.update({
            'figure.figsize': (12, 8),
            'font.size': 10,
            'axes.grid': True,
            'grid.alpha': 0.3
        })
    
    @lru_cache(maxsize=64)
    def _carregar_relatorio_cached(self, caminho_arquivo: str) -> Optional[Dict]:
        """Carrega relatório com cache"""
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar {caminho_arquivo}: {e}")
            return None
    
    def carregar_relatorio(self, caminho_arquivo: str) -> Optional[Dict]:
        """Carrega um relatório JSON - OTIMIZADO"""
        # Verifica cache primeiro
        if caminho_arquivo in self._cache_relatorios:
            return self._cache_relatorios[caminho_arquivo]
        
        relatorio = self._carregar_relatorio_cached(caminho_arquivo)
        if relatorio:
            self._cache_relatorios[caminho_arquivo] = relatorio
        
        return relatorio
    
    def carregar_multiplos_relatorios(self, diretorio: str = "relatorios") -> List[Dict]:
        """Carrega múltiplos relatórios de um diretório - OTIMIZADO"""
        relatorios = []
        
        if not os.path.exists(diretorio):
            print(f"Diretório {diretorio} não encontrado")
            return relatorios
        
        # Lista arquivos JSON de forma otimizada
        arquivos_json = [f for f in os.listdir(diretorio) if f.endswith('.json')]
        arquivos_json.sort()  # Ordena por nome (cronológico se formato padrão)
        
        for arquivo in arquivos_json:
            caminho_completo = os.path.join(diretorio, arquivo)
            relatorio = self.carregar_relatorio(caminho_completo)
            
            if relatorio:
                relatorio['arquivo_origem'] = arquivo
                relatorios.append(relatorio)
        
        print(f"✅ Carregados {len(relatorios)} relatórios de {diretorio}")
        return relatorios
    
    def analisar_brilho_tela(self, relatorios: List[Dict]) -> Dict[str, Any]:
        """Analisa brilho da tela ao longo do tempo - OTIMIZADO"""
        if not relatorios:
            return {'erro': 'Nenhum relatório fornecido'}
        
        # Extrai dados de brilho de forma otimizada
        dados_brilho = []
        timestamps = []
        
        for relatorio in relatorios:
            try:
                timestamp_str = relatorio.get('timestamp', '')
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    timestamps.append(timestamp)
                    
                    # Busca dados de brilho nas capturas
                    capturas = relatorio.get('capturas', [])
                    if capturas:
                        # Calcula média de atividade visual (substitui brilho)
                        atividades = [c.get('atividade_visual', 0) for c in capturas]
                        brilho_medio = np.mean(atividades) if atividades else 0
                    else:
                        brilho_medio = 0
                    
                    dados_brilho.append(brilho_medio)
            except Exception as e:
                print(f"Erro ao processar relatório: {e}")
                continue
        
        if not dados_brilho:
            return {'erro': 'Nenhum dado de brilho encontrado'}
        
        # Análise estatística otimizada
        brilho_array = np.array(dados_brilho)
        
        analise = {
            'total_amostras': len(dados_brilho),
            'brilho_medio': float(np.mean(brilho_array)),
            'brilho_mediano': float(np.median(brilho_array)),
            'desvio_padrao': float(np.std(brilho_array)),
            'brilho_minimo': float(np.min(brilho_array)),
            'brilho_maximo': float(np.max(brilho_array)),
            'variacao_total': float(np.max(brilho_array) - np.min(brilho_array)),
            'timestamps': [t.isoformat() for t in timestamps],
            'valores_brilho': dados_brilho
        }
        
        # Análise de tendências
        if len(dados_brilho) > 1:
            # Calcula tendência linear simples
            x = np.arange(len(dados_brilho))
            coef = np.polyfit(x, dados_brilho, 1)
            analise['tendencia'] = 'crescente' if coef[0] > 0 else 'decrescente' if coef[0] < 0 else 'estavel'
            analise['taxa_mudanca'] = float(coef[0])
        else:
            analise['tendencia'] = 'insuficiente'
            analise['taxa_mudanca'] = 0
        
        return analise
    
    def analisar_atividade_movimento(self, relatorios: List[Dict]) -> Dict[str, Any]:
        """Analisa atividade e movimento ao longo do tempo - OTIMIZADO"""
        if not relatorios:
            return {'erro': 'Nenhum relatório fornecido'}
        
        dados_atividade = []
        dados_movimento = []
        dados_objetos = []
        timestamps = []
        
        for relatorio in relatorios:
            try:
                timestamp_str = relatorio.get('timestamp', '')
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    timestamps.append(timestamp)
                    
                    # Extrai métricas de atividade
                    capturas = relatorio.get('capturas', [])
                    if capturas:
                        # Calcula médias das métricas
                        atividades = [c.get('atividade_visual', 0) for c in capturas]
                        movimentos = [c.get('objetos_movimento', 0) for c in capturas]
                        densidades = [c.get('densidade_atividade', 0) for c in capturas]
                        
                        dados_atividade.append(np.mean(atividades) if atividades else 0)
                        dados_movimento.append(np.mean(movimentos) if movimentos else 0)
                        dados_objetos.append(np.mean(densidades) if densidades else 0)
                    else:
                        dados_atividade.append(0)
                        dados_movimento.append(0)
                        dados_objetos.append(0)
            except Exception as e:
                print(f"Erro ao processar relatório: {e}")
                continue
        
        if not dados_atividade:
            return {'erro': 'Nenhum dado de atividade encontrado'}
        
        # Análise estatística
        atividade_array = np.array(dados_atividade)
        movimento_array = np.array(dados_movimento)
        objetos_array = np.array(dados_objetos)
        
        return {
            'total_amostras': len(dados_atividade),
            'atividade_visual': {
                'media': float(np.mean(atividade_array)),
                'mediana': float(np.median(atividade_array)),
                'desvio_padrao': float(np.std(atividade_array)),
                'minimo': float(np.min(atividade_array)),
                'maximo': float(np.max(atividade_array))
            },
            'objetos_movimento': {
                'media': float(np.mean(movimento_array)),
                'mediana': float(np.median(movimento_array)),
                'desvio_padrao': float(np.std(movimento_array)),
                'minimo': float(np.min(movimento_array)),
                'maximo': float(np.max(movimento_array))
            },
            'densidade_atividade': {
                'media': float(np.mean(objetos_array)),
                'mediana': float(np.median(objetos_array)),
                'desvio_padrao': float(np.std(objetos_array)),
                'minimo': float(np.min(objetos_array)),
                'maximo': float(np.max(objetos_array))
            },
            'timestamps': [t.isoformat() for t in timestamps],
            'dados_brutos': {
                'atividade_visual': dados_atividade,
                'objetos_movimento': dados_movimento,
                'densidade_atividade': dados_objetos
            }
        }
    
    def detectar_padroes_comportamentais(self, relatorios: List[Dict]) -> Dict[str, Any]:
        """Detecta padrões comportamentais nos relatórios - OTIMIZADO"""
        if not relatorios:
            return {'erro': 'Nenhum relatório fornecido'}
        
        padroes = {
            'picos_atividade': [],
            'periodos_inatividade': [],
            'objetos_frequentes': {},
            'horarios_pico': {},
            'tendencias_movimento': []
        }
        
        # Análise de objetos frequentes (otimizada)
        contador_objetos = {}
        dados_temporais = []
        
        for relatorio in relatorios:
            try:
                timestamp_str = relatorio.get('timestamp', '')
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    hora = timestamp.hour
                    
                    # Conta objetos detectados
                    capturas = relatorio.get('capturas', [])
                    atividade_total = 0
                    
                    for captura in capturas:
                        atividade_total += captura.get('atividade_visual', 0)
                        
                        # Simula detecção de objetos (baseado na densidade)
                        densidade = captura.get('densidade_atividade', 0)
                        if densidade > 50:
                            contador_objetos['alta_atividade'] = contador_objetos.get('alta_atividade', 0) + 1
                        elif densidade > 20:
                            contador_objetos['media_atividade'] = contador_objetos.get('media_atividade', 0) + 1
                        else:
                            contador_objetos['baixa_atividade'] = contador_objetos.get('baixa_atividade', 0) + 1
                    
                    dados_temporais.append({
                        'timestamp': timestamp,
                        'hora': hora,
                        'atividade_total': atividade_total
                    })
            except Exception as e:
                print(f"Erro ao processar relatório: {e}")
                continue
        
        # Análise de horários de pico
        atividade_por_hora = {}
        for dado in dados_temporais:
            hora = dado['hora']
            atividade_por_hora[hora] = atividade_por_hora.get(hora, [])
            atividade_por_hora[hora].append(dado['atividade_total'])
        
        # Calcula médias por hora
        for hora, atividades in atividade_por_hora.items():
            padroes['horarios_pico'][hora] = np.mean(atividades)
        
        # Identifica picos e vales
        if dados_temporais:
            atividades = [d['atividade_total'] for d in dados_temporais]
            media_atividade = np.mean(atividades)
            desvio_atividade = np.std(atividades)
            
            threshold_pico = media_atividade + desvio_atividade
            threshold_inativo = media_atividade - desvio_atividade
            
            for i, dado in enumerate(dados_temporais):
                if dado['atividade_total'] > threshold_pico:
                    padroes['picos_atividade'].append({
                        'timestamp': dado['timestamp'].isoformat(),
                        'atividade': dado['atividade_total'],
                        'intensidade': 'alta'
                    })
                elif dado['atividade_total'] < threshold_inativo:
                    padroes['periodos_inatividade'].append({
                        'timestamp': dado['timestamp'].isoformat(),
                        'atividade': dado['atividade_total'],
                        'intensidade': 'baixa'
                    })
        
        # Objetos mais frequentes
        padroes['objetos_frequentes'] = dict(sorted(contador_objetos.items(), 
                                                   key=lambda x: x[1], reverse=True)[:10])
        
        return padroes
    
    def gerar_relatorio_consolidado(self, relatorios: List[Dict]) -> Dict[str, Any]:
        """Gera relatório consolidado de análise - OTIMIZADO"""
        if not relatorios:
            return {'erro': 'Nenhum relatório fornecido'}
        
        print("📊 Gerando relatório consolidado...")
        
        # Análises principais (paralelas se possível)
        analise_brilho = self.analisar_brilho_tela(relatorios)
        analise_atividade = self.analisar_atividade_movimento(relatorios)
        padroes = self.detectar_padroes_comportamentais(relatorios)
        
        # Estatísticas gerais otimizadas
        total_capturas = sum(len(r.get('capturas', [])) for r in relatorios)
        periodo_analise = self._calcular_periodo_analise(relatorios)
        
        relatorio_consolidado = {
            'metadata': {
                'timestamp_geracao': datetime.now().isoformat(),
                'total_relatorios': len(relatorios),
                'total_capturas': total_capturas,
                'periodo_analise': periodo_analise
            },
            'analise_brilho': analise_brilho,
            'analise_atividade': analise_atividade,
            'padroes_comportamentais': padroes,
            'resumo_executivo': self._gerar_resumo_executivo(analise_brilho, analise_atividade, padroes)
        }
        
        return relatorio_consolidado
    
    def _calcular_periodo_analise(self, relatorios: List[Dict]) -> Dict[str, str]:
        """Calcula período de análise otimizado"""
        timestamps = []
        
        for relatorio in relatorios:
            timestamp_str = relatorio.get('timestamp', '')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    timestamps.append(timestamp)
                except:
                    continue
        
        if not timestamps:
            return {'inicio': 'N/A', 'fim': 'N/A', 'duracao': 'N/A'}
        
        timestamps.sort()
        inicio = timestamps[0]
        fim = timestamps[-1]
        duracao = fim - inicio
        
        return {
            'inicio': inicio.isoformat(),
            'fim': fim.isoformat(),
            'duracao': str(duracao)
        }
    
    def _gerar_resumo_executivo(self, analise_brilho: Dict, analise_atividade: Dict, 
                               padroes: Dict) -> Dict[str, Any]:
        """Gera resumo executivo otimizado"""
        resumo = {
            'nivel_atividade_geral': 'baixo',
            'tendencia_principal': 'estavel',
            'horario_maior_atividade': 'N/A',
            'observacoes': []
        }
        
        # Determina nível de atividade
        if 'atividade_visual' in analise_atividade:
            media_atividade = analise_atividade['atividade_visual'].get('media', 0)
            if media_atividade > 100:
                resumo['nivel_atividade_geral'] = 'alto'
            elif media_atividade > 50:
                resumo['nivel_atividade_geral'] = 'medio'
        
        # Tendência principal
        if 'tendencia' in analise_brilho:
            resumo['tendencia_principal'] = analise_brilho['tendencia']
        
        # Horário de maior atividade
        if 'horarios_pico' in padroes and padroes['horarios_pico']:
            hora_pico = max(padroes['horarios_pico'], key=padroes['horarios_pico'].get)
            resumo['horario_maior_atividade'] = f"{hora_pico}:00"
        
        # Observações automáticas
        if len(padroes.get('picos_atividade', [])) > 5:
            resumo['observacoes'].append("Múltiplos picos de atividade detectados")
        
        if len(padroes.get('periodos_inatividade', [])) > 10:
            resumo['observacoes'].append("Longos períodos de inatividade identificados")
        
        return resumo
    
    def gerar_graficos_analise(self, relatorios: List[Dict], salvar_em: str = "relatorios/graficos") -> List[str]:
        """Gera gráficos de análise - OTIMIZADO"""
        if not relatorios:
            print("❌ Nenhum relatório para gerar gráficos")
            return []
        
        os.makedirs(salvar_em, exist_ok=True)
        arquivos_gerados = []
        
        # Prepara dados otimizados
        dados_preparados = self._preparar_dados_graficos(relatorios)
        
        if not dados_preparados['timestamps']:
            print("❌ Nenhum dado temporal encontrado")
            return []
        
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Gráfico 1: Atividade Visual ao Longo do Tempo
            plt.figure(figsize=(12, 6))
            plt.plot(dados_preparados['timestamps'], dados_preparados['atividade_visual'], 
                    'b-', linewidth=2, label='Atividade Visual')
            plt.title('Atividade Visual ao Longo do Tempo', fontsize=14, fontweight='bold')
            plt.xlabel('Tempo')
            plt.ylabel('Nível de Atividade')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            arquivo1 = os.path.join(salvar_em, f'atividade_visual_{timestamp_str}.png')
            plt.savefig(arquivo1, dpi=150, bbox_inches='tight')
            plt.close()
            arquivos_gerados.append(arquivo1)
            
            # Gráfico 2: Objetos em Movimento
            plt.figure(figsize=(12, 6))
            plt.plot(dados_preparados['timestamps'], dados_preparados['objetos_movimento'], 
                    'r-', linewidth=2, label='Objetos em Movimento')
            plt.title('Detecção de Objetos em Movimento', fontsize=14, fontweight='bold')
            plt.xlabel('Tempo')
            plt.ylabel('Número de Objetos')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            arquivo2 = os.path.join(salvar_em, f'objetos_movimento_{timestamp_str}.png')
            plt.savefig(arquivo2, dpi=150, bbox_inches='tight')
            plt.close()
            arquivos_gerados.append(arquivo2)
            
            # Gráfico 3: Densidade de Atividade
            plt.figure(figsize=(12, 6))
            plt.plot(dados_preparados['timestamps'], dados_preparados['densidade_atividade'], 
                    'g-', linewidth=2, label='Densidade de Atividade')
            plt.title('Densidade de Atividade na Tela', fontsize=14, fontweight='bold')
            plt.xlabel('Tempo')
            plt.ylabel('Densidade')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            arquivo3 = os.path.join(salvar_em, f'densidade_atividade_{timestamp_str}.png')
            plt.savefig(arquivo3, dpi=150, bbox_inches='tight')
            plt.close()
            arquivos_gerados.append(arquivo3)
            
            print(f"✅ {len(arquivos_gerados)} gráficos gerados em {salvar_em}")
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráficos: {e}")
        
        return arquivos_gerados
    
    def _preparar_dados_graficos(self, relatorios: List[Dict]) -> Dict[str, List]:
        """Prepara dados para gráficos de forma otimizada"""
        dados = {
            'timestamps': [],
            'atividade_visual': [],
            'objetos_movimento': [],
            'densidade_atividade': []
        }
        
        for relatorio in relatorios:
            try:
                timestamp_str = relatorio.get('timestamp', '')
                if not timestamp_str:
                    continue
                
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                capturas = relatorio.get('capturas', [])
                
                if capturas:
                    # Calcula médias das métricas
                    atividade_media = np.mean([c.get('atividade_visual', 0) for c in capturas])
                    movimento_medio = np.mean([c.get('objetos_movimento', 0) for c in capturas])
                    densidade_media = np.mean([c.get('densidade_atividade', 0) for c in capturas])
                    
                    dados['timestamps'].append(timestamp)
                    dados['atividade_visual'].append(atividade_media)
                    dados['objetos_movimento'].append(movimento_medio)
                    dados['densidade_atividade'].append(densidade_media)
            except Exception as e:
                print(f"Erro ao processar dados: {e}")
                continue
        
        return dados
    
    def salvar_relatorio_consolidado(self, relatorio: Dict, nome_arquivo: str = None) -> str:
        """Salva relatório consolidado - OTIMIZADO"""
        if nome_arquivo is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"relatorio_consolidado_{timestamp}.json"
        
        os.makedirs("relatorios", exist_ok=True)
        caminho_completo = os.path.join("relatorios", nome_arquivo)
        
        try:
            with open(caminho_completo, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Relatório consolidado salvo em: {caminho_completo}")
            return caminho_completo
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")
            return ""

def main():
    """Função principal para teste do analisador - OTIMIZADA"""
    print("📊 ANALISADOR DE RELATÓRIOS JSON - OTIMIZADO")
    print("=" * 50)
    
    analisador = AnalisadorRelatorioJSON()
    
    # Carrega relatórios
    print("📂 Carregando relatórios...")
    relatorios = analisador.carregar_multiplos_relatorios("relatorios")
    
    if not relatorios:
        print("❌ Nenhum relatório encontrado")
        return
    
    # Gera análise consolidada
    print("🔍 Gerando análise consolidada...")
    relatorio_consolidado = analisador.gerar_relatorio_consolidado(relatorios)
    
    # Salva relatório consolidado
    arquivo_salvo = analisador.salvar_relatorio_consolidado(relatorio_consolidado)
    
    # Gera gráficos
    print("📈 Gerando gráficos de análise...")
    graficos = analisador.gerar_graficos_analise(relatorios)
    
    # Exibe resumo
    if 'resumo_executivo' in relatorio_consolidado:
        resumo = relatorio_consolidado['resumo_executivo']
        print(f"\n📋 RESUMO EXECUTIVO:")
        print(f"Nível de atividade: {resumo.get('nivel_atividade_geral', 'N/A')}")
        print(f"Tendência principal: {resumo.get('tendencia_principal', 'N/A')}")
        print(f"Horário de maior atividade: {resumo.get('horario_maior_atividade', 'N/A')}")
        
        if resumo.get('observacoes'):
            print("Observações:")
            for obs in resumo['observacoes']:
                print(f"  • {obs}")
    
    print(f"\n✅ Análise concluída!")
    print(f"📄 Relatório: {arquivo_salvo}")
    print(f"📊 Gráficos: {len(graficos)} arquivos gerados")

if __name__ == "__main__":
    main()