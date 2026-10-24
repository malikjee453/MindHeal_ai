import streamlit as st

from core.session import init_session
from core.ui import render_disclaimer
from core.visitor_counter import (
    register_visitor,
    render_visitor_gauge,
    render_visitor_diagnostic,
)

st.set_page_config(page_title="MindHeal AI | Your Space to Talk", page_icon="🌿", layout="wide")
init_session()
render_disclaimer()

st.markdown(
    """
    <style>
    :root {
        --mh-forest: #173f35;
        --mh-green: #2e7558;
        --mh-mint: #eaf4ed;
        --mh-paper: #fbfcfa;
        --mh-ink: #253b33;
        --mh-muted: #687b73;
        --mh-line: #e1e9e3;
    }
    .stApp { background: var(--mh-paper); color: var(--mh-ink); }
    .main .block-container { max-width: 1240px; padding-top: .8rem; padding-bottom: 1.8rem; }
    h1, h2, h3, h4 { color: var(--mh-forest) !important; letter-spacing: -0.025em; }
    [data-testid="stSidebar"] { background: #f0f6f1; border-right: 1px solid var(--mh-line); }
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a { border-radius: 10px !important; margin: 3px 0 !important; }
    .mh-topbar { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin:.2rem 0 1.15rem; }
    .mh-brand { display:flex; align-items:center; gap:.7rem; font-weight:800; font-size:1.12rem; letter-spacing:-.03em; color:var(--mh-forest); }
    .mh-logo { display:flex; align-items:center; justify-content:center; width:42px; height:42px; border-radius:14px; background:var(--mh-forest); color:white; font-size:1.35rem; box-shadow:0 5px 14px #173f3520; }
    .mh-brand-ai { color:var(--mh-green); }
    .mh-status { display:inline-flex; align-items:center; gap:.45rem; padding:.48rem .8rem; border:1px solid var(--mh-line); border-radius:999px; color:#567066; background:white; font-size:.78rem; font-weight:650; }
    .mh-status-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:#54a878; }
    .mh-hero { display:grid; grid-template-columns:minmax(0,1.35fr) minmax(230px,.65fr); align-items:center; gap:2rem; position:relative; overflow:hidden; padding:clamp(1.25rem,3vw,2.2rem); border:1px solid #dce8de; border-radius:26px; background:linear-gradient(120deg,#e8f3e9 0%,#f5f7ef 62%,#e0eee4 100%); margin:.25rem 0 1.25rem; }
    .mh-hero:after { content:""; position:absolute; width:280px; height:280px; border:1px solid #4c88651b; border-radius:50%; right:-95px; top:-115px; box-shadow:0 0 0 35px #4c886509,0 0 0 70px #4c886506; pointer-events:none; }
    .mh-eyebrow { color:var(--mh-green); text-transform:uppercase; font-size:.72rem; letter-spacing:.15em; font-weight:800; margin-bottom:.9rem; }
    .mh-hero h1 { font-size:clamp(2.15rem,4.4vw,3.55rem); line-height:1.06; letter-spacing:-.055em; max-width:670px; margin:0 0 1rem; }
    .mh-hero-copy { max-width:650px; color:#52695f; font-size:1.02rem; line-height:1.85; margin:0; }
    .mh-hero-aside { position:relative; z-index:1; padding:1.35rem; border:1px solid #ffffffb5; border-radius:21px; background:#ffffff9c; box-shadow:0 12px 34px #214f3710; }
    .mh-aside-icon { display:flex; align-items:center; justify-content:center; width:48px; height:48px; border-radius:16px; background:#dceee1; color:var(--mh-forest); font-size:1.55rem; margin-bottom:1rem; }
    .mh-hero-aside h3 { font-size:1.12rem; margin:0 0 .55rem; }
    .mh-hero-aside p { color:#62756b; font-size:.9rem; line-height:1.75; margin:0; }
    .mh-section-head { display:flex; align-items:end; justify-content:space-between; gap:1rem; margin:.2rem 0 .65rem; }
    .mh-section-title { color:var(--mh-forest); font-size:1.32rem; font-weight:800; letter-spacing:-.035em; margin:0 0 .28rem; }
    .mh-section-subtitle { color:var(--mh-muted); font-size:.9rem; margin:0; line-height:1.6; }
    .mh-feature { min-height:150px; padding:1rem; background:#fff; border:1px solid var(--mh-line); border-radius:19px; box-shadow:0 4px 18px #183f2d06; transition:transform .18s ease, box-shadow .18s ease; }
    .mh-feature-icon { width:38px; height:38px; display:flex; align-items:center; justify-content:center; border-radius:14px; background:var(--mh-mint); font-size:1.35rem; margin-bottom:1rem; }
    .mh-feature-title { color:var(--mh-forest); font-weight:800; font-size:1rem; margin-bottom:.45rem; }
    .mh-feature-copy { color:var(--mh-muted); font-size:.88rem; line-height:1.7; min-height:4.5rem; }
    .mh-values { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.55rem; margin-top:.8rem; }
    .mh-value { padding:.7rem; background:#f2f7f2; border:1px solid #e4ece4; border-radius:15px; }
    .mh-value strong { display:block; color:var(--mh-forest); font-size:.88rem; margin-bottom:.28rem; }
    .mh-value span { display:block; color:var(--mh-muted); font-size:.76rem; line-height:1.4; }
    .mh-quote-panel { height:100%; min-height:210px; padding:1.2rem; border-radius:21px; background:var(--mh-forest); color:#fff; display:flex; flex-direction:column; justify-content:space-between; }
    .mh-quote-mark { color:#b5d8be; font-size:2.5rem; line-height:1; }
    .mh-quote-panel h3 { color:#fff !important; font-size:1.25rem; line-height:1.3; margin:.55rem 0; letter-spacing:-.035em; }
    .mh-quote-panel p { color:#d1e2d7; font-size:.88rem; line-height:1.75; margin:0; }
    .mh-quote-foot { margin-top:1.5rem; color:#b7d7c2; font-size:.78rem; letter-spacing:.04em; }
    .mh-bottom-note { display:flex; align-items:flex-start; gap:.8rem; margin-top:1.6rem; padding:1.05rem 1.2rem; border:1px solid var(--mh-line); border-radius:15px; background:#fff; color:#5d7167; font-size:.86rem; line-height:1.7; }
    div.stButton > button { border-radius:12px; min-height:43px; font-weight:700; border:1px solid #d9e5dc; transition:all .18s ease; }
    div.stButton > button[kind="primary"] { background:var(--mh-green); border:1px solid var(--mh-green); color:white; box-shadow:0 5px 13px #2e75581c; }
    div.stButton > button:hover { border-color:#80ad91; transform:translateY(-1px); }
    @media(max-width:760px) {
        .main .block-container { padding-top:.8rem; }
        .mh-hero { grid-template-columns:1fr; gap:1.2rem; border-radius:20px; }
        .mh-hero-aside { max-width:none; }
        .mh-values { grid-template-columns:1fr; }
        .mh-status { font-size:.7rem; }
        .mh-section-head { align-items:start; flex-direction:column; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mh-topbar">
      <div class="mh-brand"><span class="mh-logo">✳</span><span>MindHeal <span class="mh-brand-ai">AI</span></span></div>
      <div class="mh-status"><span class="mh-status-dot"></span> A little space for you</div>
    </div>
    <section class="mh-hero">
      <div>
        <div class="mh-eyebrow">A thoughtful AI companion</div>
        <h1>A place to pause, reflect, and be yourself.</h1>
        <p class="mh-hero-copy">A friendly space to talk, ask questions, and be yourself — at your own pace.</p>
      </div>
      <aside class="mh-hero-aside">
        <div class="mh-aside-icon">♡</div>
        <h3>Come as you are.</h3>
        <p>Talk, explore a topic, or simply say hello.</p>
      </aside>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mh-section-head">
      <div>
        <div class="mh-section-title">Explore your space</div>
        <p class="mh-section-subtitle">Pick a place to start.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3, gap="medium")
with col1:
    st.markdown('<div class="mh-feature"><div class="mh-feature-icon">💬</div><div class="mh-feature-title">AI Companion</div><div class="mh-feature-copy">Talk things through or ask a question.</div></div>', unsafe_allow_html=True)
    if st.button("Start a conversation  →", key="start_conversation", type="primary", use_container_width=True):
        st.switch_page("pages/1_Chat.py")
with col2:
    st.markdown('<div class="mh-feature"><div class="mh-feature-icon">🎧</div><div class="mh-feature-title">Music & Relaxation</div><div class="mh-feature-copy">Listen to music and calming sounds.</div></div>', unsafe_allow_html=True)
    if st.button("Open music player  →", key="open_music", use_container_width=True):
        st.switch_page("pages/5_Music_and_Relaxation.py")
with col3:
    st.markdown('<div class="mh-feature"><div class="mh-feature-icon">📚</div><div class="mh-feature-title">PDF & Documents</div><div class="mh-feature-copy">Upload a PDF and ask questions about it.</div></div>', unsafe_allow_html=True)
    if st.button("Explore PDF tools  →", key="open_pdf", use_container_width=True):
        st.switch_page("pages/5_Upload_PDF.py")

st.markdown('<div style="height:1.2rem"></div>', unsafe_allow_html=True)
left, right = st.columns([1.25, 1], gap="large")
with left:
    st.markdown(
        """
        <div class="mh-section-title">Your space, your pace</div>
        <p class="mh-section-subtitle">Simple, friendly, and always your choice.</p>
        <div class="mh-values">
          <div class="mh-value"><strong>🌱 No pressure</strong><span>Start anywhere.</span></div>
          <div class="mh-value"><strong>🤝 Friendly</strong><span>No judgement.</span></div>
          <div class="mh-value"><strong>🔒 Your choice</strong><span>Go at your pace.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div style="height:1.1rem"></div>', unsafe_allow_html=True)
    topics_col, settings_col = st.columns(2, gap="small")
    with topics_col:
        if st.button("♡  Explore support topics", key="open_topics", use_container_width=True):
            st.switch_page("pages/2_Mental_Discomforts.py")
    with settings_col:
        if st.button("⚙️  Personalize settings", key="open_settings", use_container_width=True):
            st.switch_page("pages/8_Settings.py")
with right:
    st.markdown(
        """
        <div class="mh-quote-panel">
          <div>
            <div class="mh-quote-mark">“</div>
            <h3>You can start just as you are.</h3>
            <p>Share a thought, ask a question, or say hello.</p>
          </div>
          <div class="mh-quote-foot">YOUR SPACE · YOUR PACE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="mh-bottom-note"><span>✦</span><span><strong>A gentle reminder:</strong> MindHeal AI is designed for friendly conversation and emotional support. It is not a replacement for qualified professional care.</span></div>',
    unsafe_allow_html=True,
)

# Preserve the existing visitor counter and its diagnostics.
visitor_count = register_visitor()
if visitor_count is not None:
    render_visitor_gauge(visitor_count, maximum=100000)
else:
    render_visitor_diagnostic()

st.caption("MindHeal AI · A friendly place to pause and talk.")
