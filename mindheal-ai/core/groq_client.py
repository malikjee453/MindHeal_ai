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
    return Groq(api_key=api_key, timeout=30.0, max_retries=1)


def chat(messages, temperature=0.7, **kwargs):
    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        **kwargs,
    )

    return response.choices[0].message.content


def transcribe_audio(audio_bytes, filename="voice_input.wav"):
    """Transcribe a short voice recording with Groq Whisper."""
    client = _get_client()
    response = client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model="whisper-large-v3",
        response_format="json",
    )
    return (getattr(response, "text", "") or "").strip()

