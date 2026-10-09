# MindHeal AI

MindHeal AI is a Streamlit-based emotional-support companion with a multi-agent response workflow and retrieval-augmented knowledge support. It is designed for reflection and general educational support, not diagnosis or emergency care.

## Run locally

1. Install Python 3.11 or newer.
2. Install dependencies: `pip install -r requirements.txt`
3. Set `GROQ_API_KEY` in your environment. The default model is `openai/gpt-oss-120b`; you can override it with `GROQ_MODEL`.
4. Run from this project directory: `streamlit run app.py`.

## Streamlit Community Cloud

- Repository: `malikjee453/MindBloom_Ai` (unless you later rename the repository itself)
- Branch: `main`
- Main file path: `mindheal-ai/app.py`
- Add `GROQ_API_KEY` in the app's Secrets settings. If using the visitor counter, also configure `SUPABASE_URL` and `SUPABASE_ANON_KEY`.

The repository contains one top-level project folder, `mindheal-ai/`. Folders such as `agents/`, `core/`, `pages/`, and `rag/` are required parts of the application and should be kept.

## Privacy and wellbeing

The visitor counter, when configured, records anonymous session identifiers and timestamps. Do not place API keys in source code or commit secrets to GitHub. MindHeal AI is not a substitute for qualified mental-health care or emergency services.
