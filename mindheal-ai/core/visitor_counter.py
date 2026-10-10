"""Supabase-backed anonymous visitor counter for MindHeal AI."""
import os
import uuid

import requests
import streamlit as st

TIMEOUT = 8


def _get_config():
    """Read Supabase config safely; missing Streamlit secrets must not break the app."""
    try:
        url = st.secrets.get("SUPABASE_URL", "") or os.getenv("SUPABASE_URL", "")
        # Support both the legacy anon key and the newer publishable-key name.
        key = (
            st.secrets.get("SUPABASE_ANON_KEY", "")
            or st.secrets.get("SUPABASE_PUBLISHABLE_KEY", "")
            or os.getenv("SUPABASE_ANON_KEY", "")
            or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
        )
    except Exception:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_ANON_KEY", "") or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")

    url = (url or "").strip().rstrip("/")
    key = (key or "").strip()
    return url, key


def _headers(key):
    headers = {
        "apikey": key,
        "Content-Type": "application/json",
    }
    # Legacy anon keys are JWTs and can also be used as the bearer token.
    # New sb_publishable_* keys are not JWTs; sending them as Bearer can fail JWT validation.
    if key.count(".") == 2 and not key.startswith("sb_publishable_"):
        headers["Authorization"] = f"Bearer {key}"
    return headers


def _set_error(message):
    # Never include configuration values or request headers in diagnostic text.
    st.session_state["_visitor_error"] = message


def _response_error(response, action):
    """Convert common Supabase responses into a short, safe diagnostic."""
    status = response.status_code
    try:
        data = response.json()
        code = str(data.get("code", "") or "")
        message = str(data.get("message", "") or data.get("msg", "") or "")
    except (ValueError, AttributeError):
        code, message = "", ""

    if status in (401, 403):
        _set_error(
            f"Supabase denied the visitor-counter {action} (HTTP {status}). "
            "Check the project URL/key, Data API access, table grants, and anon RLS policy."
        )
    elif status == 404 or code == "PGRST205":
        _set_error(
            "Supabase could not find public.visitors through the Data API. "
            "Check that the visitors table exists in the public schema and is exposed."
        )
    elif code == "42501":
        _set_error(
            "Supabase is missing a database grant for the visitor counter. "
            "Apply the visitor-counter SQL setup in the repository."
        )
    elif message:
        _set_error(f"Supabase visitor-counter {action} failed (HTTP {status}): {message[:180]}")
    else:
        _set_error(f"Supabase visitor-counter {action} failed (HTTP {status}).")


def get_visitor_count():
    url, key = _get_config()
    if not url or not key:
        _set_error("Visitor counter is not configured. Check SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit secrets.")
        return None

    try:
        response = requests.get(
            f"{url}/rest/v1/visitors",
            headers={**_headers(key), "Prefer": "count=exact", "Range": "0-0"},
            params={"select": "visitor_id"},
            timeout=TIMEOUT,
        )
        if not response.ok:
            _response_error(response, "count request")
            return None

        content_range = response.headers.get("Content-Range", "")
        if "/" in content_range:
            total = content_range.rsplit("/", 1)[1]
            if total != "*":
                st.session_state.pop("_visitor_error", None)
                return int(total)

        _set_error(
            "Supabase responded, but did not return an exact visitor count. "
            "Check that the visitors table allows SELECT for the anon role."
        )
        return None
    except requests.RequestException:
        _set_error("Could not connect to Supabase for the visitor count. Check the project URL and network.")
        return None


def register_visitor():
    # Avoid inserting multiple rows on Streamlit reruns in the same browser session.
    if st.session_state.get("_visitor_registered"):
        cached_count = st.session_state.get("_visitor_count")
        if cached_count is not None:
            return cached_count
        count = get_visitor_count()
        st.session_state["_visitor_count"] = count
        return count

    url, key = _get_config()
    if not url or not key:
        _set_error("Visitor counter is not configured. Check SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit secrets.")
        return None

    try:
        response = requests.post(
            f"{url}/rest/v1/visitors",
            headers={**_headers(key), "Prefer": "return=minimal"},
            json={"visitor_id": str(uuid.uuid4())},
            timeout=TIMEOUT,
        )
        if not response.ok:
            _response_error(response, "insert")
            return None

        st.session_state["_visitor_registered"] = True
        count = get_visitor_count()
        st.session_state["_visitor_count"] = count
        return count
    except requests.RequestException:
        _set_error("Could not connect to Supabase to register this visit. Check the project URL and network.")
        return None


def render_visitor_gauge(count, maximum=100000):
    if count is None:
        return

    count = max(0, int(count))
    st.html(
        f"""
        <style>
        .mb-visitor-simple {{
            margin: 22px 0 18px 0;
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 0.95rem;
            color: #66756D;
            text-align: left;
        }}
        .mb-visitor-simple-icon {{ font-size: 1rem; margin-right: 5px; }}
        .mb-visitor-simple-text {{ font-weight: 600; color: #53675D; }}
        .mb-visitor-simple-number {{ font-weight: 800; color: #2F7655; }}
        </style>
        <div class="mb-visitor-simple">
            <span class="mb-visitor-simple-icon">👤</span>
            <span class="mb-visitor-simple-text">You are Visitor No:</span>
            <span class="mb-visitor-simple-number">{count:,}</span>
        </div>
        """
    )


def render_visitor_diagnostic():
    """Show a helpful message only when the counter failed; never show secret values."""
    message = st.session_state.get("_visitor_error")
    if message:
        st.caption(f"Visitor counter unavailable: {message}")
