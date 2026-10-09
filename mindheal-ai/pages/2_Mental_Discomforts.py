import streamlit as st
from agents.orchestrator import respond
st.title("🧠 Mental Discomforts")
topic=st.selectbox("Choose a topic",["Uncertainty","Cognitive dissonance","Boredom","Rejection","Regret","Envy","Guilt / shame","Decision fatigue","FOMO","Loneliness"])
details=st.text_area("What are you experiencing?",height=160)
if st.button("Help me work through it",type="primary") and details:
    try:
        answer,_,_=respond(f"I am experiencing {topic}. {details}"); st.markdown(answer)
    except Exception as e: st.error(f"{type(e).__name__}: {e}")
