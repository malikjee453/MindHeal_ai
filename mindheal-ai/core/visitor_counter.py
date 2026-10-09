import os
import uuid
import requests
import streamlit as st


# =========================================================
# SUPABASE CONFIGURATION
# =========================================================

def _get_config():
    url = st.secrets.get(
        "SUPABASE_URL",
        os.getenv("SUPABASE_URL", "")
    ).rstrip("/")

    key = st.secrets.get(
        "SUPABASE_ANON_KEY",
        os.getenv("SUPABASE_ANON_KEY", "")
    )

    return url, key


# =========================================================
# GET TOTAL VISITOR COUNT
# =========================================================

def get_visitor_count():
    url, key = _get_config()

    if not url or not key:
        return None

    try:
        response = requests.get(
            f"{url}/rest/v1/visitors",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Prefer": "count=exact",
                "Range": "0-0",
            },
            timeout=5,
        )

        response.raise_for_status()

        content_range = response.headers.get(
            "Content-Range",
            ""
        )

        if "/" in content_range:
            total = content_range.rsplit("/", 1)[1]

            if total != "*":
                return int(total)

        return None

    except Exception:
        return None


# =========================================================
# REGISTER VISITOR
# =========================================================

def register_visitor():

    # Already registered during this Streamlit session
    if st.session_state.get("_visitor_registered"):

        cached_count = st.session_state.get(
            "_visitor_count"
        )

        if cached_count is not None:
            return cached_count

        # Try again if the count was unavailable earlier
        count = get_visitor_count()

        st.session_state["_visitor_count"] = count

        return count

    url, key = _get_config()

    if not url or not key:
        return None

    try:
        visitor_id = str(uuid.uuid4())

        response = requests.post(
            f"{url}/rest/v1/visitors",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            json={
                "visitor_id": visitor_id
            },
            timeout=5,
        )

        response.raise_for_status()

        # Mark this Streamlit session as registered
        st.session_state["_visitor_registered"] = True

        # Get updated visitor total
        count = get_visitor_count()

        st.session_state["_visitor_count"] = count

        return count

    except Exception:
        return None


# =========================================================
# SIMPLE VISITOR COUNTER
# =========================================================

def render_visitor_gauge(count, maximum=100000):

    if count is None:
        return

    count = max(0, int(count))

    st.html(
        f"""
        <style>

        .mb-visitor-simple {{
            margin: 22px 0 18px 0;

            font-family:
                "Segoe UI",
                Arial,
                sans-serif;

            font-size: 0.95rem;

            color: #66756D;

            text-align: left;
        }}

        .mb-visitor-simple-icon {{
            font-size: 1rem;
            margin-right: 5px;
        }}

        .mb-visitor-simple-text {{
            font-weight: 600;
            color: #53675D;
        }}

        .mb-visitor-simple-number {{
            font-weight: 800;
            color: #2F7655;
        }}

        </style>

        <div class="mb-visitor-simple">

            <span class="mb-visitor-simple-icon">
                👤
            </span>

            <span class="mb-visitor-simple-text">
                You are Visitor No:
            </span>

            <span class="mb-visitor-simple-number">
                {count:,}
            </span>

        </div>
        """
    )
