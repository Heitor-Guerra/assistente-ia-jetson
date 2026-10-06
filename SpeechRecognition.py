import speech_recognition as sr
import json
import vosk
import os

class SpeechRecognition:
    """Gerencia captura de áudio e transcrição usando Vosk."""

    def __init__(self, model_path="./model"):
        vosk.SetLogLevel(-1)
        self.reconhecedor = sr.Recognizer()
        self.reconhecedor.pause_threshold = 1.0
        self.model_path = model_path
        self.fonte = None

    def calibrate(self, duration=2):
        """Abre o microfone uma única vez."""
        self.fonte = sr.Microphone()
        self.fonte.__enter__()

        print(f"Calibrando o microfone, fique em silêncio por {duration} segundos.")
        self.reconhecedor.adjust_for_ambient_noise(
            self.fonte,
            duration=2
        )
        print("Calibração concluída.\n")


    def close(self):
        """Fecha o microfone."""
        if self.fonte is not None:
            self.fonte.__exit__(None, None, None)
            self.fonte = None

    def listen(self, timeout=100, phrase_time_limit=200):
        """Captura áudio do microfone e retorna texto transcrito."""
        if self.fonte is None:
          return None
        try:
          audio = self.reconhecedor.listen(self.fonte, timeout=timeout, phrase_time_limit=phrase_time_limit)

          resultado_bruto = self.reconhecedor.recognize_vosk(audio, self.model_path)

          texto = json.loads(resultado_bruto).get("text", "").strip()

          if texto:
              print(texto)

          return texto
        except Exception as e:
            print(f"\nErro na reconhecimento: {e}\n")
            return None
