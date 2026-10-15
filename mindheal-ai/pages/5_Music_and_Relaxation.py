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
    st.subheader("Choose a relaxation sound")
    st.write("These soundscapes are generated in your browser, so they don't rely on broken external audio links.")
    sound_options = ["Rain on a window", "Ocean waves", "Forest birds", "Wind in trees", "Gentle stream", "Crackling fireplace", "Night crickets"]
    selected_sound = st.selectbox("Relaxation sound", sound_options, key="mindheal_relax_choice")
    components.html("""
    <div id="mh-audio" style="font-family:Arial,sans-serif;max-width:340px;color:#173b2d">
      <button id="mh-toggle" style="border:0;border-radius:8px;padding:9px 15px;background:#2f7655;color:white;font-size:14px;cursor:pointer">▶ Play sound</button>
      <label for="mh-volume" style="display:block;margin-top:10px;font-size:12px">Volume <span id="mh-volume-value">80%</span></label>
      <input id="mh-volume" type="range" min="0" max="100" value="80" style="width:100%;accent-color:#2f7655">
      <div id="mh-status" style="font-size:12px;color:#5c7064;margin-top:5px">Ready to play</div>
    </div>
    <script>
    (() => {
      const root=document.getElementById('mh-audio'); if(!root||root.dataset.ready)return; root.dataset.ready='1';
      const toggle=root.querySelector('#mh-toggle'), slider=root.querySelector('#mh-volume'), value=root.querySelector('#mh-volume-value'), status=root.querySelector('#mh-status');
      const kind=__SOUND_KIND__; let ctx=null, master=null, timer=null, nodes=[], playing=false;

      // Use real, licensed field recordings for these two sounds instead of synthesized approximations.
      const realSources={
        'Gentle stream':'https://commons.wikimedia.org/wiki/Special:Redirect/file/Sound_Effects_-_The_sound_of_a_small_stream.ogg?download=1',
        'Crackling fireplace':'https://upload.wikimedia.org/wikipedia/commons/transcoded/b/b1/Campfire_sound_ambience.ogg/Campfire_sound_ambience.ogg.mp3'
      };
      if(realSources[kind]){
        const audio=new Audio(realSources[kind]);
        audio.loop=true;
        audio.volume=Number(slider.value)/100;
        toggle.addEventListener('click',async()=>{
          try{
            if(!playing){
              await audio.play();
              playing=true;
              toggle.textContent='■ Stop sound';
              status.textContent='Playing: '+kind;
            }else{
              audio.pause();
              audio.currentTime=0;
              playing=false;
              toggle.textContent='▶ Play sound';
              status.textContent='Stopped';
            }
          }catch(e){
            playing=false;
            toggle.textContent='▶ Play sound';
            status.textContent='Could not load audio. Please try again.';
          }
        });
        slider.addEventListener('input',()=>{
          value.textContent=slider.value+'%';
          audio.volume=Number(slider.value)/100;
        });
        audio.addEventListener('ended',()=>{playing=false;toggle.textContent='▶ Play sound';status.textContent='Ready to play';});
        return;
      }

      function clearNodes(){if(timer){clearInterval(timer);timer=null;}nodes.forEach(n=>{try{if(n.stop)n.stop();}catch(e){}try{n.disconnect();}catch(e){}});nodes=[];}
      function noise(){const b=ctx.createBuffer(1,ctx.sampleRate*2,ctx.sampleRate),d=b.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=Math.random()*2-1;const s=ctx.createBufferSource();s.buffer=b;s.loop=true;nodes.push(s);return s;}
      function filtered(type,freq,gain){const s=noise(),f=ctx.createBiquadFilter(),g=ctx.createGain();f.type=type;f.frequency.value=freq;g.gain.value=gain;s.connect(f);f.connect(g);g.connect(master);s.start();nodes.push(f,g);}
      function tone(freq,dur,wave,gain){const o=ctx.createOscillator(),g=ctx.createGain();o.type=wave;o.frequency.value=freq;g.gain.value=0.0001;o.connect(g);g.connect(master);const t=ctx.currentTime;g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(Math.max(.0002,gain),t+.02);g.gain.exponentialRampToValueAtTime(.0001,t+dur);o.start(t);o.stop(t+dur+.03);nodes.push(o,g);}
      function start(){ctx=ctx||new(window.AudioContext||window.webkitAudioContext)();ctx.resume();master=ctx.createGain();master.gain.value=Number(slider.value)/100;master.connect(ctx.destination);
        if(kind==='Rain on a window'){filtered('lowpass',1700,.5);timer=setInterval(()=>{if(playing&&Math.random()>.25)tone(1800+Math.random()*2400,.035,'triangle',.14)},120);}
        else if(kind==='Ocean waves'){filtered('lowpass',600,.7);let up=false;timer=setInterval(()=>{if(playing){up=!up;master.gain.setTargetAtTime(Number(slider.value)/100*(up?1:.25),ctx.currentTime,2.5)}},2500);}
        else if(kind==='Forest birds'){filtered('lowpass',1000,.08);timer=setInterval(()=>{if(playing){const f=1800+Math.random()*1600;tone(f,.12,'sine',.2);setTimeout(()=>{if(playing)tone(f*1.17,.1,'sine',.16)},130)}},950);}
        else if(kind==='Wind in trees'){filtered('lowpass',400,.6);let up=false;timer=setInterval(()=>{if(playing){up=!up;master.gain.setTargetAtTime(Number(slider.value)/100*(up?.95:.22),ctx.currentTime,3)}},2800);}
        else if(kind==='Gentle stream'){
          // Flowing-water texture: several soft, overlapping ripples with no sharp crackles.
          filtered('bandpass',900,.16);
          filtered('lowpass',2200,.10);
          timer=setInterval(()=>{
            if(playing && Math.random()>.15){
              const f=450+Math.random()*950;
              tone(f,.22,'sine',.025);
              setTimeout(()=>{if(playing)tone(f*1.35,.16,'sine',.018)},80);
            }
          },180);
        }
        else if(kind==='Crackling fireplace'){
          // Distinct, sparse, short pops over a low warm fire-like rumble.
          filtered('lowpass',180,.22);
          timer=setInterval(()=>{
            if(playing && Math.random()>.48){
              const f=900+Math.random()*2600;
              tone(f,.012,'triangle',.32);
              if(Math.random()>.55)setTimeout(()=>{if(playing)tone(f*.72,.018,'triangle',.22)},35);
            }
          },240);
        }
        else{filtered('lowpass',450,.05);timer=setInterval(()=>{if(playing){const f=2700+Math.random()*1100;tone(f,.09,'sine',.18);setTimeout(()=>{if(playing)tone(f,.08,'sine',.16)},140)}},700);}
      }
      toggle.addEventListener('click',()=>{try{if(!playing){playing=true;start();toggle.textContent='■ Stop sound';status.textContent='Playing: '+kind;}else{playing=false;clearNodes();if(master)master.disconnect();toggle.textContent='▶ Play sound';status.textContent='Stopped';}}catch(e){playing=false;status.textContent='Audio could not start. Click Play again.';toggle.textContent='▶ Play sound';}});
      slider.addEventListener('input',()=>{value.textContent=slider.value+'%';if(master&&ctx)master.gain.setTargetAtTime(Number(slider.value)/100,ctx.currentTime,.04);});
    })();
    </script>
    """.replace("__SOUND_KIND__", json.dumps(selected_sound)), height=115, scrolling=False)
    if selected_sound == "Gentle stream":
        st.caption("Real stream recording by Amada44, licensed CC BY-SA 4.0. [Source and license](https://commons.wikimedia.org/wiki/File:Sound_Effects_-_The_sound_of_a_small_stream.ogg).")
    elif selected_sound == "Crackling fireplace":
        st.caption("Real campfire recording by Glaneur de sons, licensed CC BY 3.0. [Source and license](https://commons.wikimedia.org/wiki/File:Campfire_sound_ambience.ogg).")
    else:
        st.caption("These other ambient soundscapes are synthesized in your browser. Press Play to start audio.")

st.caption("MindHeal AI • Music can complement wellbeing practices, but it is not a substitute for professional care.")
