#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do sistema de monitoramento com alta frequência
"""

from monitor_tela import MonitorTela

if __name__ == "__main__":
    print("🚀 Testando sistema com alta frequência...")
    
    # Cria monitor com intervalo de 0.1 segundos (10 FPS)
    monitor = MonitorTela()
    
    # Testa por 10 segundos
    monitor.monitorar(duracao_segundos=10, intervalo_segundos=0.1)
    
    print("✅ Teste concluído!")