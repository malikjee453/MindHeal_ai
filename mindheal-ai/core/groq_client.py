import os
from groq import Groq
from core.config import GROQ_MODEL

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def chat(messages, temperature=0.7, **kwargs):
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        **kwargs,
    )

    return response.choices[0].message.content


def transcribe_audio(audio_bytes, filename="voice_input.wav"):
    """Transcribe a short voice recording with Groq Whisper."""
    response = client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model="whisper-large-v3",
        response_format="json",
    )
    return (getattr(response, "text", "") or "").strip()

