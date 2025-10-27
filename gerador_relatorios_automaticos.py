import os
import json
import time
import threading
from datetime import datetime, timedelta
import schedule
from detector_avancado import DetectorAvancado
import pyautogui
import numpy as np
import cv2

class GeradorRelatoriosAutomaticos:
    def __init__(self, intervalo_captura=30, intervalo_relatorio=10):
        """
        Inicializa o gerador de relatórios automáticos
        
        Args:
            intervalo_captura (int): Intervalo entre capturas em segundos
            intervalo_relatorio (int): Intervalo entre relatórios em minutos
        """
        self.intervalo_captura = intervalo_captura
        self.intervalo_relatorio = intervalo_relatorio
        self.detector = DetectorAvancado()
        self.dados_sessao = []
        self.executando = False
        self.thread_captura = None
        self.thread_scheduler = None
        
        # Criar diretórios necessários
        os.makedirs("capturas_automaticas", exist_ok=True)
        os.makedirs("relatorios_automaticos", exist_ok=True)
        
    def iniciar_monitoramento_automatico(self):
        """Inicia o monitoramento automático"""
        if not self.executando:
            self.executando = True
            print(f"Iniciando monitoramento automático...")
            print(f"Intervalo de captura: {self.intervalo_captura}s")
            print(f"Intervalo de relatório: {self.intervalo_relatorio}min")
            
            # Configurar agendamento de relatórios
            schedule.every(self.intervalo_relatorio).minutes.do(self.gerar_relatorio_periodico)
            
            # Iniciar threads
            self.thread_captura = threading.Thread(target=self.loop_captura, daemon=True)
            self.thread_scheduler = threading.Thread(target=self.loop_scheduler, daemon=True)
            
            self.thread_captura.start()
            self.thread_scheduler.start()
            
            print("Monitoramento automático iniciado!")
            
    def parar_monitoramento_automatico(self):
        """Para o monitoramento automático"""
        self.executando = False
        schedule.clear()
        print("Monitoramento automático parado!")
        
    def loop_captura(self):
        """Loop principal de captura"""
        contador = 0
        
        while self.executando:
            try:
                # Capturar tela
                screenshot = pyautogui.screenshot()
                imagem = np.array(screenshot)
                imagem = cv2.cvtColor(imagem, cv2.COLOR_RGB2BGR)
                
                # Salvar temporariamente para processamento
                temp_filename = f"temp_capture_{contador}.jpg"
                cv2.imwrite(temp_filename, imagem)
                
                # Processar com detector
                resultado = self.detector.detectar_objetos_pessoas(temp_filename)
                
                # Remover arquivo temporário
                os.remove(temp_filename)
                
                # Adicionar metadados
                resultado['timestamp'] = datetime.now().isoformat()
                resultado['captura_numero'] = contador
                
                # Salvar captura (opcional, para debug)
                if contador % 10 == 0:  # Salvar a cada 10 capturas
                    nome_captura = f"capturas_automaticas/captura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(nome_captura, imagem)
                
                # Adicionar aos dados
                self.dados_sessao.append(resultado)
                
                # Log de progresso
                pessoas = len(resultado.get('pessoas', []))
                objetos = len(resultado.get('objetos', []))
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Captura {contador}: "
                      f"{pessoas} pessoas, {objetos} objetos")
                
                contador += 1
                
                # Aguardar próxima captura
                time.sleep(self.intervalo_captura)
                
            except Exception as e:
                print(f"Erro na captura {contador}: {e}")
                time.sleep(5)  # Aguardar antes de tentar novamente
                
    def loop_scheduler(self):
        """Loop do agendador de tarefas"""
        while self.executando:
            schedule.run_pending()
            time.sleep(1)
            
    def gerar_relatorio_periodico(self):
        """Gera relatório periódico"""
        if not self.dados_sessao:
            print("Nenhum dado disponível para relatório")
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"relatorios_automaticos/relatorio_automatico_{timestamp}.json"
            
            # Gerar relatório
            relatorio = self.gerar_relatorio_completo()
            
            # Salvar
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False)
                
            print(f"Relatório automático gerado: {nome_arquivo}")
            
            # Limpar dados antigos (manter apenas última hora)
            self.limpar_dados_antigos()
            
        except Exception as e:
            print(f"Erro ao gerar relatório automático: {e}")
            
    def gerar_relatorio_completo(self):
        """Gera relatório completo com análises detalhadas"""
        if not self.dados_sessao:
            return {}
            
        agora = datetime.now()
        inicio_periodo = agora - timedelta(minutes=self.intervalo_relatorio)
        
        # Filtrar dados do período
        dados_periodo = [
            d for d in self.dados_sessao 
            if datetime.fromisoformat(d['timestamp']) >= inicio_periodo
        ]
        
        if not dados_periodo:
            return {}
            
        # Estatísticas básicas
        total_capturas = len(dados_periodo)
        total_pessoas = sum(len(d.get('pessoas', [])) for d in dados_periodo)
        total_objetos = sum(len(d.get('objetos', [])) for d in dados_periodo)
        
        # Análise de atividades
        atividades = []
        posturas = []
        movimentos_mao = []
        movimentos_cabeca = []
        
        for dados in dados_periodo:
            for pessoa in dados.get('pessoas', []):
                if 'atividade_provavel' in pessoa:
                    atividades.append(pessoa['atividade_provavel'])
                if 'postura' in pessoa:
                    posturas.append(pessoa['postura'])
                if 'movimento_mao' in pessoa:
                    movimentos_mao.append(pessoa['movimento_mao'])
                if 'movimento_cabeca' in pessoa:
                    movimentos_cabeca.append(pessoa['movimento_cabeca'])
        
        # Análise temporal
        atividades_por_hora = {}
        for dados in dados_periodo:
            hora = datetime.fromisoformat(dados['timestamp']).strftime('%H:00')
            if hora not in atividades_por_hora:
                atividades_por_hora[hora] = []
            
            for pessoa in dados.get('pessoas', []):
                if 'atividade_provavel' in pessoa:
                    atividades_por_hora[hora].append(pessoa['atividade_provavel'])
        
        # Gerar narrativa consolidada
        narrativa = self.gerar_narrativa_consolidada(dados_periodo)
        
        relatorio = {
            'periodo': {
                'inicio': inicio_periodo.isoformat(),
                'fim': agora.isoformat(),
                'duracao_minutos': self.intervalo_relatorio
            },
            'estatisticas_gerais': {
                'total_capturas': total_capturas,
                'total_pessoas_detectadas': total_pessoas,
                'total_objetos_detectados': total_objetos,
                'media_pessoas_por_captura': total_pessoas / total_capturas if total_capturas > 0 else 0,
                'media_objetos_por_captura': total_objetos / total_capturas if total_capturas > 0 else 0
            },
            'analise_atividades': {
                'atividades_frequentes': self.contar_frequencias(atividades),
                'posturas_frequentes': self.contar_frequencias(posturas),
                'movimentos_mao_frequentes': self.contar_frequencias(movimentos_mao),
                'movimentos_cabeca_frequentes': self.contar_frequencias(movimentos_cabeca)
            },
            'analise_temporal': {
                'atividades_por_hora': {
                    hora: self.contar_frequencias(ativs) 
                    for hora, ativs in atividades_por_hora.items()
                }
            },
            'narrativa_consolidada': narrativa,
            'resumo_executivo': self.gerar_resumo_executivo(dados_periodo),
            'alertas': self.gerar_alertas(dados_periodo)
        }
        
        return relatorio
        
    def gerar_narrativa_consolidada(self, dados_periodo):
        """Gera narrativa consolidada do período"""
        if not dados_periodo:
            return "Nenhuma atividade detectada no período."
            
        # Coletar todas as narrativas do período
        narrativas = [d.get('narrativa', '') for d in dados_periodo if d.get('narrativa')]
        
        # Análise de padrões
        atividades_detectadas = []
        for dados in dados_periodo:
            for pessoa in dados.get('pessoas', []):
                if 'atividade_provavel' in pessoa:
                    atividades_detectadas.append(pessoa['atividade_provavel'])
        
        atividades_freq = self.contar_frequencias(atividades_detectadas)
        
        # Construir narrativa
        narrativa = f"Durante os últimos {self.intervalo_relatorio} minutos, "
        narrativa += f"foram realizadas {len(dados_periodo)} capturas. "
        
        if atividades_freq:
            atividade_principal = max(atividades_freq.items(), key=lambda x: x[1])
            narrativa += f"A atividade mais frequente foi '{atividade_principal[0]}' "
            narrativa += f"({atividade_principal[1]} ocorrências). "
            
            if len(atividades_freq) > 1:
                outras_atividades = sorted(atividades_freq.items(), key=lambda x: x[1], reverse=True)[1:3]
                narrativa += "Outras atividades detectadas incluem: "
                narrativa += ", ".join([f"'{ativ}' ({freq}x)" for ativ, freq in outras_atividades])
                narrativa += ". "
        
        # Adicionar informações sobre pessoas e objetos
        total_pessoas = sum(len(d.get('pessoas', [])) for d in dados_periodo)
        total_objetos = sum(len(d.get('objetos', [])) for d in dados_periodo)
        
        if total_pessoas > 0:
            media_pessoas = total_pessoas / len(dados_periodo)
            narrativa += f"Em média, {media_pessoas:.1f} pessoas foram detectadas por captura. "
            
        if total_objetos > 0:
            media_objetos = total_objetos / len(dados_periodo)
            narrativa += f"Foram detectados em média {media_objetos:.1f} objetos por captura."
            
        return narrativa
        
    def gerar_resumo_executivo(self, dados_periodo):
        """Gera resumo executivo do período"""
        if not dados_periodo:
            return "Nenhuma atividade para resumir."
            
        # Calcular métricas principais
        total_capturas = len(dados_periodo)
        capturas_com_pessoas = sum(1 for d in dados_periodo if len(d.get('pessoas', [])) > 0)
        taxa_ocupacao = (capturas_com_pessoas / total_capturas) * 100 if total_capturas > 0 else 0
        
        # Atividades principais
        atividades = []
        for dados in dados_periodo:
            for pessoa in dados.get('pessoas', []):
                if 'atividade_provavel' in pessoa:
                    atividades.append(pessoa['atividade_provavel'])
        
        atividades_freq = self.contar_frequencias(atividades)
        
        resumo = {
            'taxa_ocupacao_percent': round(taxa_ocupacao, 1),
            'capturas_com_atividade': capturas_com_pessoas,
            'total_capturas': total_capturas,
            'atividade_principal': max(atividades_freq.items(), key=lambda x: x[1])[0] if atividades_freq else None,
            'total_atividades_detectadas': len(atividades),
            'variedade_atividades': len(atividades_freq)
        }
        
        return resumo
        
    def gerar_alertas(self, dados_periodo):
        """Gera alertas baseados nos dados do período"""
        alertas = []
        
        if not dados_periodo:
            alertas.append({
                'tipo': 'info',
                'mensagem': 'Nenhuma atividade detectada no período'
            })
            return alertas
            
        # Verificar inatividade prolongada
        capturas_sem_pessoas = sum(1 for d in dados_periodo if len(d.get('pessoas', [])) == 0)
        if capturas_sem_pessoas > len(dados_periodo) * 0.8:
            alertas.append({
                'tipo': 'warning',
                'mensagem': f'Baixa atividade detectada: {capturas_sem_pessoas}/{len(dados_periodo)} capturas sem pessoas'
            })
            
        # Verificar atividade intensa
        max_pessoas = max(len(d.get('pessoas', [])) for d in dados_periodo)
        if max_pessoas > 5:
            alertas.append({
                'tipo': 'info',
                'mensagem': f'Pico de atividade: até {max_pessoas} pessoas detectadas simultaneamente'
            })
            
        return alertas
        
    def contar_frequencias(self, lista):
        """Conta frequências de itens em uma lista"""
        freq = {}
        for item in lista:
            freq[item] = freq.get(item, 0) + 1
        return freq
        
    def limpar_dados_antigos(self):
        """Remove dados mais antigos que 1 hora"""
        agora = datetime.now()
        limite = agora - timedelta(hours=1)
        
        dados_recentes = [
            d for d in self.dados_sessao 
            if datetime.fromisoformat(d['timestamp']) >= limite
        ]
        
        removidos = len(self.dados_sessao) - len(dados_recentes)
        self.dados_sessao = dados_recentes
        
        if removidos > 0:
            print(f"Removidos {removidos} registros antigos da memória")
            
    def executar_modo_daemon(self):
        """Executa em modo daemon (background)"""
        try:
            self.iniciar_monitoramento_automatico()
            
            print("Pressione Ctrl+C para parar o monitoramento...")
            while self.executando:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nParando monitoramento...")
            self.parar_monitoramento_automatico()
            
        except Exception as e:
            print(f"Erro no monitoramento: {e}")
            self.parar_monitoramento_automatico()

if __name__ == "__main__":
    # Configuração padrão: captura a cada 30s, relatório a cada 10min
    gerador = GeradorRelatoriosAutomaticos(intervalo_captura=30, intervalo_relatorio=10)
    gerador.executar_modo_daemon()