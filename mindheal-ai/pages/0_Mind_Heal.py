import streamlit as st

from core.session import init_session
from core.ui import render_disclaimer
from core.visitor_counter import (
    register_visitor,
    render_visitor_gauge,
    render_visitor_diagnostic,
)

st.set_page_config(page_title="MindHeal AI", page_icon="🌿", layout="wide")
init_session()
render_disclaimer()

st.markdown(
    """
    <style>
    :root { --forest:#174d42; --green:#39856a; --mint:#eaf5ee; --line:#deebe1; --muted:#647e74; }
    .stApp { background: #fbfdfb; }
    .main .block-container { max-width: 1320px; padding-top: 1.5rem; padding-bottom: 3rem; }
    h1,h2,h3,h4 { color:var(--forest) !important; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#eff8f1 0%,#e5f3e9 100%); border-right:1px solid #dcebe0; }
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a { border-radius:12px !important; margin:3px 0 !important; }
    .mh-brandline { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:1.15rem; flex-wrap:wrap; }
    .mh-brand { display:flex; align-items:center; gap:11px; color:var(--forest); font-size:1.15rem; font-weight:800; }
    .mh-brand-mark { width:44px; height:44px; display:flex; align-items:center; justify-content:center; background:#dcefe2; border-radius:15px; font-size:1.55rem; }
    .mh-tag { color:#658176; border:1px solid var(--line); border-radius:999px; padding:8px 14px; background:#fff; font-size:.82rem; }
    .mh-hero { position:relative; overflow:hidden; padding:clamp(25px,4vw,44px); border:1px solid #dcebe0; border-radius:25px; margin:.2rem 0 1.5rem; background:radial-gradient(circle at 88% 18%,rgba(255,255,255,.8),transparent 24%),linear-gradient(112deg,#e0f0e5 0%,#f7f7ed 57%,#d9ebe0 100%); }
    .mh-hero:after { content:'♡'; position:absolute; right:5%; top:2%; font-size:7rem; color:rgba(45,125,89,.12); transform:rotate(12deg); }
    .mh-eyebrow { color:#4b8267; font-size:.76rem; text-transform:uppercase; font-weight:800; letter-spacing:1.6px; margin-bottom:.65rem; }
    .mh-hero h1 { font-size:clamp(2rem,4vw,3.15rem); line-height:1.1; letter-spacing:-1.2px; max-width:720px; margin:0 0 .8rem; }
    .mh-hero p { max-width:700px; color:#526e64; font-size:1.03rem; line-height:1.75; margin:0; }
    .mh-section-title { color:var(--forest); font-size:1.18rem; font-weight:800; margin:.8rem 0 .8rem; }
    .mh-card { height:100%; min-height:158px; background:#fff; border:1px solid #e1ece4; border-radius:19px; padding:20px; box-shadow:0 5px 20px rgba(27,76,57,.035); }
    .mh-card-icon { width:46px; height:46px; border-radius:15px; background:#e8f5eb; display:flex; align-items:center; justify-content:center; font-size:1.4rem; margin-bottom:12px; }
    .mh-card-title { color:#214f42; font-size:1.03rem; font-weight:800; margin-bottom:6px; }
    .mh-card-copy { color:#71857d; font-size:.9rem; line-height:1.6; }
    .mh-friend { background:linear-gradient(145deg,#f0f8f1,#e4f2e8); border:1px solid #deebe0; border-radius:22px; padding:25px; min-height:230px; }
    .mh-friend-heart { color:#39856a; font-size:2.1rem; margin-bottom:8px; }
    .mh-friend h3 { margin:0 0 10px; }
    .mh-friend p { color:#587268; line-height:1.8; margin:0; }
    .mh-quote { color:#426b59; border-left:3px solid #8dbb9a; padding:9px 0 9px 14px; margin-top:17px; font-style:italic; line-height:1.65; }
    .mh-note { border:1px solid #deebe0; border-radius:17px; padding:17px 20px; margin-top:1.25rem; color:#426b59; background:linear-gradient(110deg,#edf7ef,#f8fbf7); font-style:italic; }
    div.stButton > button { border-radius:13px; min-height:43px; font-weight:650; border:1px solid #d7e8db; transition:all .18s ease; }
    div.stButton > button[kind="primary"] { background:linear-gradient(135deg,#2f795d,#459572); border:0; color:white; box-shadow:0 5px 13px rgba(47,121,93,.15); }
    div.stButton > button:hover { border-color:#83b699; transform:translateY(-1px); }
    @media(max-width:700px) { .main .block-container { padding-top:1rem; } .mh-hero { border-radius:18px; } }
    </style>
    """, unsafe_allow_html=True
)

