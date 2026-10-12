import re
from urllib.parse import quote, urlparse, parse_qs

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
st.write("Find music, play a supported link, or choose calming sounds for a quiet moment.")
st.caption("Playback is provided by YouTube's embedded player. Availability and playback controls depend on the video's owner, region, and browser.")

tab_search, tab_link, tab_relax = st.tabs(["🔎 Search songs", "▶️ Play a link", "🌿 Relaxation sounds"])

with tab_search:
    st.subheader("Search by song or artist")
    with st.form("mindheal_music_search"):
        query = st.text_input("Song, artist, or music style", placeholder="e.g. relaxing piano, Atif Aslam, lo-fi beats")
        submitted = st.form_submit_button("Search YouTube", type="primary")
    if submitted and query.strip():
        q = quote(query.strip())
        st.markdown(f"[Open YouTube search results for **{query.strip()}**](https://www.youtube.com/results?search_query={q})")
        st.info("Choose a video on YouTube, copy its URL, then paste it in the **Play a link** tab to play it here.")
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

with tab_link:
    st.subheader("Play a YouTube link")
    url = st.text_input("Paste a YouTube video URL", placeholder="https://www.youtube.com/watch?v=...")
    if st.button("Load player", type="primary", key="mindheal_load_music"):
        raw = url.strip()
        parsed = urlparse(raw)
        host = (parsed.hostname or "").lower()
        video_id = ""
        if host in {"youtu.be", "www.youtu.be"}:
            video_id = parsed.path.strip("/").split("/")[0]
        elif host.endswith("youtube.com") or host.endswith("youtube-nocookie.com"):
            if parsed.path == "/watch":
                video_id = parse_qs(parsed.query).get("v", [""])[0]
            else:
                match = re.match(r"^/(embed|shorts|live)/([A-Za-z0-9_-]{6,})", parsed.path)
                if match:
                    video_id = match.group(2)
        if video_id and re.fullmatch(r"[A-Za-z0-9_-]{6,}", video_id):
            st.session_state["mindheal_music_video_id"] = video_id
        else:
            st.error("Please enter a valid YouTube video, Shorts, or youtu.be link.")
    video_id = st.session_state.get("mindheal_music_video_id")
    if video_id:
        st.video("https://www.youtube.com/watch?v=" + video_id)
        st.caption("Use the player's own controls to play, pause, and adjust volume. Some videos may block embedding.")
    st.markdown('<p class="music-note">Only public video links are supported here. This does not download or bypass restrictions on music.</p>', unsafe_allow_html=True)

with tab_relax:
    st.subheader("Relaxation sounds")
    st.write("Pick a soundscape to find suitable public videos, then load your chosen video in the player.")
    sounds = [
        ("Rain on a window", "rain sounds on window 1 hour"),
        ("Ocean waves", "ocean waves relaxing sounds"),
        ("Forest birds", "forest birds nature sounds"),
        ("Gentle piano", "gentle piano meditation music"),
        ("Meditation", "guided meditation relaxation music"),
        ("Sleep ambience", "sleep ambience dark screen relaxing sounds"),
    ]
    cols = st.columns(2)
    for i, (label, q) in enumerate(sounds):
        with cols[i % 2]:
            st.markdown('<div class="music-card"><strong>🌿 ' + label + '</strong><br><span class="music-note">Search public sound videos</span></div>', unsafe_allow_html=True)
            st.link_button("Find " + label, "https://www.youtube.com/results?search_query=" + quote(q), use_container_width=True)

st.divider()
st.caption("MindHeal AI • Music can complement wellbeing practices, but it is not a substitute for professional care.")
