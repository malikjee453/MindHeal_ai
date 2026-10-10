import streamlit as st
from core.session import init_session

st.markdown("""
<style>
/* Keep every page heading the same deep green as the MindHeal brand title. */
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
</style>
""", unsafe_allow_html=True)

init_session()
st.title("⚙️ Settings")
st.session_state.tone = st.selectbox(
    "Conversation tone",
    ["Warm and practical", "Gentle", "Direct and structured"],
    index=["Warm and practical", "Gentle", "Direct and structured"].index(
        st.session_state.get("tone", "Warm and practical")
    ) if st.session_state.get("tone", "Warm and practical") in ["Warm and practical", "Gentle", "Direct and structured"] else 0,
)

if st.button("Clear current chat"):
    st.session_state.messages = []
    st.success("Current chat cleared.")
