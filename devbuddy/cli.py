"""Rich terminal CLI."""
try:
 from rich.console import Console
 from rich.panel import Panel
except ImportError: Console=None;Panel=None
console=Console() if Console else None
def _print(text,style=None):
 if console:console.print(text,style=style)
 else:print(text)
def print_welcome():_print(Panel("DevBuddy 🐍\nYour friendly developer assistant",border_style="cyan") if console else "DevBuddy 🐍 — your friendly developer assistant","cyan")
def print_error(message):_print(message,"red")
def print_success(message):_print(message,"cyan")
def print_plan(actions):_print("Plan: "+", ".join(map(str,actions)),"cyan")
def print_result(result):_print(result,"bright_black")
def prompt_user(message="What would you like to build or improve today?"):
 return console.input(f"[cyan]{message}[/cyan] ") if console else input(message+" ")
def confirm_action(message):
 answer=prompt_user(message+" [y/N]");return answer.strip().lower() in ("y","yes")
def main():
 from .config import load_settings,is_ai_configured
 from .action_registry import build_default_registry
 from .ai.openrouter_client import OpenRouterClient
 from .intent_router import IntentRouter
 from .conversation import ConversationManager
 settings=load_settings();registry=build_default_registry();client=OpenRouterClient(settings) if is_ai_configured(settings) else None
 print_welcome()
 if not client:_print("OpenRouter is not configured. Working in deterministic offline mode.","bright_black")
 ConversationManager(IntentRouter(registry,client,settings),registry,settings,cli=console).start()