st.markdown(
    """
    <div class="mh-brandline">
      <div class="mh-brand"><span class="mh-brand-mark">🌿</span><span>MindHeal <span style="color:#5b9c79">AI</span></span></div>
      <div class="mh-tag">Your mind • Our care</div>
    </div>
    <section class="mh-hero">
      <div class="mh-eyebrow">A safe space to be yourself</div>
      <h1>Hey, I'm glad you're here. ♡</h1>
      <p>You don't need to fix anything or find the perfect words. Talk about your day, share what's on your mind, or simply say hello. I'll be here to listen, like a friend.</p>
    </section>
    """, unsafe_allow_html=True
)

left, right = st.columns([1.55, 1], gap="large")
with left:
    st.markdown('<div class="mh-section-title">Your space, your way</div>', unsafe_allow_html=True)
    a, b = st.columns(2, gap="medium")
    with a:
        st.markdown('<div class="mh-card"><div class="mh-card-icon">💬</div><div class="mh-card-title">AI Companion</div><div class="mh-card-copy">Talk, share a thought, or have a little conversation. No pressure, no judgement.</div></div>', unsafe_allow_html=True)
        if st.button("Chat with me", key="start_conversation", type="primary", use_container_width=True):
            st.switch_page("pages/1_Chat.py")
    with b:
        st.markdown('<div class="mh-card"><div class="mh-card-icon">🎵</div><div class="mh-card-title">Music & Relaxation</div><div class="mh-card-copy">Spend a quiet moment with the music and sounds already available in the app.</div></div>', unsafe_allow_html=True)
        if st.button("Open music player", key="open_music", use_container_width=True):
            st.switch_page("pages/5_Music_and_Relaxation.py")
    c, d = st.columns(2, gap="medium")
    with c:
        st.markdown('<div class="mh-card"><div class="mh-card-icon">📄</div><div class="mh-card-title">PDF / Documents</div><div class="mh-card-copy">Upload a PDF and ask questions about the document.</div></div>', unsafe_allow_html=True)
        if st.button("Open PDF tools", key="open_pdf", use_container_width=True):
            st.switch_page("pages/5_Upload_PDF.py")
    with d:
        st.markdown('<div class="mh-card"><div class="mh-card-icon">🤍</div><div class="mh-card-title">Support topics</div><div class="mh-card-copy">Open the existing topics for fears, addictions, and mental discomforts.</div></div>', unsafe_allow_html=True)
        if st.button("Explore support topics", key="open_topics", use_container_width=True):
            st.switch_page("pages/2_Mental_Discomforts.py")

with right:
    st.markdown("""<div class="mh-friend"><div class="mh-friend-heart">♡</div><h3>You don't have to pretend here.</h3><p>Whatever kind of day you're having, you can show up just as you are. You can say a lot, a little, or nothing at all.</p><div class="mh-quote">I'm listening. Take your time — I'm here with you.</div></div>""", unsafe_allow_html=True)
    st.markdown('<div class="mh-section-title" style="margin-top:1.25rem">A few more things in your space</div>', unsafe_allow_html=True)
    if st.button("⚙️  Settings", key="open_settings", use_container_width=True):
        st.switch_page("pages/8_Settings.py")
    st.caption("You can personalize the app using its existing settings.")

st.markdown('<div class="mh-note">🌱 &nbsp; You are welcome here, exactly as you are. No pressure to explain everything, and no need to have the right words.</div>', unsafe_allow_html=True)
# Visitor counter (restored from the original project). It requires the existing
# Supabase visitor-counter configuration; the homepage remains usable without it.
visitor_count = register_visitor()
if visitor_count is not None:
    render_visitor_gauge(visitor_count, maximum=100000)
else:
    render_visitor_diagnostic()

st.caption("MindHeal AI is a friendly emotional-support companion and is not a replacement for qualified professional care.")
