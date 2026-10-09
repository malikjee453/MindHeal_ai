import pandas as pd
import streamlit as st
from core.config import JOURNAL_DIR
st.title("📈 Progress")
path=JOURNAL_DIR/"journal.csv"
if not path.exists(): st.info("Add mood-journal entries to see progress.")
else:
    df=pd.read_csv(path); st.line_chart(df.set_index("timestamp")[["mood","energy","stress"]]); st.dataframe(df,use_container_width=True)
