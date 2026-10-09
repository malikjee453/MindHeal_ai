# MindHeal AI Visitor Gauge

1. Run `supabase_visitors.sql` once in your Supabase SQL Editor.
2. Add `core/visitor_counter.py` to your project.
3. Add `requests` to `requirements.txt`.
4. Put `SUPABASE_URL` and `SUPABASE_ANON_KEY` in Streamlit Cloud Secrets.
5. In `app.py`, add:

   from core.visitor_counter import register_visitor, render_visitor_gauge

   visitor_count = register_visitor()
   if visitor_count is not None:
       render_visitor_gauge(visitor_count, maximum=max(1000, ((visitor_count // 1000)+1)*1000))

The counter stores only a random anonymous UUID and timestamp. It does not
store IP, name, email, or chat content. It counts anonymous browser sessions,
not verified unique people.
