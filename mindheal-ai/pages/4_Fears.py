import streamlit as st
from agents.orchestrator import respond
st.title("🌤️ Fears")
fear=st.selectbox("Choose a fear",["Death","Public speaking","Failure","Rejection / abandonment","Heights","Spiders / insects","Darkness","Losing control","Loneliness / isolation","Unknown / uncertainty"])
situation=st.text_area("Describe what happens when this fear appears",height=160)
if st.button("Work through this fear",type="primary") and situation:
    try:
        answer,_,_=respond(f"My fear is {fear}. {situation}"); st.markdown(answer)
    except Exception as e: st.error(f"{type(e).__name__}: {e}")
