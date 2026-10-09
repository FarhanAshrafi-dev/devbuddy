"""Environment-backed application settings."""
from dataclasses import dataclass
import os
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args,**kwargs): return False
@dataclass
class Settings:
    openrouter_api_key: str = ""
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct:free"
    openrouter_site_url: str = ""
    openrouter_app_name: str = "DevBuddy"
    request_timeout_seconds: float = 30.0
    max_retries: int = 2
    @property
    def ai_timeout(self): return self.request_timeout_seconds
    @property
    def ai_max_retries(self): return self.max_retries
def load_settings() -> Settings:
    load_dotenv()
    return Settings(os.getenv("OPENROUTER_API_KEY", ""),os.getenv("OPENROUTER_MODEL") or "meta-llama/llama-3.1-8b-instruct:free",os.getenv("OPENROUTER_SITE_URL", ""),os.getenv("OPENROUTER_APP_NAME") or "DevBuddy",float(os.getenv("AI_TIMEOUT", "30")),max(0,min(2,int(os.getenv("AI_MAX_RETRIES", "2")))))
def is_ai_configured(settings: Settings) -> bool: return bool(settings.openrouter_api_key.strip())
