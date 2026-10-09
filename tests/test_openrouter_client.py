from types import SimpleNamespace
import httpx,pytest
from devbuddy.ai.openrouter_client import *
def cfg(key="secret-key"):return SimpleNamespace(openrouter_api_key=key,openrouter_model="test",openrouter_site_url="https://example.test",openrouter_app_name="DevBuddy",request_timeout_seconds=1,max_retries=0)
def test_successful_response(monkeypatch):
 class R:
  status_code=200
  def json(self):return {"choices":[{"message":{"content":"hello"}}],"model":"test","usage":{"total_tokens":2}}
 monkeypatch.setattr("devbuddy.ai.openrouter_client.httpx.post",lambda *a,**k:R())
 r=OpenRouterClient(cfg()).chat_completion([{"role":"user","content":"hi"}]);assert r.content=="hello" and r.usage["total_tokens"]==2
def test_auth_error_raises_AIAuthError(monkeypatch):
 class R:status_code=401
 monkeypatch.setattr("devbuddy.ai.openrouter_client.httpx.post",lambda *a,**k:R())
 with pytest.raises(AIAuthError):OpenRouterClient(cfg()).chat_completion([])
def test_rate_limit_raises_AIRateLimitError(monkeypatch):
 class R:status_code=429
 monkeypatch.setattr("devbuddy.ai.openrouter_client.httpx.post",lambda *a,**k:R())
 with pytest.raises(AIRateLimitError):OpenRouterClient(cfg()).chat_completion([])
def test_network_error_raises_AINetworkError(monkeypatch):
 monkeypatch.setattr("devbuddy.ai.openrouter_client.httpx.post",lambda *a,**k:(_ for _ in ()).throw(httpx.ConnectError("secret-key leaked")))
 with pytest.raises(AINetworkError) as e:OpenRouterClient(cfg()).chat_completion([])
 assert "secret-key" not in str(e.value)
def test_api_key_not_in_exception_message(monkeypatch):
 class R:status_code=401
 monkeypatch.setattr("devbuddy.ai.openrouter_client.httpx.post",lambda *a,**k:R())
 with pytest.raises(AIAuthError) as e:OpenRouterClient(cfg()).chat_completion([])
 assert "secret-key" not in str(e.value)
