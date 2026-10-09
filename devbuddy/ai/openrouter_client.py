"""Small, secret-safe OpenRouter Chat Completions client."""
from dataclasses import dataclass,field
import time
try: import httpx
except ImportError: httpx=None
ENDPOINT="https://openrouter.ai/api/v1/chat/completions"
class AIError(RuntimeError): pass
class AIAuthError(AIError): pass
class AIRateLimitError(AIError): pass
class AIModelUnavailableError(AIError): pass
class AINetworkError(AIError): pass
class AIResponseError(AIError): pass
@dataclass
class AIResponse:
    content: str
    model: str=""
    usage: dict=field(default_factory=dict)
    error: str|None=None
class OpenRouterClient:
    def __init__(self,config): self.config=config
    def chat_completion(self,messages, *, temperature=0.2, response_format=None):
        if not getattr(self.config,"openrouter_api_key",""): raise AIAuthError("OpenRouter API key is not configured")
        if httpx is None: raise AINetworkError("httpx is not installed")
        headers={"Authorization":f"Bearer {self.config.openrouter_api_key}","Content-Type":"application/json","X-Title":getattr(self.config,"openrouter_app_name","DevBuddy")}
        site=getattr(self.config,"openrouter_site_url","")
        if site: headers["HTTP-Referer"]=site
        payload={"model":self.config.openrouter_model,"messages":messages,"temperature":temperature}
        if response_format: payload["response_format"]=response_format
        retries=max(0,min(2,int(getattr(self.config,"max_retries",2))))
        for attempt in range(retries+1):
            try:
                response=httpx.post(ENDPOINT,headers=headers,json=payload,timeout=getattr(self.config,"request_timeout_seconds",30))
                status=response.status_code
                if status in (401,403): raise AIAuthError("OpenRouter authentication failed; check credentials")
                if status==429: raise AIRateLimitError("OpenRouter rate limit reached")
                if status in (404,422): raise AIModelUnavailableError("Configured OpenRouter model is unavailable or unsupported")
                if status>=500:
                    if attempt<retries: time.sleep(min(.2*(attempt+1),.5)); continue
                    raise AINetworkError(f"OpenRouter service returned HTTP {status}")
                if status>=400: raise AIResponseError(f"OpenRouter request failed (HTTP {status})")
                try: data=response.json(); content=data["choices"][0]["message"]["content"]
                except (ValueError,KeyError,IndexError,TypeError) as exc: raise AIResponseError("OpenRouter returned an invalid response") from None
                if not isinstance(content,str): raise AIResponseError("OpenRouter response content was not text")
                return AIResponse(content,data.get("model",self.config.openrouter_model),data.get("usage",{}))
            except (AIAuthError,AIRateLimitError,AIModelUnavailableError,AIResponseError): raise
            except Exception as exc:
                # Do not re-raise transport exceptions: they may embed request headers/secrets.
                if attempt<retries: time.sleep(min(.2*(attempt+1),.5)); continue
                raise AINetworkError("Unable to reach OpenRouter") from None
    def complete(self,messages,**kwargs): return self.chat_completion(messages,**kwargs)
