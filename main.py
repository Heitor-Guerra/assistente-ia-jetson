from SpeechRecognition import SpeechRecognition
from TextToSpeech import TextToSpeech
from LlamaCpp import LlamaCpp
import os

def main():
    system_prompt="Você é um assistente que responde de forma curta, clara e concisa. Não seja verboso. Em temas médicos, não invente informações"
    sr = SpeechRecognition()
    tts = TextToSpeech()
    llm = LlamaCpp("/home/Heitor-Guerra/.cache/huggingface/hub/models--ggml-org--gemma-3-1b-it-GGUF/snapshots/f9c28bcd85737ffc5aef028638d3341d49869c27/gemma-3-1b-it-Q4_K_M.gguf", system_prompt=system_prompt)

    run(sr, tts, llm)

def run(sr: SpeechRecognition, tts: TextToSpeech, llm: LlamaCpp):
    """Loop principal do assistente."""

    sr.calibrate()
    tts.start()

    os.system("clear")

    try:
        while True:
            # Captura entrada de voz
            print("Você: ", end="", flush=True)
            user_input = sr.listen()

            if user_input is None or not user_input.strip():
                continue

            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("\nAté mais!")
                break

            # Obtém resposta do LLM e toca áudio
            print("IA: ", end="", flush=True)
            # llm.stream_response(user_input, tts)
            llm.stream_llm_response(user_input, tts)

            tts.wait_until_idle()

    except KeyboardInterrupt:
        print("\n\nAté mais.")
    finally:
        sr.close()
        tts.stop()

if __name__ == "__main__":
    main()
