"""Shared registration for MindHeal AI's browser voice component."""
from pathlib import Path

import streamlit.components.v1 as components

_COMPONENT_DIR = Path(__file__).resolve().parents[1] / "voice_component"

try:
    if not (_COMPONENT_DIR / "index.html").is_file():
        raise FileNotFoundError(f"Voice component index.html not found in {_COMPONENT_DIR}")
    VOICE_COMPONENT = components.declare_component(
        "mindheal_browser_voice",
        path=str(_COMPONENT_DIR),
    )
    VOICE_COMPONENT_READY = True
    VOICE_COMPONENT_ERROR = ""
except Exception as exc:
    VOICE_COMPONENT = None
    VOICE_COMPONENT_READY = False
    VOICE_COMPONENT_ERROR = f"{type(exc).__name__}: {exc}"
