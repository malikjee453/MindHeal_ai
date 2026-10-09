import streamlit as st
def init_session():
    st.session_state.setdefault("messages",[])
    st.session_state.setdefault("language","English")
    st.session_state.setdefault("tone","Warm and practical")
