from agents.router import route_message
from agents.specialists import run_specialist
from agents.composer import compose_response
from core.safety import assess_safety,CRISIS_RESPONSE
from rag.retriever import retrieve_context
def respond(user_text, response_style="short", response_language="English", memory_context="", conversation_context=""):
    safety=assess_safety(user_text)
    if safety.level=="crisis": return CRISIS_RESPONSE,[],"CRISIS"
    route=route_message(user_text)
    context,sources=retrieve_context(user_text)
    analysis=run_specialist(route.route,user_text,context,memory_context=memory_context,conversation_context=conversation_context)
    answer=compose_response(
        user_text,
        analysis,
        safety.rationale if safety.level!="low" else "",
        response_style=response_style,
        response_language=response_language,
        memory_context=memory_context,
        conversation_context=conversation_context,
    )
    return answer,sources,route.route
