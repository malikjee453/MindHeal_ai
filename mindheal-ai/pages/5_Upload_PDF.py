import streamlit as st
from rag.ingestion import ingest_file

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

st.title("📄 Upload PDF")
files=st.file_uploader("Upload trusted documents",type=["pdf","docx","txt","md"],accept_multiple_files=True)
if st.button("Index documents",type="primary") and files:
    total=0
    for f in files:
        try: total+=ingest_file(f)
        except Exception as e: st.error(f"{f.name}: {type(e).__name__}: {e}")
    st.success(f"Indexed {total} text chunks.")
