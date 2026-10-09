from pathlib import Path
import re
from pypdf import PdfReader
from docx import Document
from core.config import CHUNK_SIZE,CHUNK_OVERLAP,KNOWLEDGE_DIR
from rag.vector_store import add_documents
def extract_text(path):
    if path.suffix.lower()==".pdf": return "\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
    if path.suffix.lower()==".docx": return "\n".join(p.text for p in Document(str(path)).paragraphs)
    return path.read_text(encoding="utf-8",errors="ignore")
def chunk_text(text):
    text=re.sub(r"\s+"," ",text).strip(); out=[]; start=0
    while start<len(text):
        end=min(len(text),start+CHUNK_SIZE); part=text[start:end].strip()
        if part:out.append(part)
        if end>=len(text):break
        start=max(end-CHUNK_OVERLAP,start+1)
    return out
def ingest_file(uploaded_file):
    name=Path(uploaded_file.name).name; path=KNOWLEDGE_DIR/name; path.write_bytes(uploaded_file.getvalue())
    records=[{"text":t,"filename":name,"chunk_id":i} for i,t in enumerate(chunk_text(extract_text(path)))]
    add_documents(records); return len(records)
