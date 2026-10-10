import streamlit as st

from agents.orchestrator import respond
from core.session import init_session
from core.ui import render_header


# =========================================================
# URDU FONT STYLING
# =========================================================

st.markdown(
    """
    <style>

/* Match the Chat page heading to the main MindHeal title color. */
h1, h2, h3, h4, h5, h6,
[data-testid="stHeading"] h1,
[data-testid="stHeading"] h2,
[data-testid="stHeading"] h3,
[data-testid="stHeading"] h4,
[data-testid="stHeading"] h5,
[data-testid="stHeading"] h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
.stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
    color: #173B2D !important;
    -webkit-text-fill-color: #173B2D !important;
}

    @font-face {
        font-family: "JameelNooriNastaleeq";
        src: url("/app/static/JameelNooriNastaleeq.ttf")
             format("truetype");
        font-weight: normal;
        font-style: normal;
    }

    .urdu-response {
        font-family: "JameelNooriNastaleeq", serif !important;
        direction: rtl !important;
        text-align: right !important;
        font-size: 24px !important;
        line-height: 2.2 !important;
        unicode-bidi: plaintext !important;
    }

    .urdu-response * {
        font-family: "JameelNooriNastaleeq", serif !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Detect Urdu
# ---------------------------------------------------------

def contains_urdu(text):
    urdu_chars = (
        "اآبپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنںوہھءیے"
    )

    return any(char in text for char in urdu_chars)


# ---------------------------------------------------------
# Initialize app
# ---------------------------------------------------------

init_session()

render_header(
    "MindHeal AI",
    "Supportive conversations",
    "Engr. Mubashir Malik",
)


# ---------------------------------------------------------
# Compact answer-length tabs
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    /* Force the answer-length segmented control to use MindHeal green,
       overriding Streamlit's default red primary theme. */
    div[data-testid="stSegmentedControl"] button,
    div[data-testid="stSegmentedControl"] button *,
    div[data-testid="stSegmentedControl"] [role="radio"],
    div[data-testid="stSegmentedControl"] [role="radio"] * {
        color: #2F7655 !important;
        border-color: #2F7655 !important;
        min-height: 30px !important;
        padding-top: 3px !important;
        padding-bottom: 3px !important;
        font-size: 0.82rem !important;
        line-height: 1.1 !important;
        --primary-color: #2F7655 !important;
        --primary-color-light: #E8F1EC !important;
    }
    div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
    div[data-testid="stSegmentedControl"] button[aria-checked="true"],
    div[data-testid="stSegmentedControl"] button[data-checked="true"],
    div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"] {
        background: #2F7655 !important;
        color: #FFFFFF !important;
        border-color: #2F7655 !important;
    }
    div[data-testid="stSegmentedControl"] button[aria-pressed="true"] *,
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] *,
    div[data-testid="stSegmentedControl"] button[data-checked="true"] *,
    div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"] * {
        color: #FFFFFF !important;
    }
    div[data-testid="stSegmentedControl"] button:hover,
    div[data-testid="stSegmentedControl"] [role="radio"]:hover {
        border-color: #245C42 !important;
        color: #245C42 !important;
    }
    div[data-testid="stSegmentedControl"] [data-testid="stMarkdownContainer"] p {
        font-size: 0.82rem !important;
        margin: 0 !important;
    }

    /* Clearly outline the chat input box. */
    [data-testid="stChatInput"] {
        border: 1.5px solid #2F7655 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border: 2px solid #2F7655 !important;
        box-shadow: 0 0 0 2px rgba(47, 118, 85, 0.12) !important;
    }
    [data-testid="stChatInput"] textarea {
        border: none !important;
        box-shadow: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


left_space, answer_length_col, right_space = st.columns([1, 2, 1])
with answer_length_col:
    answer_length = st.segmented_control(
        "Answer length",
        options=["Short Answer", "Detailed Answer"],
        default="Short Answer",
        label_visibility="collapsed",
        key="answer_length",
        help="Choose how much detail MindHeal should include in new replies.",
    )

if answer_length is None:
    answer_length = "Short Answer"

# Language selector directly under answer length.
language_col_left, language_col, language_col_right = st.columns([1, 2, 1])
with language_col:
    language_options = ["English", "Urdu"]
    current_language = st.session_state.get("language", "English")
    if current_language not in language_options:
        current_language = "English"
    st.session_state.language = st.selectbox(
        "Response language",
        options=language_options,
        index=language_options.index(current_language),
        key="chat_response_language",
    )

# ---------------------------------------------------------
# Previous messages
# ---------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        content = message["content"]

        if (
            message["role"] == "assistant"
            and contains_urdu(content)
        ):
            st.markdown(
                f'<div class="urdu-response">{content}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(content)


# ---------------------------------------------------------
# Chat input
# ---------------------------------------------------------

prompt = st.chat_input("What's on your mind?")


if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # -----------------------------------------------------
    # Generate response
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        try:

            with st.spinner("Thinking..."):
                answer, sources, route = respond(
                    prompt,
                    response_style=(
                        "detailed"
                        if answer_length == "Detailed Answer"
                        else "short"
                    ),
                    response_language=st.session_state.language,
                )

        except Exception as e:

            answer = (
                "⚠️ I couldn't complete that request.\n\n"
                f"`{type(e).__name__}: {e}`"
            )

            sources = []

        # -------------------------------------------------
        # Display response
        # -------------------------------------------------

        if contains_urdu(answer):

            st.markdown(
                f'<div class="urdu-response">{answer}</div>',
                unsafe_allow_html=True,
            )

        else:

            st.markdown(answer)

        # -------------------------------------------------
        # RAG sources
        # -------------------------------------------------

        if sources:

            with st.expander("Knowledge sources"):

                for source in sources:

                    st.caption(
                        f"{source['filename']} — "
                        f"chunk {source['chunk_id']} "
                        f"(similarity {source['score']})"
                    )

    # -----------------------------------------------------
    # Save response
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
