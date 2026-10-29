import streamlit as st

from core.session import init_session
from core.visitor_counter import register_visitor, render_visitor_gauge, render_visitor_diagnostic

st.set_page_config(page_title="MindHeal AI | Your Space to Talk", page_icon="🌿", layout="wide")
init_session()

st.markdown(
    """
    <style>
    :root {
        --mh-forest: #173f35;
        --mh-green: #2e7558;
        --mh-mint: #eaf4ed;
        --mh-paper: #fbfcfa;
        --mh-muted: #687b73;
        --mh-line: #e1e9e3;
    }
    .stApp { background: var(--mh-paper); color: var(--mh-forest); }
    .main .block-container {
        max-width: 1120px;
        padding-top: .35rem;
        padding-bottom: 1rem;
    }
    [data-testid="stSidebar"] { background: #f0f6f1; border-right: 1px solid var(--mh-line); }
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a { border-radius: 10px !important; margin: 3px 0 !important; }
    .mh-home {
        position: relative;
        overflow: hidden;
        margin: .2rem 0 1.15rem;
        padding: clamp(1.5rem, 4vw, 3rem) clamp(1.2rem, 5vw, 4.5rem);
        border: 1px solid #dce8de;
        border-radius: 28px;
        background: linear-gradient(125deg, #e8f3e9 0%, #f6f8f2 58%, #e2efe5 100%);
        text-align: center;
    }
    .mh-home:before {
        content: "";
        position: absolute;
        width: 270px; height: 270px;
        top: -155px; right: -70px;
        border-radius: 50%;
        border: 1px solid #4c88651b;
        box-shadow: 0 0 0 32px #4c886509, 0 0 0 64px #4c886506;
        pointer-events: none;
    }
    .mh-brand {
        display: flex; justify-content: center; align-items: center; gap: .65rem;
        margin: 0 0 1.1rem;
        color: var(--mh-forest); font-weight: 850; font-size: 1.1rem; letter-spacing: -.035em;
    }
    .mh-logo {
        display: inline-flex; align-items: center; justify-content: center;
        width: 40px; height: 40px; border-radius: 14px;
        background: var(--mh-forest); color: white; font-size: 1.35rem;
        box-shadow: 0 5px 14px #173f3520;
    }
    .mh-brand-ai { color: var(--mh-green); }
    .mh-home h1 {
        color: var(--mh-forest) !important;
        font-size: clamp(2.1rem, 5vw, 3.6rem);
        line-height: 1.08; letter-spacing: -.055em;
        margin: 0 auto .8rem; max-width: 760px;
    }
    .mh-greeting {
        color: #52695f; font-size: clamp(1rem, 2vw, 1.15rem);
        line-height: 1.65; margin: 0 auto .4rem; max-width: 580px;
    }
    .mh-heart {
        display: inline-flex; align-items: center; justify-content: center;
        width: 48px; height: 48px; margin: 0 auto .8rem;
        border-radius: 17px; background: #dceee1; color: var(--mh-forest);
        font-size: 1.6rem;
    }
    div.stButton > button {
        border-radius: 14px; min-height: 48px; font-weight: 750;
        border: 1px solid #d9e5dc; transition: all .18s ease;
    }
    div.stButton > button[kind="primary"] {
        background: var(--mh-green); border: 1px solid var(--mh-green);
        color: white; box-shadow: 0 5px 13px #2e75581c;
    }
    div.stButton > button:hover { border-color: #80ad91; transform: translateY(-1px); }
    .mh-counter {
        margin: .5rem auto 0; padding: .7rem 1rem; width: fit-content;
        color: #53675d; background: white; border: 1px solid var(--mh-line);
        border-radius: 999px; font-size: .9rem;
    }
    @media (max-width: 760px) {
        .main .block-container { padding-top: .25rem; }
        .mh-home { border-radius: 21px; padding: 1.5rem 1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="mh-home">
      <div class="mh-brand"><span class="mh-logo">✳</span><span>MindHeal <span class="mh-brand-ai">AI</span></span></div>
      <div class="mh-heart">♡</div>
      <h1>It's good to have you here.</h1>
      <p class="mh-greeting">Take a breath. Be yourself. I'm here for a friendly chat whenever you're ready.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

button_col = st.columns([1, 1.25, 1])[1]
with button_col:
    if st.button("💬  Let's talk", key="start_conversation", type="primary", use_container_width=True):
        st.switch_page("pages/1_Chat.py")

# Keep the existing visitor counter, displayed simply below the main action.
visitor_count = register_visitor()
if visitor_count is not None:
    st.markdown('<div class="mh-counter">✦  You are visitor number ' + f'{visitor_count:,}' + '</div>', unsafe_allow_html=True)
else:
    render_visitor_diagnostic()
