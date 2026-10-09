"""Explain Python errors without changing code."""
import re
from ..action_registry import ActionDefinition,ActionParameter,ActionResult
from ..safety import RiskLevel
class ExplainErrorAction:
 def __init__(self,ai_client=None):self.ai_client=ai_client
 def run(self,traceback,context=None):
  if self.ai_client:
   try:
    response=self.ai_client.chat_completion([{"role":"system","content":"Explain Python errors clearly for beginners. Never propose automatic code execution."},{"role":"user","content":traceback}]);return ActionResult(True,response.content)
   except Exception:pass
  patterns=[(r"ModuleNotFoundError|ImportError","Python could not import a module. Check its name and install/setup instructions."),(r"FileNotFoundError","A requested file or directory was not found. Verify the path and working directory."),(r"SyntaxError","The source has invalid Python syntax. Inspect the reported line, quotes, brackets, and indentation."),(r"NameError","A name is used before it is defined or is misspelled."),(r"TypeError","An operation received a value of an incompatible type; inspect the types at the traceback line."),(r"KeyError","A dictionary key was not present; verify the key or use a safe lookup."),(r"IndexError","A sequence index is outside its available range.")]
  explanation=next((msg for pat,msg in patterns if re.search(pat,traceback)),"I cannot determine the exact cause from this text alone. Read the final exception line and inspect the indicated traceback location.")
  return ActionResult(True,"Likely explanation (offline; not a diagnosis): "+explanation+" No code was edited.")
def definition():
 a=ExplainErrorAction();return ActionDefinition("explain_error","Explain Python error","Explain a traceback with beginner-friendly suggestions; no code edits.",["Explain this traceback","What does this error mean?"],[ActionParameter("traceback",required=True)],RiskLevel.LOW,False,lambda params,context:a.run(**params,context=context))
