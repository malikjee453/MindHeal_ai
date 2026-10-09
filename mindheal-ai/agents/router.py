import json,re
from core.groq_client import chat
from core.models import RouteDecision
from core.prompts import ROUTER_PROMPT
def route_message(text):
    try:
        raw=chat([{"role":"system","content":ROUTER_PROMPT},{"role":"user","content":text}],temperature=0,max_tokens=250)
        m=re.search(r"\{.*\}",raw,re.S)
        if m: return RouteDecision.model_validate(json.loads(m.group(0)))
    except Exception: pass
    x=text.lower()
    if any(t in x for t in ["suicide","kill myself","hurt myself","overdose"]): return RouteDecision(route="CRISIS",rationale="Safety fallback")
    if any(t in x for t in ["addiction","craving","nicotine","alcohol","gambling","porn","opioid"]): return RouteDecision(route="ADDICTION",rationale="Keyword fallback")
    if any(t in x for t in ["fear","afraid","phobia","panic","scared"]): return RouteDecision(route="FEAR",rationale="Keyword fallback")
    return RouteDecision(route="GENERAL_EMOTIONAL_SUPPORT",rationale="Default")
