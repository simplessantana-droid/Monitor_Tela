#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de Tela - FORMATO TESTE_DETECTOR_AVANCADO
Sistema de monitoramento de tela com detecção de pessoas e objetos
"""

import cv2
import numpy as np
import os
import time
from datetime import datetime
import json
import matplotlib.pyplot as plt
from PIL import ImageGrab, Image
import pyautogui
import ctypes

# Suporte Win32 para captura de janela oculta/minimizada
try:
    import win32gui
    import win32ui
    import win32con
    HAS_WIN32 = True
except Exception:
    HAS_WIN32 = False
import pyautogui
from functools import lru_cache
from detector_avancado import DetectorAvancado

class MonitorTela:
    def __init__(self, duracao=60, intervalo=0.1):
        """Inicializa o monitor de tela - FORMATO TESTE_DETECTOR_AVANCADO"""
        self.duracao = duracao
        self.intervalo = intervalo
        self.detector = DetectorAvancado()
        self.criar_diretorios()
        
        # Configurações otimizadas para alta frequência
        self._cache_resolucao = None
        self._contador_frames = 0
        
        # Configurações para gráficos
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        plt.rcParams.update({
            'figure.figsize': (15, 10),
            'font.size': 10,
            'axes.grid': True,
            'grid.alpha': 0.3
        })

    def criar_diretorios(self):
        """Cria os diretórios necessários para o funcionamento"""
        os.makedirs("capturas", exist_ok=True)
        os.makedirs("relatorios", exist_ok=True)
        os.makedirs(os.path.join("relatorios", "graficos"), exist_ok=True)
        self.pasta_capturas = "capturas"
    
    def criar_pasta_capturas(self):
        """Cria a pasta para armazenar as capturas se não existir"""
        os.makedirs(self.pasta_capturas, exist_ok=True)
    
    @lru_cache(maxsize=1)
    def capturar_tela(self):
        """Captura apenas a janela 'DroidCam Client' se encontrada, incluindo casos cobertos/minimizados (via PrintWindow), senão captura a tela inteira."""
        try:
            # Preferência: tentar PrintWindow (funciona coberta/minimizada em muitos casos)
            def _capture_droidcam_printwindow(title='DroidCam Client'):
                if not HAS_WIN32:
                    return None
                try:
                    hwnd = win32gui.FindWindow(None, title)
                    if hwnd == 0:
                        matches = []
                        def _enum_cb(h, _):
                            try:
                                t = win32gui.GetWindowText(h) or ''
                                if title.lower() in t.lower():
                                    matches.append(h)
                            except Exception:
                                pass
                        win32gui.EnumWindows(_enum_cb, None)
                        if matches:
                            hwnd = matches[0]
                    if hwnd == 0:
                        return None
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    width = right - left
                    height = bottom - top
                    hwndDC = win32gui.GetWindowDC(hwnd)
                    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                    saveDC = mfcDC.CreateCompatibleDC()
                    saveBitMap = win32ui.CreateBitmap()
                    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
                    saveDC.SelectObject(saveBitMap)
                    PW_RENDERFULLCONTENT = 0x00000002
                    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), PW_RENDERFULLCONTENT)
                    bmpinfo = saveBitMap.GetInfo()
                    bmpstr = saveBitMap.GetBitmapBits(True)
                    im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
                    win32gui.DeleteObject(saveBitMap.GetHandle())
                    saveDC.DeleteDC()
                    mfcDC.DeleteDC()
                    win32gui.ReleaseDC(hwnd, hwndDC)
                    if result != 1:
                        return None
                    return im
                except Exception as e:
                    print(f"⚠️ Falha PrintWindow: {e}")
                    return None

            im = _capture_droidcam_printwindow()
            if im is not None:
                screenshot = im
                self._cache_resolucao = screenshot.size
            else:
                # Fallback: tentar achar bbox e capturar via ImageGrab
                try:
                    wins = pyautogui.getWindowsWithTitle('DroidCam Client')
                    if wins:
                        w = wins[0]
                        bbox = (w.left, w.top, w.left + w.width, w.top + w.height)
                        screenshot = ImageGrab.grab(bbox=bbox)
                        self._cache_resolucao = screenshot.size
                    else:
                        screenshot = ImageGrab.grab()
                        if self._cache_resolucao is None:
                            self._cache_resolucao = screenshot.size
                except Exception:
                    screenshot = ImageGrab.grab()
                    if self._cache_resolucao is None:
                        self._cache_resolucao = screenshot.size
            
            # Converte para numpy array de forma mais eficiente
            imagem_array = np.array(screenshot)
            imagem_bgr = cv2.cvtColor(imagem_array, cv2.COLOR_RGB2BGR)
            
            return imagem_bgr
        except Exception as e:
            print(f"❌ Erro ao capturar tela: {e}")
            return None
    
    def salvar_captura(self, imagem, timestamp):
        """Salva a captura de forma otimizada para alta frequência"""
        try:
            # Usa contador de frames para evitar conflitos de nome
            self._contador_frames += 1
            nome_arquivo = f"captura_{timestamp.strftime('%Y%m%d_%H%M%S')}_{self._contador_frames:04d}.jpg"
            caminho_completo = os.path.join(self.pasta_capturas, nome_arquivo)
            
            # Salva com compressão otimizada para velocidade
            cv2.imwrite(caminho_completo, imagem, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            # Calcula o tamanho do arquivo
            tamanho_arquivo = os.path.getsize(caminho_completo)
            
            return caminho_completo, tamanho_arquivo
        except Exception as e:
            print(f"❌ Erro ao salvar captura: {e}")
            return None, None
    
    def processar_imagem(self, imagem_path: str) -> dict:
        """Processa imagem usando detector avançado - FORMATO TESTE_DETECTOR_AVANCADO"""
        try:
            # Usa o detector avançado para análise completa
            resultado = self.detector.detectar_objetos_pessoas(imagem_path)
            
            # Retorna no formato teste_detector_avancado
            return {
                'timestamp': datetime.now().isoformat(),
                'arquivo': imagem_path,
                'tamanho_arquivo': os.path.getsize(imagem_path),
                'resolucao': f"{self._cache_resolucao[0]}x{self._cache_resolucao[1]}" if self._cache_resolucao else "1920x1080",
                'deteccoes': resultado.get('deteccoes', {'pessoas': [], 'objetos': []}),
                'analises': resultado.get('analises', {'movimentos': [], 'interacoes': [], 'atividades_faciais': []}),
                'resumo_captura': {
                    'total_pessoas': resultado.get('resumo', {}).get('total_pessoas', 0),
                    'total_objetos': resultado.get('resumo', {}).get('total_objetos', 0),
                    'total_interacoes': resultado.get('resumo', {}).get('total_interacoes', 0),
                    'movimento_geral': resultado.get('resumo', {}).get('movimento_geral', 0)
                }
            }
        except Exception as e:
            print(f"Erro ao processar imagem {imagem_path}: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'arquivo': imagem_path,
                'tamanho_arquivo': 0,
                'resolucao': "0x0",
                'deteccoes': {'pessoas': [], 'objetos': []},
                'analises': {'movimentos': [], 'interacoes': [], 'atividades_faciais': []},
                'resumo_captura': {
                    'total_pessoas': 0,
                    'total_objetos': 0,
                    'total_interacoes': 0,
                    'movimento_geral': 0
                }
            }

    def calcular_estatisticas_finais(self, capturas: list) -> dict:
        """Calcula estatísticas finais - FORMATO TESTE_DETECTOR_AVANCADO"""
        if not capturas:
            return {
                'total_pessoas': 0,
                'total_objetos': 0,
                'total_interacoes': 0,
                'movimento_geral': 0,
                'pessoas_unicas': 0,
                'objetos_unicos': 0,
                'atividade_maxima': 0,
                'periodo_maior_atividade': 'N/A'
            }
        
        # Soma totais
        total_pessoas = sum(c.get('resumo_captura', {}).get('total_pessoas', 0) for c in capturas)
        total_objetos = sum(c.get('resumo_captura', {}).get('total_objetos', 0) for c in capturas)
        total_interacoes = sum(c.get('resumo_captura', {}).get('total_interacoes', 0) for c in capturas)
        movimento_geral = sum(c.get('resumo_captura', {}).get('movimento_geral', 0) for c in capturas)
        
        # Calcula médias e máximos
        media_pessoas = total_pessoas / len(capturas) if capturas else 0
        media_objetos = total_objetos / len(capturas) if capturas else 0
        
        # Encontra período de maior atividade
        max_atividade = 0
        periodo_max = 'N/A'
        
        for captura in capturas:
            atividade_atual = (
                captura.get('resumo_captura', {}).get('total_pessoas', 0) +
                captura.get('resumo_captura', {}).get('total_objetos', 0) +
                captura.get('resumo_captura', {}).get('movimento_geral', 0)
            )
            
            if atividade_atual > max_atividade:
                max_atividade = atividade_atual
                timestamp = captura.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        periodo_max = dt.strftime('%H:%M:%S')
                    except:
                        periodo_max = 'N/A'
        
        return {
            'total_pessoas': total_pessoas,
            'total_objetos': total_objetos,
            'total_interacoes': total_interacoes,
            'movimento_geral': movimento_geral,
            'media_pessoas_por_captura': round(media_pessoas, 2),
            'media_objetos_por_captura': round(media_objetos, 2),
            'atividade_maxima': max_atividade,
            'periodo_maior_atividade': periodo_max
        }

    def gerar_narrativa_consolidada(self, capturas: list, estatisticas: dict) -> str:
        """Gera narrativa consolidada da sessão com ações específicas - FORMATO TESTE_DETECTOR_AVANCADO"""
        if not capturas:
            return "Nenhuma captura foi realizada durante a sessão."
        
        total_pessoas = estatisticas.get('total_pessoas', 0)
        total_objetos = estatisticas.get('total_objetos', 0)
        total_interacoes = estatisticas.get('total_interacoes', 0)
        periodo_max = estatisticas.get('periodo_maior_atividade', 'N/A')
        
        narrativa_partes = []
        
        # Análise detalhada de atividades das pessoas
        if total_pessoas > 0:
            atividades_detectadas = self._analisar_atividades_sessao(capturas)
            
            media_pessoas = estatisticas.get('media_pessoas_por_captura', 0)
            if media_pessoas > 1:
                narrativa_partes.append(f"Durante a sessão foram detectadas {total_pessoas} pessoas no total, com uma média de {media_pessoas:.1f} pessoas por captura.")
            else:
                narrativa_partes.append(f"Foi detectada presença humana em {total_pessoas} capturas durante a sessão.")
            
            # Adiciona descrição das atividades específicas
            if atividades_detectadas:
                narrativa_partes.append(f"Atividades observadas: {atividades_detectadas}")
        else:
            narrativa_partes.append("Nenhuma pessoa foi detectada durante toda a sessão de monitoramento.")
        
        # Análise de objetos
        if total_objetos > 0:
            media_objetos = estatisticas.get('media_objetos_por_captura', 0)
            narrativa_partes.append(f"Foram identificados {total_objetos} objetos diversos, com média de {media_objetos:.1f} objetos por captura.")
        else:
            narrativa_partes.append("Nenhum objeto específico foi detectado nas capturas.")
        
        # Análise de interações
        if total_interacoes > 0:
            narrativa_partes.append(f"Foram observadas {total_interacoes} interações entre pessoas e objetos.")
        
        # Período de maior atividade
        if periodo_max != 'N/A':
            narrativa_partes.append(f"O período de maior atividade foi registrado às {periodo_max}.")
        
        # Análise geral
        if total_pessoas == 0 and total_objetos == 0:
            narrativa_partes.append("A sessão apresentou baixa atividade visual, sem detecções significativas.")
        elif total_pessoas > 0 and total_objetos > 0:
            narrativa_partes.append("A sessão apresentou atividade moderada com presença humana e objetos diversos.")
        
        return " ".join(narrativa_partes)
    
    def _analisar_atividades_sessao(self, capturas: list) -> str:
        """Analisa as atividades específicas detectadas durante a sessão"""
        try:
            atividades_contadas = {}
            posturas_contadas = {}
            movimentos_maos_contados = {}
            
            for captura in capturas:
                analises = captura.get('analises', {})
                atividades_faciais = analises.get('atividades_faciais', [])
                
                for atividade in atividades_faciais:
                    # Conta atividades prováveis
                    atividade_provavel = atividade.get('atividade_provavel', 'desconhecida')
                    if atividade_provavel != 'desconhecida':
                        atividades_contadas[atividade_provavel] = atividades_contadas.get(atividade_provavel, 0) + 1
                    
                    # Conta posturas
                    postura = atividade.get('postura_corporal', 'desconhecida')
                    if postura != 'desconhecida':
                        posturas_contadas[postura] = posturas_contadas.get(postura, 0) + 1
                    
                    # Conta movimentos das mãos
                    movimento_maos = atividade.get('movimento_maos', 'nao_detectado')
                    if movimento_maos != 'nao_detectado':
                        movimentos_maos_contados[movimento_maos] = movimentos_maos_contados.get(movimento_maos, 0) + 1
            
            # Monta descrição das atividades
            descricoes = []
            
            # Atividade mais frequente
            if atividades_contadas:
                atividade_principal = max(atividades_contadas, key=atividades_contadas.get)
                count_principal = atividades_contadas[atividade_principal]
                
                # Traduz atividades para descrições mais naturais
                traducoes_atividades = {
                    'trabalhando_no_computador': 'trabalho no computador',
                    'conversando_ou_apresentando': 'conversas ou apresentações',
                    'lendo_ou_escrevendo': 'leitura ou escrita',
                    'observando_ou_aguardando': 'observação ou espera',
                    'manipulando_objeto_no_chao': 'manipulação de objetos'
                }
                
                atividade_desc = traducoes_atividades.get(atividade_principal, atividade_principal.replace('_', ' '))
                descricoes.append(f"predominantemente {atividade_desc} ({count_principal} detecções)")
            
            # Postura mais comum
            if posturas_contadas:
                postura_principal = max(posturas_contadas, key=posturas_contadas.get)
                if postura_principal == 'agachado_ou_sentado':
                    descricoes.append("principalmente sentado")
                elif postura_principal == 'em_pe':
                    descricoes.append("principalmente em pé")
            
            # Movimento das mãos mais comum
            if movimentos_maos_contados:
                movimento_principal = max(movimentos_maos_contados, key=movimentos_maos_contados.get)
                traducoes_movimentos = {
                    'digitando': 'digitação frequente',
                    'gesticulando': 'gesticulação ativa',
                    'maos_no_colo': 'mãos em repouso',
                    'apontando': 'apontamentos frequentes',
                    'segurando_objeto': 'manipulação de objetos',
                    'maos_ao_lado': 'postura relaxada'
                }
                
                movimento_desc = traducoes_movimentos.get(movimento_principal, movimento_principal.replace('_', ' '))
                descricoes.append(movimento_desc)
            
            return ', '.join(descricoes) if descricoes else 'atividades variadas'
            
        except Exception as e:
            print(f"❌ Erro ao analisar atividades da sessão: {e}")
            return 'atividades não identificadas'

    def gerar_graficos(self, capturas: list, nome_arquivo: str):
        """Gera gráficos de análise - FORMATO TESTE_DETECTOR_AVANCADO"""
        if not capturas:
            print("❌ Nenhuma captura para gerar gráficos")
            return
        
        # Prepara dados
        timestamps = []
        pessoas_dados = []
        objetos_dados = []
        movimento_dados = []
        interacoes_dados = []
        
        for captura in capturas:
            try:
                timestamp_str = captura.get('timestamp', '')
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    timestamps.append(timestamp)
                    
                    resumo = captura.get('resumo_captura', {})
                    pessoas_dados.append(resumo.get('total_pessoas', 0))
                    objetos_dados.append(resumo.get('total_objetos', 0))
                    movimento_dados.append(resumo.get('movimento_geral', 0))
                    interacoes_dados.append(resumo.get('total_interacoes', 0))
            except Exception as e:
                print(f"Erro ao processar timestamp: {e}")
                continue
        
        if not timestamps:
            print("❌ Nenhum dado temporal válido")
            return
        
        # Cria figura com subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Análise de Detecção - Pessoas e Objetos', fontsize=16, fontweight='bold')
        
        # Gráfico 1: Pessoas Detectadas
        ax1.plot(timestamps, pessoas_dados, 'b-', linewidth=2, marker='o', markersize=4)
        ax1.set_title('Pessoas Detectadas ao Longo do Tempo')
        ax1.set_ylabel('Número de Pessoas')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Objetos Detectados
        ax2.plot(timestamps, objetos_dados, 'r-', linewidth=2, marker='s', markersize=4)
        ax2.set_title('Objetos Detectados ao Longo do Tempo')
        ax2.set_ylabel('Número de Objetos')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Movimento Geral
        ax3.plot(timestamps, movimento_dados, 'g-', linewidth=2, marker='^', markersize=4)
        ax3.set_title('Movimento Geral Detectado')
        ax3.set_ylabel('Nível de Movimento')
        ax3.set_xlabel('Tempo')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Interações
        ax4.plot(timestamps, interacoes_dados, 'm-', linewidth=2, marker='d', markersize=4)
        ax4.set_title('Interações Detectadas')
        ax4.set_ylabel('Número de Interações')
        ax4.set_xlabel('Tempo')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Salva gráfico
        caminho_grafico = os.path.join("relatorios", "graficos", nome_arquivo)
        plt.savefig(caminho_grafico, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Gráficos salvos em: {caminho_grafico}")

    def monitorar(self, duracao_segundos: int = 60, intervalo_segundos: float = 0.1):
        """Monitora a tela - FORMATO TESTE_DETECTOR_AVANCADO com alta frequência"""
        print(f"🖥️ INICIANDO MONITORAMENTO - FORMATO TESTE_DETECTOR_AVANCADO")
        print(f"⏱️ Duração: {duracao_segundos}s | Intervalo: {intervalo_segundos}s")
        print(f"🚀 Frequência máxima: {1/intervalo_segundos:.1f} capturas/segundo")
        print("=" * 60)
        
        inicio = time.time()
        capturas = []
        contador = 0
        ultimo_print = 0
        
        try:
            while time.time() - inicio < duracao_segundos:
                contador += 1
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Inclui milissegundos
                
                # Captura tela
                imagem = self.capturar_tela()
                imagem_path, _ = self.salvar_captura(imagem, datetime.now())
                if not imagem_path:
                    time.sleep(intervalo_segundos)
                    continue
                
                # Processa com detector avançado
                resultado_processamento = self.processar_imagem(imagem_path)
                capturas.append(resultado_processamento)
                
                # Mostra progresso a cada segundo para não sobrecarregar o terminal
                tempo_atual = time.time()
                if tempo_atual - ultimo_print >= 1.0:
                    pessoas = resultado_processamento.get('resumo_captura', {}).get('total_pessoas', 0)
                    objetos = resultado_processamento.get('resumo_captura', {}).get('total_objetos', 0)
                    fps_atual = contador / (tempo_atual - inicio)
                    
                    print(f"📸 Captura {contador}: {pessoas} pessoas, {objetos} objetos | FPS: {fps_atual:.1f}")
                    ultimo_print = tempo_atual
                
                time.sleep(intervalo_segundos)
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoramento interrompido pelo usuário")
        
        fim = time.time()
        duracao_real = fim - inicio
        
        # Calcula estatísticas finais
        estatisticas = self.calcular_estatisticas_finais(capturas)
        
        # Gera narrativa consolidada
        narrativa = self.gerar_narrativa_consolidada(capturas, estatisticas)
        
        # Cria relatório final no formato teste_detector_avancado
        relatorio_final = {
            'timestamp': datetime.now().isoformat(),
            'resumo': {
                'total_capturas': len(capturas),
                'duracao_segundos': round(duracao_real, 2),
                'capturas_por_minuto': round((len(capturas) / duracao_real) * 60, 2),
                'total_pessoas': estatisticas.get('total_pessoas', 0),
                'total_objetos': estatisticas.get('total_objetos', 0),
                'total_interacoes': estatisticas.get('total_interacoes', 0),
                'movimento_geral': estatisticas.get('movimento_geral', 0),
                'media_pessoas_por_captura': estatisticas.get('media_pessoas_por_captura', 0),
                'media_objetos_por_captura': estatisticas.get('media_objetos_por_captura', 0),
                'periodo_maior_atividade': estatisticas.get('periodo_maior_atividade', 'N/A')
            },
            'deteccoes': {
                'pessoas': [],
                'objetos': []
            },
            'analises': {
                'movimentos': [],
                'interacoes': [],
                'atividades_faciais': []
            },
            'capturas': capturas,
            'narrativa': narrativa,
            'status': 'sucesso'
        }
        
        # Consolida todas as detecções
        todas_pessoas = []
        todos_objetos = []
        todos_movimentos = []
        todas_interacoes = []
        
        for captura in capturas:
            deteccoes = captura.get('deteccoes', {})
            analises = captura.get('analises', {})
            
            todas_pessoas.extend(deteccoes.get('pessoas', []))
            todos_objetos.extend(deteccoes.get('objetos', []))
            todos_movimentos.extend(analises.get('movimentos', []))
            todas_interacoes.extend(analises.get('interacoes', []))
        
        relatorio_final['deteccoes']['pessoas'] = todas_pessoas
        relatorio_final['deteccoes']['objetos'] = todos_objetos
        relatorio_final['analises']['movimentos'] = todos_movimentos
        relatorio_final['analises']['interacoes'] = todas_interacoes
        
        # Salva relatório
        timestamp_relatorio = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_relatorio = f"relatorio_{timestamp_relatorio}.json"
        caminho_relatorio = os.path.join("relatorios", nome_relatorio)
        
        with open(caminho_relatorio, 'w', encoding='utf-8') as f:
            json.dump(relatorio_final, f, indent=2, ensure_ascii=False)
        
        # Gera gráficos
        nome_grafico = f"graficos_{timestamp_relatorio}.png"
        self.gerar_graficos(capturas, nome_grafico)
        
        # Exibe resumo final
        print("\n" + "="*60)
        print("📊 RESUMO FINAL - FORMATO TESTE_DETECTOR_AVANCADO")
        print("="*60)
        print(f"📸 Total de capturas: {len(capturas)}")
        print(f"⏱️ Duração real: {duracao_real:.2f}s")
        print(f"📈 Capturas/minuto: {(len(capturas) / duracao_real) * 60:.2f}")
        print(f"👥 Total de pessoas: {estatisticas.get('total_pessoas', 0)}")
        print(f"📦 Total de objetos: {estatisticas.get('total_objetos', 0)}")
        print(f"🔄 Total de interações: {estatisticas.get('total_interacoes', 0)}")
        print(f"🎯 Período de maior atividade: {estatisticas.get('periodo_maior_atividade', 'N/A')}")
        print(f"📄 Relatório salvo: {caminho_relatorio}")
        print(f"📊 Gráficos salvos: relatorios/graficos/{nome_grafico}")
        print("\n📝 NARRATIVA:")
        print(f"{narrativa}")
        print("="*60)

if __name__ == "__main__":
    monitor = MonitorTela()
    monitor.monitorar(duracao_segundos=60, intervalo_segundos=0.1)