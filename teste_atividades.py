#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das melhorias de análise de atividades humanas
"""

from detector_avancado import DetectorAvancado
import numpy as np
import cv2

def testar_analise_atividades():
    """Testa o sistema de análise de atividades"""
    print("=== TESTE DE ANÁLISE DE ATIVIDADES ===")
    
    # Criar detector
    detector = DetectorAvancado()
    
    # Simular frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Forçar detecção simulada de pessoa
    resultado = detector._deteccao_simulada(frame)
    
    print(f"Pessoas detectadas: {len(resultado['deteccoes']['pessoas'])}")
    print(f"Objetos detectados: {len(resultado['deteccoes']['objetos'])}")
    
    # Mostrar atividades faciais
    atividades = resultado['analises']['atividades_faciais']
    for i, atividade in enumerate(atividades):
        print(f"\nPessoa {i+1}:")
        print(f"  - Postura: {atividade['postura_corporal']}")
        print(f"  - Movimento mãos: {atividade['movimento_maos']}")
        print(f"  - Movimento cabeça: {atividade['movimento_cabeca']}")
        print(f"  - Atividade provável: {atividade['atividade_provavel']}")
    
    print(f"\nNarrativa: {resultado['narrativa']}")
    
    return resultado

if __name__ == "__main__":
    testar_analise_atividades()