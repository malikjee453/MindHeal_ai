from pathlib import Path
import streamlit.components.v1 as components

_COMPONENT_DIR = Path(__file__).parent / "frontend"
_voice_component = components.declare_component(
    "mindheal_browser_voice",
    path=str(_COMPONENT_DIR),
)


def browser_voice(key: str = "mindheal_browser_voice"):
    """Render browser-native speech recognition and return completed speech text."""
    return _voice_component(key=key, default="",)
