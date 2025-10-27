import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import os
from datetime import datetime
import numpy as np
from PIL import Image, ImageTk
import cv2
from detector_avancado import DetectorAvancado
import pyautogui
import queue

class MonitorTempoReal:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Monitor de Atividades em Tempo Real")
        self.root.geometry("1200x800")
        
        # Variáveis de controle
        self.monitorando = False
        self.detector = DetectorAvancado()
        self.thread_monitor = None
        self.dados_sessao = []
        self.contador_capturas = 0
        self.inicio_sessao = None
        
        # Queue para comunicação entre threads
        self.queue_resultados = queue.Queue()
        
        # Configurar interface
        self.configurar_interface()
        
        # Timer para atualizar interface
        self.root.after(100, self.atualizar_interface)
        
    def configurar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="Monitor de Atividades em Tempo Real", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de controles
        controles_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        controles_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botões de controle
        self.btn_iniciar = ttk.Button(controles_frame, text="Iniciar Monitoramento", 
                                     command=self.iniciar_monitoramento)
        self.btn_iniciar.grid(row=0, column=0, padx=(0, 10))
        
        self.btn_parar = ttk.Button(controles_frame, text="Parar Monitoramento", 
                                   command=self.parar_monitoramento, state='disabled')
        self.btn_parar.grid(row=0, column=1, padx=(0, 10))
        
        self.btn_relatorio = ttk.Button(controles_frame, text="Gerar Relatório", 
                                       command=self.gerar_relatorio)
        self.btn_relatorio.grid(row=0, column=2, padx=(0, 10))
        
        # Configurações
        config_frame = ttk.LabelFrame(controles_frame, text="Configurações", padding="5")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(config_frame, text="Intervalo (segundos):").grid(row=0, column=0, padx=(0, 5))
        self.intervalo_var = tk.StringVar(value="5")
        intervalo_spin = ttk.Spinbox(config_frame, from_=1, to=60, width=10, 
                                    textvariable=self.intervalo_var)
        intervalo_spin.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(config_frame, text="Relatório automático (min):").grid(row=0, column=2, padx=(0, 5))
        self.relatorio_auto_var = tk.StringVar(value="10")
        relatorio_spin = ttk.Spinbox(config_frame, from_=1, to=120, width=10, 
                                    textvariable=self.relatorio_auto_var)
        relatorio_spin.grid(row=0, column=3)
        
        # Frame principal de conteúdo
        conteudo_frame = ttk.Frame(main_frame)
        conteudo_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        conteudo_frame.columnconfigure(0, weight=1)
        conteudo_frame.columnconfigure(1, weight=1)
        conteudo_frame.rowconfigure(0, weight=1)
        
        # Frame de status e estatísticas
        status_frame = ttk.LabelFrame(conteudo_frame, text="Status e Estatísticas", padding="10")
        status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(1, weight=1)
        
        # Status atual
        self.status_label = ttk.Label(status_frame, text="Status: Parado", 
                                     font=('Arial', 12, 'bold'))
        self.status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Área de estatísticas
        self.stats_text = scrolledtext.ScrolledText(status_frame, height=15, width=40)
        self.stats_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame de narrativa em tempo real
        narrativa_frame = ttk.LabelFrame(conteudo_frame, text="Narrativa em Tempo Real", padding="10")
        narrativa_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        narrativa_frame.columnconfigure(0, weight=1)
        narrativa_frame.rowconfigure(0, weight=1)
        
        # Área de narrativa
        self.narrativa_text = scrolledtext.ScrolledText(narrativa_frame, height=20, width=50)
        self.narrativa_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Barra de status
        self.status_bar = ttk.Label(main_frame, text="Pronto para iniciar monitoramento", 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def iniciar_monitoramento(self):
        """Inicia o monitoramento em tempo real"""
        if not self.monitorando:
            self.monitorando = True
            self.inicio_sessao = datetime.now()
            self.dados_sessao = []
            self.contador_capturas = 0
            
            # Atualizar interface
            self.btn_iniciar.config(state='disabled')
            self.btn_parar.config(state='normal')
            self.status_label.config(text="Status: Monitorando", foreground='green')
            self.status_bar.config(text="Monitoramento iniciado...")
            
            # Limpar áreas de texto
            self.stats_text.delete(1.0, tk.END)
            self.narrativa_text.delete(1.0, tk.END)
            
            # Iniciar thread de monitoramento
            self.thread_monitor = threading.Thread(target=self.loop_monitoramento, daemon=True)
            self.thread_monitor.start()
            
            # Iniciar timer para relatórios automáticos
            self.agendar_relatorio_automatico()
            
    def parar_monitoramento(self):
        """Para o monitoramento"""
        self.monitorando = False
        
        # Atualizar interface
        self.btn_iniciar.config(state='normal')
        self.btn_parar.config(state='disabled')
        self.status_label.config(text="Status: Parado", foreground='red')
        self.status_bar.config(text="Monitoramento parado")
        
    def loop_monitoramento(self):
        """Loop principal de monitoramento"""
        intervalo = int(self.intervalo_var.get())
        
        while self.monitorando:
            try:
                # Capturar tela
                screenshot = pyautogui.screenshot()
                imagem = np.array(screenshot)
                imagem = cv2.cvtColor(imagem, cv2.COLOR_RGB2BGR)
                
                # Processar com detector
                resultado = self.detector.detectar_atividades(imagem)
                
                # Adicionar timestamp
                resultado['timestamp'] = datetime.now().isoformat()
                resultado['captura_numero'] = self.contador_capturas
                
                # Adicionar aos dados da sessão
                self.dados_sessao.append(resultado)
                self.contador_capturas += 1
                
                # Enviar resultado para interface
                self.queue_resultados.put(resultado)
                
                # Aguardar próxima captura
                time.sleep(intervalo)
                
            except Exception as e:
                print(f"Erro no monitoramento: {e}")
                self.queue_resultados.put({'erro': str(e)})
                
    def atualizar_interface(self):
        """Atualiza a interface com novos resultados"""
        try:
            while not self.queue_resultados.empty():
                resultado = self.queue_resultados.get_nowait()
                
                if 'erro' in resultado:
                    self.status_bar.config(text=f"Erro: {resultado['erro']}")
                else:
                    self.processar_resultado(resultado)
                    
        except queue.Empty:
            pass
        
        # Reagendar atualização
        self.root.after(100, self.atualizar_interface)
        
    def processar_resultado(self, resultado):
        """Processa um resultado de detecção"""
        timestamp = datetime.fromisoformat(resultado['timestamp'])
        
        # Atualizar estatísticas
        self.atualizar_estatisticas(resultado, timestamp)
        
        # Atualizar narrativa
        self.atualizar_narrativa(resultado, timestamp)
        
        # Atualizar barra de status
        pessoas = len(resultado.get('pessoas', []))
        objetos = len(resultado.get('objetos', []))
        self.status_bar.config(text=f"Última captura: {timestamp.strftime('%H:%M:%S')} - "
                                   f"Pessoas: {pessoas}, Objetos: {objetos}")
        
    def atualizar_estatisticas(self, resultado, timestamp):
        """Atualiza a área de estatísticas"""
        pessoas = len(resultado.get('pessoas', []))
        objetos = len(resultado.get('objetos', []))
        
        # Calcular estatísticas da sessão
        if self.dados_sessao:
            total_pessoas = sum(len(r.get('pessoas', [])) for r in self.dados_sessao)
            total_objetos = sum(len(r.get('objetos', [])) for r in self.dados_sessao)
            media_pessoas = total_pessoas / len(self.dados_sessao)
            media_objetos = total_objetos / len(self.dados_sessao)
            
            # Atividades mais frequentes
            atividades = []
            for r in self.dados_sessao:
                for pessoa in r.get('pessoas', []):
                    if 'atividade_provavel' in pessoa:
                        atividades.append(pessoa['atividade_provavel'])
            
            atividades_freq = {}
            for atividade in atividades:
                atividades_freq[atividade] = atividades_freq.get(atividade, 0) + 1
            
            # Atualizar texto
            stats_text = f"""ESTATÍSTICAS DA SESSÃO
{'='*30}
Início: {self.inicio_sessao.strftime('%H:%M:%S')}
Duração: {timestamp - self.inicio_sessao}
Capturas: {len(self.dados_sessao)}

ÚLTIMA CAPTURA
{'='*30}
Horário: {timestamp.strftime('%H:%M:%S')}
Pessoas detectadas: {pessoas}
Objetos detectados: {objetos}

MÉDIAS DA SESSÃO
{'='*30}
Pessoas por captura: {media_pessoas:.1f}
Objetos por captura: {media_objetos:.1f}

ATIVIDADES MAIS FREQUENTES
{'='*30}"""
            
            for atividade, freq in sorted(atividades_freq.items(), key=lambda x: x[1], reverse=True)[:5]:
                stats_text += f"\n{atividade}: {freq}x"
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            
    def atualizar_narrativa(self, resultado, timestamp):
        """Atualiza a narrativa em tempo real"""
        narrativa = resultado.get('narrativa', 'Nenhuma atividade detectada')
        
        # Adicionar timestamp e separador
        entrada = f"[{timestamp.strftime('%H:%M:%S')}] {narrativa}\n{'-'*50}\n\n"
        
        # Inserir no início do texto
        self.narrativa_text.insert(1.0, entrada)
        
        # Limitar o número de entradas (manter apenas as últimas 20)
        linhas = self.narrativa_text.get(1.0, tk.END).split('\n')
        if len(linhas) > 100:  # Aproximadamente 20 entradas
            texto_limitado = '\n'.join(linhas[:100])
            self.narrativa_text.delete(1.0, tk.END)
            self.narrativa_text.insert(1.0, texto_limitado)
            
    def gerar_relatorio(self):
        """Gera relatório da sessão atual"""
        if not self.dados_sessao:
            messagebox.showwarning("Aviso", "Nenhum dado para gerar relatório")
            return
            
        try:
            # Criar diretório de relatórios se não existir
            os.makedirs("relatorios_tempo_real", exist_ok=True)
            
            # Nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"relatorios_tempo_real/relatorio_{timestamp}.json"
            
            # Gerar estatísticas consolidadas
            relatorio = self.gerar_estatisticas_consolidadas()
            
            # Salvar relatório
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False)
                
            messagebox.showinfo("Sucesso", f"Relatório salvo em: {nome_arquivo}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
            
    def gerar_estatisticas_consolidadas(self):
        """Gera estatísticas consolidadas da sessão"""
        if not self.dados_sessao:
            return {}
            
        # Estatísticas básicas
        total_capturas = len(self.dados_sessao)
        total_pessoas = sum(len(r.get('pessoas', [])) for r in self.dados_sessao)
        total_objetos = sum(len(r.get('objetos', [])) for r in self.dados_sessao)
        
        # Atividades detectadas
        atividades = []
        posturas = []
        movimentos_mao = []
        
        for resultado in self.dados_sessao:
            for pessoa in resultado.get('pessoas', []):
                if 'atividade_provavel' in pessoa:
                    atividades.append(pessoa['atividade_provavel'])
                if 'postura' in pessoa:
                    posturas.append(pessoa['postura'])
                if 'movimento_mao' in pessoa:
                    movimentos_mao.append(pessoa['movimento_mao'])
        
        # Contar frequências
        def contar_frequencias(lista):
            freq = {}
            for item in lista:
                freq[item] = freq.get(item, 0) + 1
            return freq
        
        relatorio = {
            'sessao': {
                'inicio': self.inicio_sessao.isoformat() if self.inicio_sessao else None,
                'fim': datetime.now().isoformat(),
                'duracao_minutos': (datetime.now() - self.inicio_sessao).total_seconds() / 60 if self.inicio_sessao else 0
            },
            'estatisticas': {
                'total_capturas': total_capturas,
                'total_pessoas_detectadas': total_pessoas,
                'total_objetos_detectados': total_objetos,
                'media_pessoas_por_captura': total_pessoas / total_capturas if total_capturas > 0 else 0,
                'media_objetos_por_captura': total_objetos / total_capturas if total_capturas > 0 else 0
            },
            'atividades_frequentes': contar_frequencias(atividades),
            'posturas_frequentes': contar_frequencias(posturas),
            'movimentos_mao_frequentes': contar_frequencias(movimentos_mao),
            'dados_brutos': self.dados_sessao
        }
        
        return relatorio
        
    def agendar_relatorio_automatico(self):
        """Agenda geração automática de relatórios"""
        if self.monitorando:
            intervalo_min = int(self.relatorio_auto_var.get())
            # Reagendar para o próximo relatório
            self.root.after(intervalo_min * 60 * 1000, self.relatorio_automatico)
            
    def relatorio_automatico(self):
        """Gera relatório automático"""
        if self.monitorando and self.dados_sessao:
            self.gerar_relatorio()
            # Reagendar próximo relatório
            self.agendar_relatorio_automatico()
            
    def executar(self):
        """Executa a aplicação"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MonitorTempoReal()
    app.executar()