import pytest
from devbuddy.action_registry import ActionDefinition,ActionParameter,ActionRegistry
from devbuddy.safety import RiskLevel
def action():return ActionDefinition("a","Action","Description",["example"],[ActionParameter("name",required=True)],RiskLevel.LOW,False,lambda p,c:None)
def test_register_action():
 r=ActionRegistry();r.register(action());assert len(r.list_all())==1
def test_get_action_by_id():
 r=ActionRegistry();a=action();r.register(a);assert r.get("a") is a;assert r.find_by_id("a") is a
def test_list_all_actions():
 r=ActionRegistry();r.register(action());assert r.list_all()[0].id=="a"
def test_duplicate_registration_raises():
 r=ActionRegistry();r.register(action())
 with pytest.raises(ValueError):r.register(action())
def test_to_prompt_description():
 r=ActionRegistry();r.register(action());assert '"id": "a"' in r.to_prompt_description()
