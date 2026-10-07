import speech_recognition as sr
import json
import vosk
import os

class SpeechRecognition:
    """Gerencia captura de áudio e transcrição usando Vosk."""

    def __init__(self, model_path="./speechRecognition/model"):
        vosk.SetLogLevel(-1)
        self.reconhecedor = sr.Recognizer()
        self.reconhecedor.pause_threshold = 1.0
        self.model_path = model_path

    def calibrate(self, duration=2):
        """Calibra o microfone."""

        with sr.Microphone() as fonte:
            os.system("clear")
            print(f"Calibrando o microfone, fique em silêncio por {duration} segundos.")
            self.reconhecedor.adjust_for_ambient_noise(
                fonte,
                duration=2
            )
        print("Calibração concluída.\n")


    def listen(self):
        """Captura áudio do microfone e retorna texto transcrito."""
        try:
          with sr.Microphone() as fonte:
            os.system("clear")
            texto = ""
            print("Você: ", end="", flush=True)
            while texto.strip():
              audio = self.reconhecedor.listen(fonte)

              resultado_bruto = self.reconhecedor.recognize_vosk(audio, self.model_path)

              texto = json.loads(resultado_bruto).get("text", "").strip()

              if texto:
                print(texto)

            return texto
        except Exception as e:
            print(f"\nErro na reconhecimento: {e}\n")
            return None
