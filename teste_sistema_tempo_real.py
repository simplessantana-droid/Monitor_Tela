import sys
import os
import time
import threading
from datetime import datetime
import json

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from detector_avancado import DetectorAvancado
from gerador_relatorios_automaticos import GeradorRelatoriosAutomaticos

def teste_detector_basico():
    """Testa o detector básico"""
    print("="*50)
    print("TESTE 1: Detector Básico")
    print("="*50)
    
    try:
        detector = DetectorAvancado()
        print("✓ DetectorAvancado inicializado com sucesso")
        
        # Teste com imagem simulada
        import numpy as np
        imagem_teste = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Criar arquivo temporário para teste
        import cv2
        cv2.imwrite("temp_test.jpg", imagem_teste)
        resultado = detector.detectar_objetos_pessoas("temp_test.jpg")
        os.remove("temp_test.jpg")
        print("✓ Detecção de objetos e pessoas executada")
        
        # Verificar estrutura do resultado
        campos_esperados = ['pessoas', 'objetos', 'narrativa', 'timestamp']
        for campo in campos_esperados:
            if campo in resultado:
                print(f"✓ Campo '{campo}' presente no resultado")
            else:
                print(f"✗ Campo '{campo}' ausente no resultado")
                
        print(f"Narrativa gerada: {resultado.get('narrativa', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"✗ Erro no teste do detector: {e}")
        return False

def teste_gerador_relatorios():
    """Testa o gerador de relatórios automáticos"""
    print("\n" + "="*50)
    print("TESTE 2: Gerador de Relatórios Automáticos")
    print("="*50)
    
    try:
        # Criar gerador com intervalos curtos para teste
        gerador = GeradorRelatoriosAutomaticos(intervalo_captura=2, intervalo_relatorio=1)
        print("✓ GeradorRelatoriosAutomaticos inicializado")
        
        # Verificar criação de diretórios
        if os.path.exists("capturas_automaticas"):
            print("✓ Diretório 'capturas_automaticas' criado")
        if os.path.exists("relatorios_automaticos"):
            print("✓ Diretório 'relatorios_automaticos' criado")
            
        # Simular algumas capturas
        import numpy as np
        import cv2
        for i in range(3):
            imagem_teste = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.imwrite("temp_test.jpg", imagem_teste)
            resultado = gerador.detector.detectar_objetos_pessoas("temp_test.jpg")
            os.remove("temp_test.jpg")
            resultado['timestamp'] = datetime.now().isoformat()
            resultado['captura_numero'] = i
            gerador.dados_sessao.append(resultado)
            
        print(f"✓ {len(gerador.dados_sessao)} capturas simuladas adicionadas")
        
        # Testar geração de relatório
        relatorio = gerador.gerar_relatorio_completo()
        if relatorio:
            print("✓ Relatório completo gerado com sucesso")
            
            # Verificar campos do relatório
            campos_relatorio = ['periodo', 'estatisticas_gerais', 'analise_atividades', 'narrativa_consolidada']
            for campo in campos_relatorio:
                if campo in relatorio:
                    print(f"✓ Campo '{campo}' presente no relatório")
                    
        return True
        
    except Exception as e:
        print(f"✗ Erro no teste do gerador: {e}")
        return False

def teste_integracao_completa():
    """Testa a integração completa do sistema"""
    print("\n" + "="*50)
    print("TESTE 3: Integração Completa")
    print("="*50)
    
    try:
        # Inicializar gerador
        gerador = GeradorRelatoriosAutomaticos(intervalo_captura=1, intervalo_relatorio=1)
        
        print("Iniciando monitoramento de teste por 5 segundos...")
        gerador.iniciar_monitoramento_automatico()
        
        # Aguardar algumas capturas
        time.sleep(5)
        
        # Parar monitoramento
        gerador.parar_monitoramento_automatico()
        
        print(f"✓ Monitoramento executado, {len(gerador.dados_sessao)} capturas realizadas")
        
        if gerador.dados_sessao:
            # Testar geração de relatório
            gerador.gerar_relatorio_periodico()
            
            # Verificar se arquivo foi criado
            arquivos_relatorio = [f for f in os.listdir("relatorios_automaticos") if f.startswith("relatorio_automatico_")]
            if arquivos_relatorio:
                print(f"✓ Relatório automático gerado: {arquivos_relatorio[-1]}")
                
                # Verificar conteúdo do relatório
                with open(f"relatorios_automaticos/{arquivos_relatorio[-1]}", 'r', encoding='utf-8') as f:
                    relatorio = json.load(f)
                    
                if 'narrativa_consolidada' in relatorio:
                    print(f"✓ Narrativa consolidada: {relatorio['narrativa_consolidada'][:100]}...")
                    
        return True
        
    except Exception as e:
        print(f"✗ Erro no teste de integração: {e}")
        return False

def teste_narrativa_melhorada():
    """Testa especificamente as melhorias na narrativa"""
    print("\n" + "="*50)
    print("TESTE 4: Narrativa Melhorada")
    print("="*50)
    
    try:
        detector = DetectorAvancado()
        
        # Simular detecção com dados específicos
        import numpy as np
        imagem_teste = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Forçar detecção simulada
        resultado = detector._deteccao_simulada(imagem_teste)
        
        # Gerar narrativa
        narrativa = detector._gerar_narrativa(resultado)
        
        print(f"✓ Narrativa gerada: {narrativa}")
        
        # Testar descrição de ação específica
        if hasattr(detector, '_descrever_acao_especifica'):
            atividades_teste = [
                {'postura_corporal': 'sentado', 'movimento_maos': 'digitando', 'movimento_cabeca': 'olhando_tela', 'atividade_provavel': 'trabalhando_no_computador'},
                {'postura_corporal': 'em_pe', 'movimento_maos': 'gesticulando', 'movimento_cabeca': 'olhando_frente', 'atividade_provavel': 'conversando_ou_apresentando'},
                {'postura_corporal': 'sentado', 'movimento_maos': 'segurando_objeto', 'movimento_cabeca': 'olhando_baixo', 'atividade_provavel': 'lendo_ou_escrevendo'},
                {'postura_corporal': 'em_pe', 'movimento_maos': 'maos_ao_lado', 'movimento_cabeca': 'olhando_direita', 'atividade_provavel': 'observando_ou_aguardando'}
            ]
            
            print("\nTestando descrições específicas:")
            for atividade in atividades_teste:
                descricao = detector._descrever_acao_especifica(atividade)
                print(f"✓ {atividade['atividade_provavel']}: {descricao}")
                
        return True
        
    except Exception as e:
        print(f"✗ Erro no teste de narrativa: {e}")
        return False

def executar_todos_testes():
    """Executa todos os testes do sistema"""
    print("INICIANDO TESTES DO SISTEMA DE MONITORAMENTO EM TEMPO REAL")
    print("=" * 70)
    
    testes = [
        ("Detector Básico", teste_detector_basico),
        ("Gerador de Relatórios", teste_gerador_relatorios),
        ("Integração Completa", teste_integracao_completa),
        ("Narrativa Melhorada", teste_narrativa_melhorada)
    ]
    
    resultados = []
    
    for nome, teste_func in testes:
        try:
            resultado = teste_func()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"✗ Erro crítico no teste '{nome}': {e}")
            resultados.append((nome, False))
    
    # Resumo dos resultados
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "✓ PASSOU" if resultado else "✗ FALHOU"
        print(f"{nome}: {status}")
        if resultado:
            sucessos += 1
    
    print(f"\nResultado geral: {sucessos}/{len(testes)} testes passaram")
    
    if sucessos == len(testes):
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
    
    return sucessos == len(testes)

if __name__ == "__main__":
    # Verificar dependências
    try:
        import schedule
        print("✓ Dependência 'schedule' disponível")
    except ImportError:
        print("⚠️  Dependência 'schedule' não encontrada. Instale com: pip install schedule")
    
    try:
        import pyautogui
        print("✓ Dependência 'pyautogui' disponível")
    except ImportError:
        print("⚠️  Dependência 'pyautogui' não encontrada. Instale com: pip install pyautogui")
    
    # Executar testes
    executar_todos_testes()