"""Validation for untrusted AI-generated plans."""
from dataclasses import dataclass,field
@dataclass
class AIIntentResponse:
    interpretation: str
    action_ids: list[str]=field(default_factory=list)
    parameters: dict=field(default_factory=dict)
    execution_order: list[str]=field(default_factory=list)
    confidence: float=0.0
    clarification_questions: list[str]=field(default_factory=list)
    explanation: str=""
def validate_ai_response(data: dict) -> AIIntentResponse:
    if not isinstance(data,dict): raise ValueError("AI response must be a JSON object")
    # Accept both compact modern schema and legacy selected_actions structure.
    selected=data.get("selected_actions",[])
    if selected and not data.get("action_ids"):
        selected=sorted(selected,key=lambda x:x.get("order",0))
        ids=[x.get("action_id") for x in selected]; params={x.get("action_id"):x.get("parameters",{}) for x in selected}
        order=ids
    else:
        ids=data.get("action_ids",[]);params=data.get("parameters",{});order=data.get("execution_order",ids)
    interpretation=data.get("interpretation"); confidence=data.get("confidence")
    questions=data.get("clarification_questions",[]); explanation=data.get("explanation","")
    if not isinstance(interpretation,str) or not isinstance(ids,list) or not all(isinstance(x,str) for x in ids): raise ValueError("Invalid interpretation or action_ids")
    if not isinstance(params,dict) or not isinstance(order,list) or not all(isinstance(x,str) for x in order): raise ValueError("Invalid parameters or execution_order")
    if not isinstance(confidence,(int,float)) or isinstance(confidence,bool) or not 0<=confidence<=1: raise ValueError("confidence must be between 0 and 1")
    if not isinstance(questions,list) or not all(isinstance(x,str) for x in questions): raise ValueError("clarification_questions must be strings")
    if not isinstance(explanation,str): raise ValueError("explanation must be a string")
    return AIIntentResponse(interpretation,ids,params,order,float(confidence),questions,explanation)
PLAN_SCHEMA={"type":"object","required":["interpretation","action_ids","parameters","execution_order","confidence","clarification_questions","explanation"]}
def validate_ai_plan_response(raw):
    try:return True,[],validate_ai_response(raw)
    except ValueError as e:return False,[str(e)],{}
