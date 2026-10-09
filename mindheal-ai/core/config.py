from pathlib import Path
import os
APP_NAME = "MindHeal AI"
APP_TAGLINE = "A supportive AI companion for emotional growth, habits, and fears."
BUILDER = "Engr. Mubashir Malik"
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
INDEX_DIR = DATA_DIR / "index"
JOURNAL_DIR = DATA_DIR / "journal"
for d in (KNOWLEDGE_DIR, INDEX_DIR, JOURNAL_DIR): d.mkdir(parents=True, exist_ok=True)
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
TOP_K = 5
MAX_CONTEXT_CHARS = 9000
