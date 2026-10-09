from datetime import datetime
import pandas as pd
import streamlit as st
from core.config import JOURNAL_DIR
st.title("📔 Mood Journal")
mood=st.slider("Mood",1,10,5); energy=st.slider("Energy",1,10,5); stress=st.slider("Stress",1,10,5); note=st.text_area("Reflection")
if st.button("Save entry",type="primary"):
    path=JOURNAL_DIR/"journal.csv"; row=pd.DataFrame([{"timestamp":datetime.now().isoformat(timespec="seconds"),"mood":mood,"energy":energy,"stress":stress,"note":note}])
    if path.exists(): row=pd.concat([pd.read_csv(path),row],ignore_index=True)
    row.to_csv(path,index=False); st.success("Journal entry saved locally.")
path=JOURNAL_DIR/"journal.csv"
if path.exists(): st.dataframe(pd.read_csv(path),use_container_width=True)
