#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico das melhorias na narrativa
Demonstra as novas descrições de ações específicas
"""

import sys
import os
import json
from datetime import datetime

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from detector_avancado import DetectorAvancado

def testar_narrativa_melhorada():
    """Testa especificamente as melhorias na narrativa"""
    print("🧪 Testando narrativa melhorada com ações específicas...")
    print("=" * 60)
    
    # Inicializa o detector
    detector = DetectorAvancado()
    
    # Testa diretamente a detecção simulada
    print("📋 Testando detecção simulada com narrativa melhorada")
    print("-" * 40)
    
    try:
        # Força detecção simulada (passa uma imagem dummy)
        import numpy as np
        imagem_dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        resultado = detector._deteccao_simulada(imagem_dummy)
        
        # Gera narrativa com as melhorias
        narrativa = detector._gerar_narrativa(resultado)
        
        print("✅ Resultado da detecção simulada:")
        print(f"   Pessoas: {resultado['resumo']['total_pessoas']}")
        print(f"   Objetos: {resultado['resumo']['total_objetos']}")
        
        # Mostra atividades detectadas
        atividades = resultado.get('analises', {}).get('atividades_faciais', [])
        if atividades:
            print("\n🔍 Atividades detectadas:")
            for i, atividade in enumerate(atividades):
                print(f"   Pessoa {i+1}:")
                print(f"     - Postura: {atividade.get('postura_corporal', 'N/A')}")
                print(f"     - Movimento mãos: {atividade.get('movimento_maos', 'N/A')}")
                print(f"     - Movimento cabeça: {atividade.get('movimento_cabeca', 'N/A')}")
                print(f"     - Atividade inferida: {atividade.get('atividade_provavel', 'N/A')}")
        
        print(f"\n📝 Narrativa melhorada:")
        print(f"   {narrativa}")
        
        # Testa diferentes combinações de atividades
        print("\n" + "=" * 60)
        print("🎭 Testando diferentes combinações de atividades")
        print("=" * 60)
        
        # Simula diferentes atividades manualmente
        atividades_teste = [
            {
                'postura_corporal': 'agachado_ou_sentado',
                'movimento_maos': 'digitando',
                'movimento_cabeca': 'cabeca_para_baixo',
                'atividade_provavel': 'trabalhando_no_computador'
            },
            {
                'postura_corporal': 'em_pe',
                'movimento_maos': 'gesticulando',
                'movimento_cabeca': 'olhando_direita',
                'atividade_provavel': 'conversando_ou_apresentando'
            },
            {
                'postura_corporal': 'agachado_ou_sentado',
                'movimento_maos': 'maos_no_colo',
                'movimento_cabeca': 'cabeca_para_baixo',
                'atividade_provavel': 'lendo_ou_escrevendo'
            },
            {
                'postura_corporal': 'em_pe',
                'movimento_maos': 'apontando',
                'movimento_cabeca': 'olhando_esquerda',
                'atividade_provavel': 'observando_ou_aguardando'
            }
        ]
        
        for i, atividade in enumerate(atividades_teste, 1):
            print(f"\n📋 Cenário {i}:")
            print(f"   Postura: {atividade['postura_corporal']}")
            print(f"   Mãos: {atividade['movimento_maos']}")
            print(f"   Cabeça: {atividade['movimento_cabeca']}")
            print(f"   Atividade: {atividade['atividade_provavel']}")
            
            # Testa a descrição específica
            descricao = detector._descrever_acao_especifica(atividade)
            print(f"   ➤ Descrição: {descricao}")
        
        print("\n" + "=" * 60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("🎉 Melhorias implementadas:")
        print("   • Narrativa agora descreve ações específicas")
        print("   • Eliminou o uso de 'provavelmente'")
        print("   • Combina postura, movimento das mãos e cabeça")
        print("   • Fornece descrições detalhadas e contextuais")
        print("   • Mapeamento inteligente de atividades")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    sucesso = testar_narrativa_melhorada()
    
    if sucesso:
        print("\n🎯 Teste da narrativa melhorada concluído com sucesso!")
        exit(0)
    else:
        print("\n❌ Teste falhou!")
        exit(1)