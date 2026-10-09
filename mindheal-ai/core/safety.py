import json,re
from .groq_client import chat
from .models import SafetyAssessment
from .prompts import BASE_SYSTEM
CRISIS_RESPONSE = """I’m glad you said this instead of handling it alone. If you may hurt yourself or someone else, have taken an overdose, or are in immediate danger, contact your local emergency service now or go to the nearest emergency department. If possible, stay with a trusted person and move away from anything you could use to cause harm. If the danger is not immediate, contact a qualified mental-health or addiction professional and a trusted person today. I can stay with you here and help you focus on the next safe step."""
def assess_safety(text):
    try:
        raw=chat([{"role":"system","content":BASE_SYSTEM},{"role":"user","content":f'Assess this message for immediate safety risk. Return JSON only with level, self_harm, harm_to_others, overdose_or_dangerous_withdrawal, rationale. Message: {text}'}],temperature=0,max_tokens=300)
        m=re.search(r"\{.*\}",raw,re.S)
        if m: return SafetyAssessment.model_validate(json.loads(m.group(0)))
    except Exception: pass
    x=text.lower(); terms=["kill myself","suicide","end my life","hurt myself","self harm","kill someone","hurt someone","overdose"]
    if any(t in x for t in terms):
        return SafetyAssessment(level="crisis",self_harm=any(t in x for t in ["suicide","kill myself","hurt myself","self harm"]),harm_to_others=any(t in x for t in ["kill someone","hurt someone"]),overdose_or_dangerous_withdrawal="overdose" in x,rationale="Fallback safety detection.")
    return SafetyAssessment()
