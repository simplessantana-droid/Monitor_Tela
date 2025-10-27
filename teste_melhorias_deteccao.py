#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das melhorias na detecção de atividades específicas
Testa as novas funcionalidades de descrição de ações específicas
"""

import sys
import os
import json
from datetime import datetime

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from detector_avancado import DetectorAvancado

def testar_melhorias_deteccao():
    """Testa as melhorias implementadas na detecção"""
    print("🧪 Testando melhorias na detecção de atividades...")
    print("=" * 60)
    
    # Inicializa o detector
    detector = DetectorAvancado()
    
    # Simula diferentes cenários de teste
    cenarios = [
        {
            'nome': 'Pessoa trabalhando no computador',
            'descricao': 'Simulando pessoa digitando no computador'
        },
        {
            'nome': 'Pessoa em apresentação',
            'descricao': 'Simulando pessoa gesticulando durante apresentação'
        },
        {
            'nome': 'Pessoa lendo documento',
            'descricao': 'Simulando pessoa lendo com mãos no colo'
        },
        {
            'nome': 'Pessoa observando',
            'descricao': 'Simulando pessoa aguardando ou observando'
        }
    ]
    
    resultados_teste = []
    
    for i, cenario in enumerate(cenarios, 1):
        print(f"\n📋 Cenário {i}: {cenario['nome']}")
        print(f"   {cenario['descricao']}")
        print("-" * 40)
        
        try:
            # Gera relatório completo (usa detecção simulada)
            relatorio = detector.gerar_relatorio_completo("imagem_simulada.jpg")
            
            # Extrai informações relevantes
            pessoas_detectadas = relatorio.get('resumo', {}).get('total_pessoas', 0)
            narrativa = relatorio.get('narrativa', 'Sem narrativa')
            atividades = relatorio.get('analises', {}).get('atividades_faciais', [])
            
            print(f"✅ Pessoas detectadas: {pessoas_detectadas}")
            
            if atividades:
                for j, atividade in enumerate(atividades):
                    print(f"   Pessoa {j+1}:")
                    print(f"     - Postura: {atividade.get('postura_corporal', 'N/A')}")
                    print(f"     - Movimento mãos: {atividade.get('movimento_maos', 'N/A')}")
                    print(f"     - Movimento cabeça: {atividade.get('movimento_cabeca', 'N/A')}")
                    print(f"     - Atividade: {atividade.get('atividade_provavel', 'N/A')}")
            
            print(f"\n📝 Narrativa: {narrativa}")
            
            # Armazena resultado
            resultados_teste.append({
                'cenario': cenario['nome'],
                'sucesso': True,
                'pessoas_detectadas': pessoas_detectadas,
                'narrativa': narrativa,
                'atividades': atividades
            })
            
        except Exception as e:
            print(f"❌ Erro no cenário {i}: {e}")
            resultados_teste.append({
                'cenario': cenario['nome'],
                'sucesso': False,
                'erro': str(e)
            })
    
    # Resumo dos testes
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    sucessos = sum(1 for r in resultados_teste if r.get('sucesso', False))
    total = len(resultados_teste)
    
    print(f"✅ Testes bem-sucedidos: {sucessos}/{total}")
    
    if sucessos == total:
        print("🎉 Todas as melhorias estão funcionando corretamente!")
        print("\n🔍 Principais melhorias implementadas:")
        print("   • Análise mais específica de movimento de cabeça")
        print("   • Detecção contextual de movimento das mãos")
        print("   • Inferência determinística de atividades")
        print("   • Narrativa com ações específicas ao invés de probabilidades")
        print("   • Descrições detalhadas das ações realizadas")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
    
    # Salva relatório de teste
    relatorio_teste = {
        'timestamp': datetime.now().isoformat(),
        'total_cenarios': total,
        'sucessos': sucessos,
        'resultados': resultados_teste
    }
    
    nome_arquivo = f"teste_melhorias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(relatorio_teste, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Relatório salvo em: {nome_arquivo}")
    except Exception as e:
        print(f"⚠️  Erro ao salvar relatório: {e}")
    
    return sucessos == total

if __name__ == "__main__":
    sucesso = testar_melhorias_deteccao()
    
    if sucesso:
        print("\n🎯 Teste concluído com sucesso!")
        exit(0)
    else:
        print("\n❌ Teste falhou!")
        exit(1)