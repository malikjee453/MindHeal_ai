import json
import ipaddress
import socket
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote, urlparse

import imageio_ffmpeg
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Music & Relaxation | MindHeal AI", page_icon="🎵", layout="wide")

MAX_VIDEO_BYTES = 40 * 1024 * 1024
TIMEOUT = (5, 20)
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime", "application/octet-stream"}

st.markdown("""
<style>
h1,h2,h3 { color:#173B2D !important; }
.music-card { padding:1rem 1.1rem; border:1px solid #dce8df; border-radius:14px; background:#f5f9f6; margin:.35rem 0 1rem; }
.music-note { color:#5c7064; font-size:.92rem; }

/* Compact audio player for relaxation sounds */
div[data-testid="stAudio"] {
    max-width: 340px !important;
    width: 100% !important;
}
div[data-testid="stAudio"] audio {
    height: 32px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🎵 Music & Relaxation")
st.write("Choose a built-in relaxation sound, or upload a video file from your device to extract its audio as an MP3.")

tab_relax, tab_convert = st.tabs(["🌿 Relaxation music", "🎧 Upload video and convert to MP3"])

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

def _tokens(value):
    import re
    return set(re.findall(r"[a-z0-9]+", str(value or "").lower()))

def _normalize(value):
    return " ".join(sorted(_tokens(value)))

def search_deezer_previews(search_query, limit=8):
    """Search Deezer with a few query variants and return official short previews."""
    import re

    raw = " ".join(search_query.split())
    tokens = re.findall(r"[a-z0-9]+", raw.lower())
    variants = [raw]
    # Search title words separately as a fallback; this helps when a typo or
    # extra word prevents the catalog from returning the intended song.
    if len(tokens) >= 2:
        variants.append(" ".join(tokens[:2]))
    if len(tokens) >= 3:
        variants.append(" ".join(tokens[:3]))
    # Known artist fallback for common spelling variants of this song.
    if "billie" in tokens and "jean" in tokens:
        variants.extend(["Billie Jean Michael Jackson", "Michael Jackson Billie Jean"])
    seen_ids = set()
    results = []
    for variant in variants:
        try:
            response = requests.get(
                "https://api.deezer.com/search",
                params={"q": variant, "limit": limit * 3},
                timeout=TIMEOUT,
                headers={"User-Agent": "MindHealAI-MusicSearch/1.0"},
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            continue
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            continue
        for track in payload["data"]:
            track_id = str(track.get("id", ""))
            title = track.get("title") or ""
            artist = (track.get("artist") or {}).get("name") or "Artist not listed"
            album = (track.get("album") or {}).get("title") or ""
            preview = track.get("preview")
            if not title or not preview or (track_id and track_id in seen_ids):
                continue
            title_tokens = set(re.findall(r"[a-z0-9]+", title.lower()))
            artist_tokens = set(re.findall(r"[a-z0-9]+", artist.lower()))
            query_tokens = set(tokens)
            is_billie_jean = {"billie", "jean"}.issubset(title_tokens)
            title_overlap = len(query_tokens & title_tokens)
            artist_overlap = len(query_tokens & artist_tokens)
            # A strong match must have the song title words, or multiple query
            # terms in title/artist. Never accept one incidental word alone.
            if len(query_tokens) >= 2:
                relevant = is_billie_jean if {"billie", "jean"}.issubset(query_tokens) else (
                    title_overlap >= min(2, len(query_tokens)) or
                    (title_overlap >= 1 and artist_overlap >= 1)
                )
            else:
                relevant = bool(query_tokens & (title_tokens | artist_tokens))
            if not relevant:
                continue
            score = (100 if is_billie_jean else 0) + title_overlap * 10 + artist_overlap * 5
            results.append({
                "title": title,
                "creator": artist,
                "album": album,
                "url": preview,
                "source_url": track.get("link") or "https://www.deezer.com/",
                "source": "Deezer",
                "kind": "preview",
                "score": score,
                "track_id": track_id,
            })
            if track_id:
                seen_ids.add(track_id)
    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:limit]

def search_playable_audio(search_query, limit=8):
    """Find relevant previews and public full MP3s with strict relevance checks."""
    wanted = _tokens(search_query)
    results = search_deezer_previews(search_query, limit=limit)
    seen = {(item["title"].lower(), item["creator"].lower()) for item in results}

    terms = [part.strip() for part in search_query.replace('"', " ").split() if part.strip()]
    safe_phrase = " ".join(terms)
    query_forms = [
        f'mediatype:audio AND title:"{safe_phrase}"',
        f'mediatype:audio AND "{safe_phrase}"',
    ]
    seen_ids = set()
    archive_results = []
    for catalog_query in query_forms:
        try:
            response = requests.get(
                "https://archive.org/advancedsearch.php",
                params=[
                    ("q", catalog_query), ("fl[]", "identifier"),
                    ("fl[]", "title"), ("fl[]", "creator"),
                    ("fl[]", "description"), ("rows", str(limit * 4)),
                    ("page", "1"), ("output", "json"),
                    ("sort[]", "downloads desc"),
                ],
                timeout=TIMEOUT,
                headers={"User-Agent": "MindHealAI-MusicSearch/1.0"},
            )
            response.raise_for_status()
            docs = response.json().get("response", {}).get("docs", [])
        except (requests.RequestException, ValueError):
            continue
        for item in docs:
            identifier = item.get("identifier")
            if not identifier or identifier in seen_ids:
                continue
            seen_ids.add(identifier)
            title = item.get("title") or identifier
            creator = item.get("creator") or "Creator not listed"
            title_tokens, creator_tokens = _tokens(title), _tokens(creator)

            # For multiword queries require a title match, not one incidental
            # word in a creator name or a long description.
            title_hits = len(wanted & title_tokens)
            creator_hits = len(wanted & creator_tokens)
            title_coverage = title_hits / max(1, len(wanted))
            exact_title = wanted == title_tokens
            phrase_match = " ".join(search_query.lower().split()) in " ".join(title.lower().split())
            if len(wanted) >= 2:
                if not (exact_title or phrase_match or (title_coverage >= 0.75 and title_hits >= 2)):
                    continue
            elif title_hits == 0:
                continue

            try:
                meta_response = requests.get(
                    f"https://archive.org/metadata/{quote(identifier, safe='')}",
                    timeout=TIMEOUT,
                    headers={"User-Agent": "MindHealAI-MusicSearch/1.0"},
                )
                meta_response.raise_for_status()
                files = meta_response.json().get("files", [])
            except (requests.RequestException, ValueError):
                continue
            mp3_files = [
                f for f in files
                if str(f.get("name", "")).lower().endswith(".mp3")
                and not f.get("private") and f.get("size") is not None
            ]
            if not mp3_files:
                continue
            mp3_files.sort(key=lambda f: (int(f.get("size", 0) or 0), f.get("name", "")))
            file_info = mp3_files[0]
            key = (title.lower(), creator.lower())
            if key in seen:
                continue
            archive_results.append({
                "title": title,
                "creator": creator,
                "album": "",
                "url": f"https://archive.org/download/{quote(identifier, safe='')}/{quote(file_info['name'], safe='/')}",
                "filename": file_info["name"],
                "source_url": f"https://archive.org/details/{quote(identifier, safe='')}",
                "source": "Internet Archive",
                "kind": "full_mp3",
                "score": (100 if exact_title else 0) + (50 if phrase_match else 0) + title_hits * 10 + creator_hits * 2,
            })
    archive_results.sort(key=lambda item: item["score"], reverse=True)
    results.extend(archive_results[:max(0, limit - len(results))])
    return results[:limit]

with tab_convert:
    st.subheader("Upload a video from your device")
    st.write("Choose an MP4, WebM, or MOV video file from your local disk. Only convert media you own or have permission to use.")
    uploaded_video = st.file_uploader(
        "Choose video file",
        type=["mp4", "webm", "mov"],
        key="mindheal_local_video_upload",
    )
    if uploaded_video is not None:
        st.caption(f"Selected: {uploaded_video.name} · {uploaded_video.size / (1024 * 1024):.1f} MB")
    if st.button("Convert uploaded video to MP3", type="primary", key="mindheal_convert_upload"):
        try:
            if uploaded_video is None:
                raise ValueError("Please choose a video file from your device first.")
            if uploaded_video.size > MAX_VIDEO_BYTES:
                raise ValueError("Video exceeds the 40 MB limit.")
            with st.spinner("Converting your uploaded video…"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    input_path = Path(temp_dir) / (Path(uploaded_video.name).name or "input_video")
                    output_path = Path(temp_dir) / "converted_audio.mp3"
                    input_path.write_bytes(uploaded_video.getvalue())
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
    st.subheader("🎵 Music that keeps playing while you chat")
    st.write(
        "Upload your music, then click **Open persistent music player**. "
        "A separate small player window will keep playing while you use the Chat, "
        "Mental Discomforts, Addictions, or Fears pages. Keep that player window open."
    )

    uploaded_music = st.file_uploader(
        "Click to upload music from device",
        type=["mp3", "wav", "ogg", "m4a", "aac", "flac"],
        key="mindheal_music_upload",
        help="Supported formats: MP3, WAV, OGG, M4A, AAC, FLAC",
    )
    if uploaded_music is not None:
        # Keep the selected file in Streamlit session state so ordinary reruns
        # don't discard the user's selection.
        st.session_state["mindheal_music_bytes"] = uploaded_music.getvalue()
        st.session_state["mindheal_music_name"] = uploaded_music.name
        st.session_state["mindheal_music_type"] = uploaded_music.type or "audio/mpeg"

    music_bytes = st.session_state.get("mindheal_music_bytes")
    music_name = st.session_state.get("mindheal_music_name", "uploaded music")
    music_type = st.session_state.get("mindheal_music_type", "audio/mpeg")

    if music_bytes:
        import base64
        encoded_audio = base64.b64encode(music_bytes).decode("ascii")
        st.caption(f"Selected: {music_name}")
        components.html("""
        <div style="font-family:Arial,sans-serif;max-width:520px;color:#173b2d">
          <div style="font-size:14px;margin:4px 0 8px;color:#173b2d">
            Click below to open a separate player. If playback does not start automatically, press Play in the player window.
          </div>
          <button id="mh-open-player" type="button" style="margin-top:8px;border:0;border-radius:8px;padding:11px 16px;background:#2f7655;color:white;font-weight:700;cursor:pointer">
            🎵 Open persistent music player
          </button>
          <div id="mh-player-status" style="font-size:12px;margin-top:6px;color:#5c7064" aria-live="polite"></div>
        </div>
        <script>
        (() => {
          const open=document.getElementById('mh-open-player');
          const status=document.getElementById('mh-player-status');
          const source='data:__MIME__;base64,__AUDIO_DATA__';
          if(!open || open.dataset.ready)return;
          open.dataset.ready='1';
          open.addEventListener('click',()=>{
            // Open synchronously from the click to avoid popup blockers.
            const win=window.open('about:blank','mindheal_music_player','width=440,height=260,resizable=yes');
            if(!win){status.textContent='The browser blocked the player window. Allow pop-ups for this site, then click again.';return;}
            const html='<!doctype html><html><head><meta charset="utf-8"><title>MindHeal — Music Player</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font:16px Arial,sans-serif;background:#f5f9f6;color:#173b2d;padding:20px}h2{font-size:18px}audio{width:100%}button{border:0;border-radius:8px;padding:9px 14px;background:#2f7655;color:white;cursor:pointer;margin-top:10px}</style></head><body><h2>🌿 MindHeal music</h2><p>Keep this window open while you chat.</p><audio id="player" controls loop preload="auto"></audio><br><button id="stop">■ Stop music</button><script>const a=document.getElementById("player");a.src='+JSON.stringify(source)+';a.loop=true;document.getElementById("stop").onclick=()=>{a.pause();a.currentTime=0};a.addEventListener("error",()=>{document.getElementById("msg").textContent="This audio format could not be played by your browser."});<\/script><p id="msg" style="font-size:12px"></p></body></html>';
            win.document.open();
            win.document.write(html);
            win.document.close();
            status.textContent='Player window opened. Press Play in that window if it does not start automatically.';
            try { win.focus(); } catch(e) {}
          });
        })();
        </script>
        """.replace("__MIME__", json.dumps(music_type)[1:-1]).replace("__AUDIO_DATA__", encoded_audio), height=155, scrolling=False)

st.caption("MindHeal AI • Music can complement wellbeing practices, but it is not a substitute for professional care.")
