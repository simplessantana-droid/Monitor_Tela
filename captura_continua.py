#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Captura Contínua de Tela
Captura screenshots continuamente e processa com DetectorAvancado
"""

import os
import time
import json
from datetime import datetime
from detector_avancado import DetectorAvancado
import pyautogui
import cv2
import numpy as np

class CapturaContinua:
    def __init__(self, intervalo_captura=0.5, intervalo_relatorio=60):
        """
        Inicializa o sistema de captura contínua
        
        Args:
            intervalo_captura (float): Intervalo entre capturas em segundos
            intervalo_relatorio (int): Intervalo entre relatórios em segundos
        """
        self.intervalo_captura = intervalo_captura
        self.intervalo_relatorio = intervalo_relatorio
        self.detector = DetectorAvancado()
        self.contador_capturas = 0
        self.ultimo_relatorio = time.time()
        self.estatisticas = {
            'total_pessoas': 0,
            'total_objetos': 0,
            'capturas_realizadas': 0,
            'inicio_sessao': datetime.now().isoformat(),
            'atividades_detectadas': []
        }
        
        # Criar diretórios necessários
        os.makedirs('capturas_continuas', exist_ok=True)
        os.makedirs('relatorios_continuas', exist_ok=True)
        
        print("🚀 Sistema de Captura Contínua ULTRA-RÁPIDA Iniciado!")
        print(f"📸 Intervalo de captura: {intervalo_captura} segundos")
        print(f"📊 Relatórios automáticos: a cada {intervalo_relatorio} segundos ({intervalo_relatorio/60:.1f} minutos)")
        print("🔄 Capturando indefinidamente... (Ctrl+C para parar)")
        print("-" * 60)
    
    def capturar_tela(self):
        """Captura a tela atual"""
        try:
            # Capturar screenshot
            screenshot = pyautogui.screenshot()
            
            # Converter para array numpy
            img_array = np.array(screenshot)
            
            # Converter RGB para BGR (OpenCV)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            return img_bgr
        except Exception as e:
            print(f"❌ Erro ao capturar tela: {e}")
            return None
    
    def salvar_captura(self, imagem):
        """Salva a captura em arquivo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"capturas_continuas/captura_{timestamp}_{self.contador_capturas:04d}.jpg"
            
            cv2.imwrite(nome_arquivo, imagem)
            return nome_arquivo
        except Exception as e:
            print(f"❌ Erro ao salvar captura: {e}")
            return None
    
    def processar_captura(self, caminho_imagem):
        """Processa a captura com o DetectorAvancado"""
        try:
            resultado = self.detector.detectar_objetos_pessoas(caminho_imagem)
            
            if resultado:
                # Atualizar estatísticas
                pessoas = resultado.get('pessoas_detectadas', 0)
                objetos = resultado.get('objetos_detectados', 0)
                
                self.estatisticas['total_pessoas'] += pessoas
                self.estatisticas['total_objetos'] += objetos
                
                # Adicionar atividade detectada
                if pessoas > 0 or objetos > 0:
                    atividade = {
                        'timestamp': datetime.now().isoformat(),
                        'pessoas': pessoas,
                        'objetos': objetos,
                        'narrativa': resultado.get('narrativa_especifica', 'Atividade detectada')
                    }
                    self.estatisticas['atividades_detectadas'].append(atividade)
                
                return resultado
        except Exception as e:
            print(f"❌ Erro ao processar captura: {e}")
            return None
    
    def exibir_progresso(self, resultado):
        """Exibe o progresso da captura"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if resultado:
            pessoas = resultado.get('pessoas_detectadas', 0)
            objetos = resultado.get('objetos_detectados', 0)
            narrativa = resultado.get('narrativa_especifica', 'Nenhuma atividade específica')
            
            print(f"[{timestamp}] Captura #{self.contador_capturas:04d} | "
                  f"Pessoas: {pessoas} | Objetos: {objetos}")
            
            if pessoas > 0 or objetos > 0:
                print(f"  📝 {narrativa}")
        else:
            print(f"[{timestamp}] Captura #{self.contador_capturas:04d} | Sem detecções")
    
    def salvar_relatorio_periodico(self):
        """Salva relatório baseado no tempo (a cada minuto)"""
        tempo_atual = time.time()
        
        if tempo_atual - self.ultimo_relatorio >= self.intervalo_relatorio:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_relatorio = f"relatorios_continuas/relatorio_minuto_{timestamp}.json"
                
                tempo_sessao = tempo_atual - time.mktime(datetime.fromisoformat(self.estatisticas['inicio_sessao']).timetuple())
                capturas_por_minuto = round((self.contador_capturas / max(1, tempo_sessao)) * 60, 2)
                
                relatorio = {
                    'relatorio_periodico': {
                        'timestamp': datetime.now().isoformat(),
                        'intervalo_minutos': self.intervalo_relatorio / 60,
                        'capturas_neste_periodo': self.contador_capturas,
                        'tempo_sessao_segundos': round(tempo_sessao, 2)
                    },
                    'estatisticas_atuais': {
                        'total_pessoas_detectadas': self.estatisticas['total_pessoas'],
                        'total_objetos_detectados': self.estatisticas['total_objetos'],
                        'capturas_realizadas': self.contador_capturas,
                        'capturas_por_minuto': capturas_por_minuto,
                        'media_pessoas_por_captura': round(self.estatisticas['total_pessoas'] / max(1, self.contador_capturas), 2),
                        'media_objetos_por_captura': round(self.estatisticas['total_objetos'] / max(1, self.contador_capturas), 2)
                    },
                    'atividades_recentes': self.estatisticas['atividades_detectadas'][-20:],  # Últimas 20
                    'configuracao': {
                        'intervalo_captura_segundos': self.intervalo_captura,
                        'intervalo_relatorio_segundos': self.intervalo_relatorio
                    }
                }
                
                with open(nome_relatorio, 'w', encoding='utf-8') as f:
                    json.dump(relatorio, f, indent=2, ensure_ascii=False)
                
                print(f"\n📊 RELATÓRIO AUTOMÁTICO GERADO: {nome_relatorio}")
                print(f"   ⏱️ Capturas/min: {capturas_por_minuto} | Total: {self.contador_capturas}")
                print(f"   👥 Pessoas: {self.estatisticas['total_pessoas']} | 📦 Objetos: {self.estatisticas['total_objetos']}")
                print("-" * 60)
                
                # Atualizar timestamp do último relatório
                self.ultimo_relatorio = tempo_atual
                
            except Exception as e:
                print(f"❌ Erro ao salvar relatório: {e}")
    
    def executar(self):
        """Executa o loop principal de captura contínua"""
        try:
            while True:
                # Capturar tela
                imagem = self.capturar_tela()
                
                if imagem is not None:
                    self.contador_capturas += 1
                    self.estatisticas['capturas_realizadas'] = self.contador_capturas
                    
                    # Salvar captura
                    caminho_imagem = self.salvar_captura(imagem)
                    
                    if caminho_imagem:
                        # Processar com DetectorAvancado
                        resultado = self.processar_captura(caminho_imagem)
                        
                        # Exibir progresso
                        self.exibir_progresso(resultado)
                        
                        # Salvar relatório periódico
                        self.salvar_relatorio_periodico()
                
                # Aguardar próxima captura
                time.sleep(self.intervalo_captura)
                
        except KeyboardInterrupt:
            print("\n🛑 Captura interrompida pelo usuário")
            self.finalizar_sessao()
        except Exception as e:
            print(f"\n❌ Erro durante execução: {e}")
            self.finalizar_sessao()
    
    def finalizar_sessao(self):
        """Finaliza a sessão e salva relatório final"""
        try:
            print("\n📊 Gerando relatório final...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_relatorio_final = f"relatorios_continuas/relatorio_final_{timestamp}.json"
            
            tempo_total = datetime.now() - datetime.fromisoformat(self.estatisticas['inicio_sessao'])
            
            relatorio_final = {
                'sessao_completa': {
                    'inicio': self.estatisticas['inicio_sessao'],
                    'fim': datetime.now().isoformat(),
                    'duracao_total': str(tempo_total),
                    'capturas_realizadas': self.contador_capturas
                },
                'estatisticas_finais': {
                    'total_pessoas_detectadas': self.estatisticas['total_pessoas'],
                    'total_objetos_detectados': self.estatisticas['total_objetos'],
                    'media_pessoas_por_captura': round(self.estatisticas['total_pessoas'] / max(1, self.contador_capturas), 2),
                    'media_objetos_por_captura': round(self.estatisticas['total_objetos'] / max(1, self.contador_capturas), 2),
                    'capturas_por_minuto': round(self.contador_capturas / max(1, tempo_total.total_seconds() / 60), 2)
                },
                'todas_atividades': self.estatisticas['atividades_detectadas'],
                'timestamp_relatorio': datetime.now().isoformat()
            }
            
            with open(nome_relatorio_final, 'w', encoding='utf-8') as f:
                json.dump(relatorio_final, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Relatório final salvo: {nome_relatorio_final}")
            print(f"📈 Total de capturas: {self.contador_capturas}")
            print(f"⏱️ Duração: {tempo_total}")
            print(f"👥 Pessoas detectadas: {self.estatisticas['total_pessoas']}")
            print(f"📦 Objetos detectados: {self.estatisticas['total_objetos']}")
            
        except Exception as e:
            print(f"❌ Erro ao finalizar sessão: {e}")

if __name__ == "__main__":
    # Criar e executar sistema de captura contínua ULTRA-RÁPIDA
    # Captura a cada 0.5 segundos, relatório a cada 1 minuto (60 segundos)
    captura = CapturaContinua(intervalo_captura=0.5, intervalo_relatorio=60)
    captura.executar()