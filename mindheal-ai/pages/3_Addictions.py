import streamlit as st
from agents.orchestrator import respond
st.title("🔄 Habits & Addictions")
category=st.selectbox("Area",["Alcohol","Nicotine / tobacco","Opioids","Stimulants","Caffeine","Gambling","Internet / smartphone","Social media","Gaming","Pornography / sexual behavior"])
intensity=st.slider("Current urge intensity",0,10,5); trigger=st.text_input("Main trigger"); details=st.text_area("What tends to happen before and after?",height=160)
if st.button("Build a coping plan",type="primary"):
    try:
        answer,_,_=respond(f"I want help with {category}. Urge intensity: {intensity}/10. Trigger: {trigger}. Details: {details}"); st.markdown(answer)
    except Exception as e: st.error(f"{type(e).__name__}: {e}")
