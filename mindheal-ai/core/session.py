import streamlit as st
def init_session():
    st.session_state.setdefault("messages",[])
    st.session_state.setdefault("language","English")
    st.session_state.setdefault("tone","Warm and practical")

# Register the browser voice component from an importable module. This avoids
# Streamlit's "module is None" error when declaration happens in a page script.
try:
    from pathlib import Path
    import streamlit.components.v1 as components

    _VOICE_COMPONENT_DIR = Path(__file__).resolve().parents[1] / "voice_component"
    if not (_VOICE_COMPONENT_DIR / "index.html").is_file():
        raise FileNotFoundError(f"Voice component index.html not found: {_VOICE_COMPONENT_DIR}")
    VOICE_COMPONENT = components.declare_component(
        "mindheal_browser_voice",
        path=str(_VOICE_COMPONENT_DIR),
    )
    VOICE_COMPONENT_READY = True
    VOICE_COMPONENT_ERROR = ""
except Exception as exc:
    VOICE_COMPONENT = None
    VOICE_COMPONENT_READY = False
    VOICE_COMPONENT_ERROR = f"{type(exc).__name__}: {exc}"
