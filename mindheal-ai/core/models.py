from typing import List, Literal
from pydantic import BaseModel, Field
RouteName = Literal["MENTAL_DISCOMFORT","ADDICTION","FEAR","GENERAL_EMOTIONAL_SUPPORT","INFORMATION_REQUEST","CRISIS","UNKNOWN"]
class SafetyAssessment(BaseModel):
    level: Literal["low","moderate","high","crisis"] = "low"
    self_harm: bool = False
    harm_to_others: bool = False
    overdose_or_dangerous_withdrawal: bool = False
    rationale: str = ""
class RouteDecision(BaseModel):
    route: RouteName = "GENERAL_EMOTIONAL_SUPPORT"
    rationale: str = ""
class RAGSource(BaseModel):
    filename: str
    chunk_id: int
    score: float = 0.0
