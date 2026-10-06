import requests
import json
from llama_cpp import Llama

class LlamaCpp:
    """Gerencia comunicação com o servidor llama-cpp."""

    def __init__(self, model_path ,url="http://localhost:9001", system_prompt="Responda de forma clara e objetiva.", max_tokens=200):
        self.url = f"{url}/v1/chat/completions"
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=4,
            verbose=False,
        )

    def stream_response(self, prompt, tts_handler):
        """Stream da resposta do LLM e envia chunks para TTS."""
        payload = {
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": True,
            "max_tokens": self.max_tokens,
        }

        text_buffer = ""
        try:
            response = requests.post(self.url, json=payload, stream=True, timeout=(10, 120))
            response.raise_for_status()

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                # SSE lines usually look like: data: {...}
                if line.startswith("data:"):
                    line = line[len("data:"):].strip()

                # End-of-stream marker
                if line == "[DONE]":
                    break

                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    print(f"\nLinha inválida: {line!r}")
                    continue

                choices = chunk.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})
                text = delta.get("content") or ""

                if not text:
                    continue

                print(text, end="", flush=True)
                text_buffer += text

                if (any(text_buffer.endswith(p) for p in [".", "!", "?"]) or len(text_buffer) >= 200):
                    tts_handler.synthesize_and_queue(text_buffer)
                    text_buffer = ""

            # Processa texto restante
            if text_buffer.strip():
                tts_handler.synthesize_and_queue(text_buffer)

            print("\n")
        except Exception as e:
            print(f"\nErro: {e}")

    def stream_llm_response(self, prompt, tts_handler):
        """
        Stream responses from Llama model and send chunks to TTS handler.
        """

        payload = {
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self.max_tokens,
            "stream": True,
        }

        text_buffer = ""
        full_response = ""

        try:
            # Stream completions directly from model
            response_stream = self.llm.create_chat_completion(**payload)

            for chunk in response_stream:
                # Extract text from chunk dict
                choices = chunk.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})
                text = delta.get("content") or ""

                if not text:
                    continue

                # Print and buffer text
                print(text, end="", flush=True)
                text_buffer += text
                full_response += text

                # Send to TTS when punctuation or buffer size reached
                if (any(text_buffer.endswith(p) for p in [".", "!", "?"])
                    or len(text_buffer) >= 200):
                    tts_handler.synthesize_and_queue(text_buffer)
                    text_buffer = ""

            # Process remaining text
            if text_buffer.strip():
                tts_handler.synthesize_and_queue(text_buffer)

            print("\n")
            return full_response

        except Exception as e:
            print(f"\nErro: {e}")
            return ""
