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

## Private background memory and progress tracking

To enable email/password accounts and opt-in memory:

1. In Supabase, open **SQL Editor** and run the complete script in `supabase_mindheal_memory.sql`.
2. In Streamlit Cloud, open the app's **Settings → Secrets** and add:
   ```toml
   SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co"
   SUPABASE_ANON_KEY = "YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY"
   ```
   Use the project's publishable/anon key only; **never put a service-role key in Streamlit secrets or client code**.
3. Reboot the Streamlit app. Users can create an account or sign in on the Chat page.
4. Memory is **off by default**. A signed-in user must turn on **Enable background memory** in Settings to save conversation turns and background summaries. The Settings page also supports deleting saved conversation memory and progress check-ins.
5. Progress check-ins are optional and user-entered. The app compares self-reported mood and stress ratings over time; these are not diagnoses or objective measures of mental health.

Supabase Auth handles password authentication; MindHeal does not store plaintext passwords. The SQL enables row-level security so account records are restricted to the authenticated user's ID. Keep the Supabase project and keys secure.

The background summary uses the existing `openai/gpt-oss-120b` model through Groq when enabled. This is retrieval/context memory, **not model training**.

## Privacy and wellbeing

The visitor counter, when configured, records anonymous session identifiers and timestamps. Do not place API keys in source code or commit secrets to GitHub. MindHeal AI is not a substitute for qualified mental-health care or emergency services.
