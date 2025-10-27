#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples de detecção de pessoas
"""

from detector_avancado import DetectorAvancado
import cv2
import numpy as np

def main():
    print("=== TESTE SIMPLES DE DETECÇÃO ===")
    
    # Inicializa detector
    detector = DetectorAvancado()
    
    # Cria uma imagem de teste simples
    imagem_teste = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Adiciona alguns elementos visuais para simular uma cena
    cv2.rectangle(imagem_teste, (100, 100), (200, 300), (255, 255, 255), -1)  # Retângulo branco
    cv2.rectangle(imagem_teste, (300, 150), (400, 350), (128, 128, 128), -1)  # Retângulo cinza
    cv2.circle(imagem_teste, (500, 200), 50, (255, 0, 0), -1)  # Círculo azul
    
    # Salva imagem temporária
    cv2.imwrite("teste_temp.jpg", imagem_teste)
    
    # Testa detecção
    resultado = detector.detectar_objetos_pessoas("teste_temp.jpg")
    
    # Mostra resultados
    print(f"Pessoas detectadas: {resultado['resumo']['total_pessoas']}")
    print(f"Objetos detectados: {resultado['resumo']['total_objetos']}")
    
    if resultado['deteccoes']['pessoas']:
        print("\nDetalhes das pessoas:")
        for i, pessoa in enumerate(resultado['deteccoes']['pessoas'], 1):
            print(f"  Pessoa {i}: ID={pessoa['id']}, Confiança={pessoa['confianca']:.2f}")
            pos = pessoa['posicao']
            print(f"    Posição: x={pos['x']}, y={pos['y']}, w={pos['largura']}, h={pos['altura']}")
    
    if resultado['deteccoes']['objetos']:
        print("\nDetalhes dos objetos:")
        for i, obj in enumerate(resultado['deteccoes']['objetos'], 1):
            print(f"  Objeto {i}: ID={obj['id']}, Tipo={obj['tipo']}, Confiança={obj['confianca']:.2f}")
    
    print(f"\nNarrativa: {resultado.get('narrativa', 'Não disponível')}")
    
    # Remove arquivo temporário
    import os
    if os.path.exists("teste_temp.jpg"):
        os.remove("teste_temp.jpg")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main()