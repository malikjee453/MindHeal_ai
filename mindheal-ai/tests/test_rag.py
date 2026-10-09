from rag.ingestion import chunk_text
def test_chunking(): assert len(chunk_text("a"*2000))>1
