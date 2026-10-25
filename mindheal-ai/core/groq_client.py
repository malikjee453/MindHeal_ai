import os
from groq import Groq
from core.config import GROQ_MODEL

# Bound request time so a transient provider delay cannot leave the UI spinning forever.
def _get_client():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Add your Groq API key to the environment "
            "or Streamlit secrets, then restart the app."
        )
    # Do not retry slow chat requests automatically: retries can make the UI appear frozen.
    # A single bounded attempt lets the app show its existing friendly error message promptly.
    return Groq(api_key=api_key, timeout=20.0, max_retries=0)


def chat(messages, temperature=0.7, **kwargs):
    client = _get_client()
    model = GROQ_MODEL
    request_options = dict(kwargs)

    # GPT-OSS models use max_completion_tokens and can spend substantial time
    # reasoning before producing visible text. Keep everyday MindHeal replies
    # responsive and return only the user-facing answer.
    if model.startswith("openai/gpt-oss-"):
        if "max_tokens" in request_options:
            request_options["max_completion_tokens"] = request_options.pop("max_tokens")
        request_options.setdefault("reasoning_effort", "low")
        request_options.setdefault("include_reasoning", False)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        **request_options,
    )

    answer = response.choices[0].message.content
    if not answer:
        raise RuntimeError(
            "Groq returned an empty answer. Please try again; if it repeats, check the model "
            "and API status in your Groq console."
        )
    return answer


def transcribe_audio(audio_bytes, filename="voice_input.wav"):
    """Transcribe a short voice recording with Groq Whisper."""
    client = _get_client()
    response = client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model="whisper-large-v3",
        response_format="json",
    )
    return (getattr(response, "text", "") or "").strip()
