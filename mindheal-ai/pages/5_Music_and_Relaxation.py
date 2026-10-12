from urllib.parse import quote, urlparse

import streamlit as st

st.set_page_config(page_title="Music & Relaxation | MindHeal AI", page_icon="🎵", layout="wide")

st.markdown("""
<style>
h1,h2,h3 { color:#173B2D !important; }
.music-card { padding:1rem 1.1rem; border:1px solid #dce8df; border-radius:14px; background:#f5f9f6; margin:.35rem 0 1rem; }
.music-note { color:#5c7064; font-size:.92rem; }
</style>
""", unsafe_allow_html=True)

st.title("🎵 Music & Relaxation")
st.write("A lightweight audio player for music and calming sounds.")
st.caption("For quick loading, this page uses an audio-only player. Provide a direct audio-file URL (such as MP3, WAV, or OGG) from a source that permits playback.")

tab_search, tab_audio, tab_relax = st.tabs(["🔎 Find music", "🎧 MP3 / audio player", "🌿 Relaxation sounds"])

with tab_search:
    st.subheader("Find a song")
    with st.form("mindheal_music_search"):
        query = st.text_input("Song, artist, or music style", placeholder="e.g. Atif Aslam, relaxing piano, lo-fi beats")
        submitted = st.form_submit_button("Search YouTube", type="primary")
    if submitted and query.strip():
        st.link_button("Open song search results", "https://www.youtube.com/results?search_query=" + quote(query.strip()), use_container_width=True)
        st.info("To play audio inside this lightweight player, use a direct MP3/audio-file URL in the next tab. YouTube watch links are video embeds and are not converted to MP3.")
    st.markdown("Popular searches")
    quick = [
        ("Calm piano", "calm relaxing piano music"),
        ("Lo-fi focus", "lofi beats for focus"),
        ("Urdu / Pakistani songs", "Pakistani Urdu songs"),
        ("Nature ambience", "nature ambience relaxing sounds"),
    ]
    cols = st.columns(2)
    for i, (label, q) in enumerate(quick):
        with cols[i % 2]:
            st.link_button(label, "https://www.youtube.com/results?search_query=" + quote(q), use_container_width=True)

with tab_audio:
    st.subheader("Play an MP3 or audio stream")
    audio_url = st.text_input(
        "Direct audio URL",
        placeholder="https://example.com/audio/song.mp3",
        help="Use the direct URL to an audio file or stream, not a normal webpage or YouTube watch link.",
    )
    if st.button("Load audio", type="primary", key="mindheal_load_audio"):
        parsed = urlparse(audio_url.strip())
        if parsed.scheme in {"https", "http"} and parsed.netloc:
            st.session_state["mindheal_audio_url"] = audio_url.strip()
        else:
            st.error("Enter a valid http:// or https:// direct audio URL.")
    saved_url = st.session_state.get("mindheal_audio_url", "")
    if saved_url:
        st.audio(saved_url)
        st.caption("If playback fails, the host may block streaming or require a different direct audio URL.")
    st.caption("Supported formats depend on the browser and source, commonly MP3, WAV, and OGG. The app does not download or convert songs.")

with tab_relax:
    st.subheader("Relaxation sounds")
    st.write("Find rain, ocean, forest, or meditation audio. Use a direct audio URL in the player to keep playback lightweight.")
    sounds = [
        ("Rain on a window", "rain sounds mp3 relaxation"),
        ("Ocean waves", "ocean waves relaxing sounds audio"),
        ("Forest birds", "forest birds nature sounds audio"),
        ("Gentle piano", "gentle piano meditation music"),
        ("Meditation", "guided meditation relaxation audio"),
        ("Sleep ambience", "sleep ambience relaxing audio"),
    ]
    cols = st.columns(2)
    for i, (label, q) in enumerate(sounds):
        with cols[i % 2]:
            st.markdown('<div class="music-card"><strong>🌿 ' + label + '</strong><br><span class="music-note">Find suitable audio sources</span></div>', unsafe_allow_html=True)
            st.link_button("Search " + label, "https://www.google.com/search?q=" + quote(q), use_container_width=True)

st.divider()
st.caption("MindHeal AI • Music can complement wellbeing practices, but it is not a substitute for professional care.")
