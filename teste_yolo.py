#!/usr/bin/env python3
"""
Teste simples do YOLOv8
"""

import os
import sys

def testar_yolo():
    try:
        print("🔧 Testando YOLOv8...")
        
        # Importa YOLO
        from ultralytics import YOLO
        print("✅ Ultralytics importado com sucesso")
        
        # Carrega modelo
        if os.path.exists('yolov8n.pt'):
            print("✅ Arquivo yolov8n.pt encontrado")
            model = YOLO('yolov8n.pt')
            print("✅ Modelo YOLOv8 carregado com sucesso")
            
            # Testa detecção em uma imagem de exemplo
            print("🔍 Testando detecção...")
            
            # Cria uma imagem de teste simples
            import cv2
            import numpy as np
            
            # Imagem de teste (640x480, azul)
            test_img = np.zeros((480, 640, 3), dtype=np.uint8)
            test_img[:] = (255, 0, 0)  # Azul
            
            # Salva imagem de teste
            cv2.imwrite('teste_img.jpg', test_img)
            print("✅ Imagem de teste criada")
            
            # Executa detecção
            results = model('teste_img.jpg')
            print(f"✅ Detecção executada - {len(results)} resultado(s)")
            
            # Verifica resultados
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    print(f"📊 {len(boxes)} detecções encontradas")
                    for i, box in enumerate(boxes):
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        class_name = result.names[class_id]
                        print(f"   - {class_name}: {confidence:.2f}")
                else:
                    print("📊 Nenhuma detecção encontrada (normal para imagem de teste)")
            
            # Remove imagem de teste
            if os.path.exists('teste_img.jpg'):
                os.remove('teste_img.jpg')
            
            print("🎉 YOLOv8 está funcionando corretamente!")
            return True
            
        else:
            print("❌ Arquivo yolov8n.pt não encontrado")
            return False
            
    except ImportError as e:
        print(f"❌ Erro ao importar ultralytics: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    sucesso = testar_yolo()
    sys.exit(0 if sucesso else 1)