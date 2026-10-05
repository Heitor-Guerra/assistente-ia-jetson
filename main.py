import requests
import subprocess
import tempfile
import os
import json
import re
import threading
from queue import Queue


def strip_markdown(text):
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # [link](url)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)  # # Headers
    text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)  # - Bullets
    text = text.replace('`', '')
    text = text.replace('*', '')
    text = text.replace('#', '')
    return text


def audio_player_thread(audio_queue):
    while True:
        item = audio_queue.get()
        if item is None:  # Sentinel value to exit
            break

        text, model_name = item
        wav_file = synthesize_with_piper(text, model_name)
        if wav_file:
            play_audio_files([wav_file])
            try:
                os.remove(wav_file)
            except:
                pass
        audio_queue.task_done()

def chat_with_audio(prompt, system_prompt="Responda de forma clara e objetiva.", model_name="pt_BR-faber-medium"):
    llama_url = "http://localhost:9001/completion"

    # Prepare request to llama-cpp
    payload = {
        "prompt": prompt,
        "stream": True,
        "system_prompt": system_prompt,
        "max_tokens": 200,
    }

    print("AI: ", end="", flush=True)

    # Create audio queue and background player thread
    audio_queue = Queue()
    player = threading.Thread(target=audio_player_thread, args=(audio_queue,), daemon=False)
    player.start()

    # Buffer to accumulate text before sending to Piper
    text_buffer = ""

    try:
        # Stream from llama-cpp
        response = requests.post(llama_url, json=payload, stream=True, timeout=30)
        response.raise_for_status()

        # Process streaming chunks
        for line in response.iter_lines():
            if line:
                try:
                    # Remove the "data: " prefix (SSE format)
                    if isinstance(line, bytes):
                        line = line.decode('utf-8')

                    if line.startswith("data: "):
                        line = line[6:]

                    chunk = json.loads(line)
                    text = chunk.get("content", "")

                    if text:
                        print(text, end="", flush=True)
                        text_buffer += text

                        # Send to Piper when we have a complete sentence or reach buffer size
                        if any(text.endswith(punct) for punct in ['.', '!', '?']) or len(text_buffer) > 200:
                            # Clean markdown before synthesis
                            clean_text = strip_markdown(text_buffer).strip()
                            if clean_text:
                                audio_queue.put((clean_text, model_name))
                            text_buffer = ""

                except json.JSONDecodeError:
                    continue

        # Process any remaining text
        if text_buffer.strip():
            clean_text = strip_markdown(text_buffer).strip()
            if clean_text:
                audio_queue.put((clean_text, model_name))

        print("\n")

    except requests.exceptions.ConnectionError:
        print("\nErro: não foi possível conectar.")
    except Exception as e:
        print(f"\nErro: {e}")
    finally:
        # Signal the audio player thread to exit and wait for it
        audio_queue.put(None)
        player.join(timeout=5)


def synthesize_with_piper(text, model_name):
    if not text.strip():
        return None

    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_wav.close()

    try:
        process = subprocess.Popen(
            [
                "./piper/piper",
                "--model", f"./piper/{model_name}.onnx",
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
        print("\nError: Piper binary not found")
        return None
    except Exception as e:
        return None


def play_audio_files(file_paths):
    for filepath in file_paths:
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=60
        )


if __name__ == "__main__":
    sys_prompt = "Você é um assistente que responde de forma curta, clara e concisa. Não seja Verboso. Em temas médicos, não invente informações"

    while True:
        try:
            user_input = input("Você: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['sair']:
                print("Até mais!")
                break

            chat_with_audio(user_input, system_prompt=sys_prompt)
            print("-" * 40 + "\n")

        except KeyboardInterrupt:
            print("\n\nAté mais!")
            break
