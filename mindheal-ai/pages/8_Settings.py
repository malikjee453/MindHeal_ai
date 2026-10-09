import streamlit as st
from core.session import init_session
init_session(); st.title("⚙️ Settings")
st.session_state.language=st.selectbox("Language",["English","Urdu","Roman Urdu"])
st.session_state.tone=st.selectbox("Conversation tone",["Warm and practical","Gentle","Direct and structured"])
if st.button("Clear current chat"):
    st.session_state.messages=[]; st.success("Current chat cleared.")
