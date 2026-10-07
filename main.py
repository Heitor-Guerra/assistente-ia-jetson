from SpeechRecognition import SpeechRecognition
from TextToSpeech import TextToSpeech
from LlamaCpp import LlamaCpp
import os

def main():
    system_prompt="Você é um assistente que responde de forma curta, clara e concisa. Não seja verboso. Em temas médicos, não invente informações"
    sr = SpeechRecognition()
    tts = TextToSpeech()
    llm = LlamaCpp("./llama/*.gguf", system_prompt=system_prompt)

    run(sr, tts, llm)

def run(sr: SpeechRecognition, tts: TextToSpeech, llm: LlamaCpp):
    """Loop principal do assistente."""

    sr.calibrate()
    tts.start()

    os.system("clear")

    try:
        while True:
            choice = int(input("Escolha como quer perguntar:\n[1] - Voz\n[2] - Texto"))

            if choice == 1:
                # Captura entrada de voz
                user_input = sr.listen()
            else:
                user_input = input("Você: ")

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
            print("-"*60)

    except KeyboardInterrupt:
        print("\n\nAté mais.")
    finally:
        sr.close()
        tts.stop()

if __name__ == "__main__":
    main()
