# Assistente de Voz IA com Llama

Um assistente inteligente de voz que utiliza reconhecimento de fala, processamento de linguagem natural e síntese de voz para criar uma experiência conversacional fluida.

### Importante:
Este projeto foi idealizado e otimizado para rodar em um Jetson Nano 2019. Se você deseja utilizar em outros dispositivos ou trocar os modelos de IA, você precisará apenas:

    Modificar os arquivos .sh (download_piper.sh(configurado para arm64) e download_vosk_model.sh(Carrega o modelo pt-br pequeno)) para baixar modelos compatíveis com seu hardware
    Colocar o modelo Llama (.gguf) no caminho: ./llama/

O restante do código continuará funcionando normalmente.

----------

## Requisitos

- Python 3.8+
- Microfone para captura de áudio
- Speakers/Headphones para reprodução de áudio
- ffplay para reprodução de áudio (ffmpeg)

## Setup
1. Clonar o repositório

```bash

git clone https://github.com/Heitor-Guerra/assistente-ia-jetson
cd assistente-ia-jetson
```

2. Executar os scripts de setup

```bash
# Configura o modelo de reconhecimento de voz (Vosk)
bash download_vosk_model.sh

# Configura o modelo de síntese de voz (Piper)
bash download_piper.sh
```

3. Instalar dependências Python

```bash

pip install -r requirements.txt
```

4. Executar o assistente

```bash
python main.py
```

## Estrutura do Projeto

    .
    ├── main.py                 # Arquivo principal do assistente
    ├── SpeechRecognition.py   # Módulo de reconhecimento de voz
    ├── TextToSpeech.py        # Módulo de síntese de voz
    ├── LlamaCpp.py            # Módulo do LLM (Llama)
    ├── setup_vosk.sh          # Script para configurar Vosk
    ├── setup_piper.sh         # Script para configurar Piper│
    ├── llama/
    │   └── model.gguf         # Modelo Llama (você deve adicionar)
    │
    ├── speechRecognition/
    │   └── model/            # Modelo Vosk (criado por download_vosk_model.sh)
    │
    └── piper/
        ├── piper            # Binário Piper (criado por download_piper.sh)
        └── *.onnx*          # Modelos de voz (criado por download_piper.sh)

## Como Usar

Ao executar python main.py, você terá dois modos de interação:

Escolha como quer perguntar:
    [1] - Voz (usa microfone)
    [2] - Texto (digita na linha de comando)

Modo Voz

    O assistente calibra o microfone automaticamente
    Fale sua pergunta normalmente
    A resposta será sintetizada e reproduzida

Modo Texto

    Digite sua pergunta diretamente
    A resposta será sintetizada e reproduzida

Para sair, digite: sair, exit ou quit

## Customização
- Trocar o Modelo Llama

    Baixe um modelo GGUF compatível (recomendado: modelos quantizados de 1B)
    Coloque na pasta llama/ com extensão .gguf
    Execute main.py normalmente


- Trocar o Modelo de Reconhecimento de Voz

    Edite download_vosk_model.sh com a URL do modelo desejado
    Execute bash download_vosk_model.sh
    O script reorganizará automaticamente


- Trocar o Modelo de Síntese de Voz

    Edite download_piper.sh com a URL do modelo desejado
    Execute bash download_piper.sh
    Altere piper_model em TextToSpeech.py para o novo nome do modelo


- Modificar o Prompt do Sistema
Edite a variável system_prompt em main.py:

🐛 Solução de Problemas
Erro: "Piper binary not found"

    Certifique-se de ter executado bash setup_piper.sh
    Verifique se a pasta piper/ existe

Erro: "Modelo Vosk não encontrado"

    Execute bash setup_vosk.sh novamente
    Verifique a pasta speechRecognition/model/

Áudio não está sendo reproduzido

    Verifique se ffplay está instalado: `ffplay -version
    No Ubuntu/Debian: sudo apt install ffmpeg

Modelo Llama não carrega

    Coloque o arquivo .gguf em model/llama/
    Certifique-se de que é um arquivo GGUF válido
    Verifique a RAM disponível (modelos requerem memória)

Microfone não está funcionando

    Teste seu microfone: arecord -d 3 test.wav
    Verifique as permissões: sudo usermod -a -G audio $USER
