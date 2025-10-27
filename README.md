# Sistema de Monitoramento de Tela com OpenCV

Este projeto implementa um sistema completo de monitoramento de tela usando OpenCV e Python, capaz de capturar screenshots periodicamente e gerar relatórios detalhados com análises visuais.

## Funcionalidades

- 📸 **Captura automática de tela** em intervalos configuráveis
- 🔍 **Análise de movimento** com detecção de atividade visual e objetos em movimento
- 📊 **Geração de relatórios** em JSON com estatísticas de movimento e atividade
- 📈 **Gráficos automáticos** mostrando tendências de movimento ao longo do tempo
- 💾 **Armazenamento organizado** das capturas em pasta dedicada

## Instalação

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

Ou instalar manualmente:

```bash
pip install opencv-python numpy pillow matplotlib
```

### 2. Executar o sistema

```bash
python monitor_tela.py
```

## Como usar

1. Execute o script `monitor_tela.py`
2. O sistema irá configurar automaticamente:
   - Duração: 60 segundos (1 minuto)
   - Intervalo: 5 segundos entre capturas
3. Pressione Enter para iniciar o monitoramento
4. O sistema irá:
   - Capturar a tela a cada 5 segundos
   - Salvar as imagens na pasta `capturas/`
   - Processar cada imagem para extrair informações
   - Gerar relatório final em JSON
   - Criar gráficos de análise

## Estrutura dos arquivos gerados

```
projeto/
├── monitor_tela.py          # Script principal
├── requirements.txt         # Dependências
├── capturas/               # Pasta com screenshots
│   ├── captura_20241225_143022.png
│   └── ...
├── relatorio_20241225_143100.json  # Relatório detalhado
    └── graficos/                    # Pasta para gráficos
        └── graficos_20241225_143100.png  # Gráficos de análise de movimento
```

## Relatório gerado

O sistema gera um relatório completo contendo:

### Estatísticas gerais:
- Total de capturas realizadas
- Tempo de início e fim
- Duração total do monitoramento
- Capturas por minuto
- Tamanho médio dos arquivos

### Para cada captura:
- Timestamp exato
- Caminho do arquivo salvo
- Tamanho do arquivo
- Resolução da imagem
- Brilho médio da tela
- Número de bordas detectadas
- Histograma de cores (primeiros 50 valores)

### Gráficos incluídos:
1. **Brilho médio ao longo do tempo** - mostra variações de luminosidade
2. **Atividade visual** - número de bordas detectadas (indica movimento/mudanças)
3. **Tamanho dos arquivos** - variação do tamanho das capturas
4. **Distribuição do brilho** - histograma da luminosidade geral

## Personalização

Você pode modificar as configurações no arquivo `monitor_tela.py`:

```python
# Alterar duração e intervalo
duracao = 120  # 2 minutos
intervalo = 3  # a cada 3 segundos
```

## Requisitos do sistema

- Python 3.7+
- Windows/Linux/macOS
- Acesso à tela (para captura de screenshots)

## Casos de uso

- **Monitoramento de produtividade** - analisar padrões de uso da tela
- **Análise de comportamento visual** - estudar mudanças na interface
- **Documentação automática** - registrar atividades na tela
- **Análise de performance** - detectar travamentos ou problemas visuais
- **Pesquisa UX/UI** - estudar interações com interfaces

## Exemplo de saída

```
=== SISTEMA DE MONITORAMENTO DE TELA ===
Configuração atual:
- Duração: 60 segundos
- Intervalo: 5 segundos
- Total estimado de capturas: 12

Captura 1: 14:30:22
Captura 2: 14:30:27
...
Captura 12: 14:31:17

=== RELATÓRIO GERADO ===
Arquivo: relatorio_20241225_143117.json
Total de capturas: 12
Duração: 60.0 segundos
Capturas por minuto: 12.0
Tamanho médio dos arquivos: 1250.5 KB
```