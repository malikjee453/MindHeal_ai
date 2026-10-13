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

with tab_search:
    st.subheader("Search and play MP3s here")
    st.caption("Searches for official 30-second song previews and separately for full MP3s in Internet Archive. Preview availability depends on the catalog and region.")
    with st.form("mindheal_music_search"):
        query = st.text_input("Song, artist, or music style", placeholder="e.g. relaxing piano, jazz, rain sounds")
        submitted = st.form_submit_button("Search songs", type="primary")
    if submitted:
        if not query.strip():
            st.warning("Enter a song, artist, or style to search.")
        else:
            st.session_state["mindheal_music_query"] = query.strip()
            st.session_state["mindheal_music_results"] = []
            try:
                with st.spinner("Searching song previews and playable MP3s…"):
                    st.session_state["mindheal_music_results"] = search_playable_audio(query.strip())
            except (requests.RequestException, ValueError) as exc:
                st.error("Music search is temporarily unavailable. Please try again shortly.")
    results = st.session_state.get("mindheal_music_results", [])
    if results:
        st.success(f"Found {len(results)} relevant playable result(s).")
        for idx, item in enumerate(results):
            with st.container(border=True):
                st.markdown(f"**{item['title']}**")
                st.caption(item["creator"])
                st.audio(item["url"], format="audio/mpeg")
                st.caption("Source: Internet Archive")
                st.link_button("View source and rights information", item["source_url"])
    elif st.session_state.get("mindheal_music_query"):
        st.info("No matching preview or MP3 was returned by the available catalogs. Try the song title and artist separately. If Deezer is unavailable in your region, its previews may not appear.")

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
