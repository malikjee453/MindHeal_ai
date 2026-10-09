from core.config import TOP_K,MAX_CONTEXT_CHARS
from rag.vector_store import search
def retrieve_context(query):
    results=search(query,TOP_K); pieces=[]; sources=[]; total=0
    for r,score in results:
        if total+len(r["text"])>MAX_CONTEXT_CHARS:break
        pieces.append(f"[{r['filename']} / chunk {r['chunk_id']}]\n{r['text']}")
        sources.append({"filename":r["filename"],"chunk_id":r["chunk_id"],"score":round(score,4)}); total+=len(r["text"])
    return "\n\n".join(pieces),sources
