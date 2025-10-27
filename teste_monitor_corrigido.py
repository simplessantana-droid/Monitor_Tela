#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do sistema de monitoramento corrigido
"""

from monitor_tela import MonitorTela
import time

def main():
    print("=== TESTE DO SISTEMA CORRIGIDO ===")
    print("Testando detecção de pessoas por 10 segundos...")
    
    # Inicializa monitor
    monitor = MonitorTela()
    
    # Executa monitoramento por 10 segundos com intervalo de 1 segundo
    monitor.monitorar(duracao_segundos=10, intervalo_segundos=1.0)
    
    print("\n✅ Teste do sistema corrigido concluído!")
    print("Verifique o relatório gerado na pasta 'relatorios'")

if __name__ == "__main__":
    main()