import subprocess
import tempfile
import os
import json
import re
import threading
from queue import Queue

class TextToSpeech:
    """Gerencia síntese de voz usando Piper e reprodução de áudio."""

    def __init__(self, piper_model="pt_BR-faber-medium", piper_path="./piper"):
        self.piper_path = piper_path
        self.piper_model = piper_model
        self.audio_queue = Queue()
        self.player_thread = None
        self.running = False

    def _strip_markdown(self, text):
        """Remove formatação Markdown do texto."""
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)
        text = text.replace('`', '').replace('*', '').replace('#', '')
        return text

    def _synthesize_chunk(self, text):
        """Gera arquivo WAV para um fragmento de texto."""
        text = self._strip_markdown(text).strip()
        if not text:
            return None

        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_wav.close()

        try:
            process = subprocess.Popen(
                [
                    f"{self.piper_path}/piper",
                    "--model", f"{self.piper_path}/{self.piper_model}.onnx",
                    "--output-file", temp_wav.name,
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout, stderr = process.communicate(input=text.encode('utf-8'), timeout=30)

            if process.returncode != 0:
                return None

            return temp_wav.name

        except FileNotFoundError:
            print("Error: Piper binary not found")
            return None
        except Exception as e:
            return None

    def _play_file(self, filepath):
        """Reproduz um arquivo de áudio."""
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=60
        )

    def _audio_player_loop(self):
        """Loop executado no thread de reprodução de áudio."""
        while self.running:
            item = self.audio_queue.get()
            if item is None:
                break

            wav_file = item
            if wav_file:
                try:
                    self._play_file(wav_file)
                except Exception as e:
                    print(f"Erro ao reproduzir áudio: {e}")

                try:
                    os.remove(wav_file)
                except:
                    pass

            self.audio_queue.task_done()

    def start(self):
        """Inicia o thread de reprodução de áudio."""
        self.running = True
        self.player_thread = threading.Thread(target=self._audio_player_loop, daemon=True)
        self.player_thread.start()
        print("\nText to Speech iniciado")

    def stop(self):
        """Para o thread de reprodução de áudio."""
        self.running = False
        self.audio_queue.put(None)
        if self.player_thread:
            self.player_thread.join(timeout=5)
        print("\nText to Speech finalizado.")


    def wait_until_idle(self):
        """Waits until all queued audio has finished playing."""
        self.audio_queue.join()

    def synthesize_and_queue(self, text):
        """Gera e enfileira áudio para reprodução assíncrona."""
        text = text.strip()
        if not text:
            return

        wav_file = self._synthesize_chunk(text)
        if wav_file:
            self.audio_queue.put(wav_file)
        else:
            print("Falha ao gerar áudio.")
