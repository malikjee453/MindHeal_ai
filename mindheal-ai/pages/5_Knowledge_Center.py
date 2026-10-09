import streamlit as st
from rag.ingestion import ingest_file
st.title("📚 Knowledge Center")
files=st.file_uploader("Upload trusted documents",type=["pdf","docx","txt","md"],accept_multiple_files=True)
if st.button("Index documents",type="primary") and files:
    total=0
    for f in files:
        try: total+=ingest_file(f)
        except Exception as e: st.error(f"{f.name}: {type(e).__name__}: {e}")
    st.success(f"Indexed {total} text chunks.")
