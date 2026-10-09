"""Read-only project checks; never executes project code."""
import ast
from pathlib import Path
from ..safety import resolve_safe_path,RiskLevel
from ..action_registry import ActionDefinition,ActionParameter,ActionResult,ExecutionContext
class CheckProjectAction:
 def run(self,project_dir=".",context=None):
  ctx=context or ExecutionContext();root=resolve_safe_path(ctx.base_dir,project_dir);findings=[]
  if not root.is_dir():return ActionResult(False,"Project directory does not exist.")
  for name in ("README.md",".gitignore","__init__.py"):
   if not (root/name).exists(): findings.append({"severity":"WARNING","message":f"Missing {name}"})
  for p in root.rglob("*.py"):
   if any(part.startswith(".") or part in (".venv","venv","build","dist") for part in p.relative_to(root).parts):continue
   try:ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
   except (SyntaxError,UnicodeError) as e:findings.append({"severity":"ERROR","message":f"Syntax issue in {p.relative_to(root)}: {e}"})
  if not findings:findings.append({"severity":"INFO","message":"No issues found by basic read-only checks."})
  return ActionResult(True,f"Checked {root}; {len(findings)} finding(s).",data={"findings":findings})
def definition():return ActionDefinition("check_project","Check project","Read-only check for docs, structure, and Python syntax.",["Check my project","Inspect for syntax errors"],[ActionParameter("project_dir",default=".")],RiskLevel.LOW,False,lambda params,context:CheckProjectAction().run(**params,context=context))
