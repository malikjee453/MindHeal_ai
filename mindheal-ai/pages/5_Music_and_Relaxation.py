import ipaddress
import socket
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote, urlparse

import imageio_ffmpeg
import requests
import streamlit as st

st.set_page_config(page_title="Music & Relaxation | MindHeal AI", page_icon="🎵", layout="wide")

MAX_VIDEO_BYTES = 40 * 1024 * 1024
TIMEOUT = (5, 20)
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime", "application/octet-stream"}

st.markdown("""
<style>
h1,h2,h3 { color:#173B2D !important; }
.music-card { padding:1rem 1.1rem; border:1px solid #dce8df; border-radius:14px; background:#f5f9f6; margin:.35rem 0 1rem; }
.music-note { color:#5c7064; font-size:.92rem; }
</style>
""", unsafe_allow_html=True)

st.title("🎵 Music & Relaxation")
st.write("Search for music, play audio, or convert a video file you own or are authorized to use into MP3.")
st.caption("YouTube watch links are not direct video files and are not downloaded or converted here.")

tab_search, tab_convert, tab_relax = st.tabs(["🔎 Find music", "🎧 Convert video to MP3", "🌿 Relaxation sounds"])

def validate_public_url(raw_url):
    parsed = urlparse(raw_url.strip())
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use a public HTTPS direct video-file URL (not a YouTube watch page).")
    host = parsed.hostname.lower()
    if host in {"localhost"} or host.endswith((".localhost", ".local")):
        raise ValueError("Local and private-network addresses are not allowed.")
    try:
        addresses = socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("The video host could not be resolved.") from exc
    if not addresses:
        raise ValueError("The video host could not be resolved.")
    for addr in addresses:
        ip = ipaddress.ip_address(addr[4][0])
        if not ip.is_global:
            raise ValueError("Only publicly reachable video hosts are allowed.")
    return parsed

with tab_search:
    st.subheader("Find a song")
    with st.form("mindheal_music_search"):
        query = st.text_input("Song, artist, or music style", placeholder="e.g. relaxing piano, Atif Aslam, lo-fi beats")
        submitted = st.form_submit_button("Search YouTube", type="primary")
    if submitted and query.strip():
        st.link_button("Open song search results", "https://www.youtube.com/results?search_query=" + quote(query.strip()), use_container_width=True)
        st.info("For audio playback here, use a direct audio URL or convert an authorized video file in the next tab. YouTube watch links are not converted.")
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

with tab_convert:
    st.subheader("Convert an authorized direct video URL")
    st.write("Use a direct MP4/WebM/MOV file URL you own or have permission to convert. YouTube watch links are not supported.")
    video_url = st.text_input("Direct HTTPS video-file URL", placeholder="https://your-site.example/video.mp4")
    if st.button("Convert URL to MP3", type="primary", key="mindheal_convert_url"):
        try:
            parsed = validate_public_url(video_url)
            with st.spinner("Checking and downloading the video…"):
                # Do not follow redirects: prevents redirect-based access to private services.
                with requests.get(video_url.strip(), stream=True, timeout=TIMEOUT, allow_redirects=False, headers={"User-Agent": "MindHealAI-MediaConverter/1.0"}) as response:
                    if response.is_redirect:
                        raise ValueError("Redirecting URLs are not accepted. Use the final public HTTPS file URL.")
                    response.raise_for_status()
                    content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
                    length = response.headers.get("Content-Length")
                    if length and int(length) > MAX_VIDEO_BYTES:
                        raise ValueError("Video exceeds the 40 MB limit.")
                    if content_type and content_type not in ALLOWED_VIDEO_TYPES:
                        raise ValueError("The URL does not appear to point directly to a supported video file.")
                    with tempfile.TemporaryDirectory() as temp_dir:
                        input_path = Path(temp_dir) / "input_video"
                        output_path = Path(temp_dir) / "converted_audio.mp3"
                        total = 0
                        with input_path.open("wb") as out:
                            for chunk in response.iter_content(chunk_size=64 * 1024):
                                if not chunk:
                                    continue
                                total += len(chunk)
                                if total > MAX_VIDEO_BYTES:
                                    raise ValueError("Video exceeds the 40 MB download limit.")
                                out.write(chunk)
                        if total == 0:
                            raise ValueError("The downloaded file was empty.")
                        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
                        command = [
                            ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error",
                            "-y", "-i", str(input_path), "-vn", "-map", "0:a:0?",
                            "-codec:a", "libmp3lame", "-b:a", "128k",
                            "-t", "600", str(output_path),
                        ]
                        proc = subprocess.run(command, capture_output=True, text=True, timeout=90, check=False)
                        if proc.returncode != 0 or not output_path.exists() or output_path.stat().st_size == 0:
                            raise ValueError("Could not extract an audio track. Check that the URL points to a supported video containing audio.")
                        audio_bytes = output_path.read_bytes()
            st.session_state["mindheal_converted_mp3"] = audio_bytes
            st.success("MP3 conversion complete.")
        except (ValueError, requests.RequestException, subprocess.TimeoutExpired, OSError) as exc:
            st.error(str(exc) or "The video could not be converted.")
    mp3 = st.session_state.get("mindheal_converted_mp3")
    if mp3:
        st.audio(mp3, format="audio/mpeg")
        st.download_button("Download converted MP3", data=mp3, file_name="mindheal_audio.mp3", mime="audio/mpeg")
    st.caption("Safety limits: HTTPS only, public hosts only, no redirects, maximum 40 MB input and 10 minutes of converted audio. Some hosts block server downloads. Convert only media you own or are authorized to use.")

with tab_relax:
    st.subheader("Relaxation sounds")
    st.write("Find public audio sources, then paste a direct audio-file URL into the player below.")
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
st.subheader("Play a direct audio URL")
audio_url = st.text_input("MP3 / audio stream URL", placeholder="https://example.com/audio/song.mp3")
if st.button("Load audio", key="mindheal_load_audio"):
    parsed_audio = urlparse(audio_url.strip())
    if parsed_audio.scheme in {"https", "http"} and parsed_audio.netloc:
        st.session_state["mindheal_audio_url"] = audio_url.strip()
    else:
        st.error("Enter a valid audio URL.")
if st.session_state.get("mindheal_audio_url"):
    st.audio(st.session_state["mindheal_audio_url"])
st.caption("MindHeal AI • Music can complement wellbeing practices, but it is not a substitute for professional care.")
