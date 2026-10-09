import streamlit as st
from core.session import init_session

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
