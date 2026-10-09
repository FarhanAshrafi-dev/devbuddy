import json,pytest
from devbuddy.intent_router import IntentRouter
from devbuddy.action_registry import ActionRegistry,ActionDefinition
from devbuddy.safety import RiskLevel
def registry():
 r=ActionRegistry();r.register(ActionDefinition("create_project","Create","Create project",["create a Python project"],[],RiskLevel.MEDIUM,True,lambda p,c:None));return r
def test_offline_fallback_create_project():
 x=IntentRouter(registry()).route("create a Python project");assert x.matched_actions==["create_project"] and not x.used_ai
def test_offline_fallback_unknown():assert not IntentRouter(registry()).route("tell me a joke").matched_actions
def test_parse_valid_ai_response():
 r=IntentRouter(registry());parsed=r._parse_ai_response(json.dumps(dict(interpretation="create",action_ids=["create_project"],parameters={},execution_order=["create_project"],confidence=.9,clarification_questions=[],explanation="ok")));assert parsed.confidence==.9
def test_parse_invalid_ai_response():
 with pytest.raises(ValueError):IntentRouter(registry())._parse_ai_response("not json")
