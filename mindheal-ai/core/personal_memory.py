"""Opt-in, per-account memory for MindHeal using Supabase Auth + RLS-protected tables."""
import os
import requests
import streamlit as st

TIMEOUT = 15

def _config():
    try:
        url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", "")).rstrip("/")
        key = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
    except Exception:
        url = os.getenv("SUPABASE_URL", "").rstrip("/")
        key = os.getenv("SUPABASE_ANON_KEY", "")
    if not url or not key:
        return None, None
    return url, key

def configured():
    url, key = _config()
    return bool(url and key)

def _auth_request(endpoint, payload):
    url, key = _config()
    if not url or not key:
        return False, "Account service is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY to Streamlit secrets."
    try:
        r = requests.post(f"{url}/auth/v1/{endpoint}", json=payload,
                          headers={"apikey": key, "Content-Type": "application/json"}, timeout=TIMEOUT)
        data = r.json() if r.content else {}
        if r.ok:
            return True, data
        return False, data.get("msg") or data.get("message") or data.get("error_description") or "Authentication failed."
    except requests.RequestException:
        return False, "Could not reach the account service. Please try again."

def sign_up(email, password):
    return _auth_request("signup", {"email": email.strip(), "password": password})

def sign_in(email, password):
    return _auth_request("token?grant_type=password", {"email": email.strip(), "password": password})

def _headers():
    url, key = _config()
    token = st.session_state.get("mindheal_access_token")
    if not url or not key or not token:
        return None, None
    return url, {"apikey": key, "Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def db_request(table, method="GET", params=None, body=None, prefer=None):
    url, headers = _headers()
    if not url:
        return None
    if prefer:
        headers["Prefer"] = prefer
    try:
        r = requests.request(method, f"{url}/rest/v1/{table}", headers=headers,
                             params=params, json=body, timeout=TIMEOUT)
        if not r.ok:
            return None
        if r.status_code == 204 or not r.content:
            return []
        return r.json()
    except (requests.RequestException, ValueError):
        return None

def user_id():
    return st.session_state.get("mindheal_user_id")

def logged_in():
    return bool(user_id() and st.session_state.get("mindheal_access_token"))

def require_auth():
    if not logged_in():
        st.info("Please sign in from the Chat page to access your private MindHeal account.")
        st.stop()

def load_profile():
    rows = db_request("mindheal_profiles", params={"select":"user_id,display_name,memory_enabled,memory_summary","limit":"1"})
    if rows:
        return rows[0]
    uid = user_id()
    if uid:
        db_request("mindheal_profiles", method="POST", body={"user_id":uid,"display_name":"","memory_enabled":False,"memory_summary":""}, prefer="resolution=merge-duplicates,return=minimal")
    return {"user_id":uid,"display_name":"","memory_enabled":False,"memory_summary":""}

def save_profile(display_name=None, memory_enabled=None, memory_summary=None):
    profile = load_profile()
    body = {"user_id":user_id()}
    for key, value in (("display_name",display_name),("memory_enabled",memory_enabled),("memory_summary",memory_summary)):
        if value is not None:
            body[key] = value
    db_request("mindheal_profiles", method="POST", body=body, prefer="resolution=merge-duplicates,return=minimal")

def save_turn(role, content):
    if not logged_in() or not st.session_state.get("mindheal_memory_enabled"):
        return
    db_request("mindheal_turns", method="POST", body={"user_id":user_id(),"role":role,"content":content[:12000]}, prefer="return=minimal")

def recent_turns(limit=12):
    rows = db_request("mindheal_turns", params={"select":"role,content,created_at","order":"created_at.desc","limit":str(limit)})
    return list(reversed(rows or []))

def save_progress(mood, stress, note=""):
    return db_request("mindheal_progress", method="POST", body={"user_id":user_id(),"mood":int(mood),"stress":int(stress) if stress is not None else None,"note":note[:1000]}, prefer="return=minimal") is not None

def get_progress(limit=30):
    return db_request("mindheal_progress", params={"select":"mood,stress,note,created_at","order":"created_at.asc","limit":str(limit)}) or []

def clear_memory():
    db_request("mindheal_turns", method="DELETE", params={"user_id":f"eq.{user_id()}"})
    save_profile(memory_summary="")
