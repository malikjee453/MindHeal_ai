import streamlit as st

from core.config import APP_NAME, APP_TAGLINE, BUILDER
from core.session import init_session
from core.ui import render_disclaimer
from core.visitor_counter import (
    register_visitor,
    render_visitor_gauge,
)
from core.world_clock import render_world_clock


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MindHeal AI",
    page_icon=None,
    layout="wide",
)

init_session()


# =========================================================
# MINDBLOOM HOMEPAGE STYLING
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       PAGE LAYOUT
       ===================================================== */

    .main .block-container {
        max-width: 1100px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }


    /* =====================================================
       TEXT
       ===================================================== */

    .stMarkdown p,
    .stMarkdown li {
        color: #33483d !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #5f7067 !important;
    }


    /* =====================================================
       MINDHEAL BRAND
       ===================================================== */

    .mb-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 6px;
    }

    .mb-logo {
        font-size: 2.7rem;
        line-height: 1;
    }

    .mb-name {
        font-family:
            "Trebuchet MS",
            "Segoe UI",
            Arial,
            sans-serif;

        font-size: 3.25rem;
        font-weight: 900;
        letter-spacing: -2.8px;
        line-height: 1;

        background: linear-gradient(
            135deg,
            #173B2D 0%,
            #2F7655 48%,
            #5A9E78 100%
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .mb-ai {
        color: #D28B35 !important;
        -webkit-text-fill-color: #D28B35 !important;

        font-family:
            "Segoe UI",
            Arial,
            sans-serif;

        font-size: 1rem;
        font-weight: 800;
        letter-spacing: 1.5px;

        vertical-align: super;
        margin-left: 6px;
    }


    /* =====================================================
       TAGLINE
       ===================================================== */

    .mb-tagline {
        color: #53675d !important;
        font-size: 1rem;
        margin-top: 10px;
    }


    /* =====================================================
       BUILDER
       ===================================================== */

    .mb-builder {
        color: #66776e !important;
        font-size: 0.8rem;
        margin-top: 5px;
        margin-bottom: 28px;
    }


    /* =====================================================
       WELCOME MESSAGE
       ===================================================== */

    .mb-welcome {
        font-family:
            "Trebuchet MS",
            "Segoe UI",
            Arial,
            sans-serif;

        font-size: 2.15rem;
        font-weight: 800;
        letter-spacing: -1px;
        line-height: 1.25;

        background: linear-gradient(
            135deg,
            #173B2D 0%,
            #2F7655 50%,
            #5A9E78 100%
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;

        margin-top: 24px;
        margin-bottom: 12px;
    }


    /* =====================================================
       FEATURE TITLES
       ===================================================== */

    .mb-feature-title {
        color: #17231D !important;
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 6px;
    }


    /* =====================================================
       FEATURE TEXT
       ===================================================== */

    .mb-feature-text {
        color: #66756D !important;
        line-height: 1.6;
    }


    /* =====================================================
       START CONVERSATION BUTTON
       ===================================================== */

    div.stButton > button {
        background: linear-gradient(
            135deg,
            #2F7655,
            #438B66
        ) !important;

        color: white !important;

        border: none !important;
        border-radius: 14px !important;

        min-height: 68px !important;
        min-width: 320px !important;

        padding: 12px 28px !important;

        box-shadow:
            0 8px 20px rgba(47, 118, 85, 0.22);

        transition: all 0.2s ease;
    }

    div.stButton > button p {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: white !important;
        line-height: 1.2 !important;
        margin: 0 !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(
            135deg,
            #286648,
            #397A59
        ) !important;

        color: white !important;

        transform: translateY(-2px);

        box-shadow:
            0 12px 26px rgba(47, 118, 85, 0.30);
    }


    /* =====================================================
       DISCLAIMER
       ===================================================== */

    div[data-testid="stExpander"] {
        border-radius: 12px;
        border-color: #DDE6DF;
    }


    /* =====================================================
       VISITOR COUNTER POSITION
       ===================================================== */

    .mb-visitor-card {
        margin-left: auto !important;
        margin-right: auto !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="mb-brand">'
    '<div class="mb-name">MindHeal'
    '<span class="mb-ai">AI</span>'
    '</div>'
    '</div>'
    '<div class="mb-tagline">'
    'A supportive AI companion for emotional growth, habits, fears, '
    'and evidence-informed self-help.'
    '</div>'
    '<div class="mb-builder">'
    'Built by: Engr. Mubashir Malik'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# DISCLAIMER
# =========================================================

render_disclaimer()


# =========================================================
# WELCOME
# =========================================================

st.markdown(
    '<div class="mb-welcome">'
    'Tell Me All,<br>'
    'What You Can\'t Share With Anyone.'
    '</div>',
    unsafe_allow_html=True,
)

st.write(
    "Type your question or share what is on your mind. "
    "You can ask me to answer in English or Urdu."
)


# =========================================================
# FEATURES
# =========================================================

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        '<div class="mb-feature-title">💬 Talk</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="mb-feature-text">'
        'Talk to me, I can help.'
        '</div>',
        unsafe_allow_html=True,
    )


with c2:
    st.markdown(
        '<div class="mb-feature-title">🧠 Explore</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="mb-feature-text">'
        'Find your discomforts, habits, addictions, and fears '
        'here and get advice to overcome them.'
        '</div>',
        unsafe_allow_html=True,
    )


with c3:
    st.markdown(
        '<div class="mb-feature-title">📚 Learn</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="mb-feature-text">'
        'Upload books and documents and ask questions from them '
        'for short-term memory.'
        '</div>',
        unsafe_allow_html=True,
    )




# =========================================================
# VISITOR COUNTER
# =========================================================
render_world_clock()

visitor_count = register_visitor()

if visitor_count is not None:
    render_visitor_gauge(
        visitor_count,
        maximum=100000,
    )


# =========================================================
# START CONVERSATION
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

if st.button(
    "💬  Start a conversation",
    key="start_conversation",
):
    st.switch_page("pages/1_Chat.py")
