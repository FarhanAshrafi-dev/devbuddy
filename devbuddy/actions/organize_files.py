"""Preview-first conservative file organization."""
from pathlib import Path
import shutil
from ..safety import resolve_safe_path,confirm_action,RiskLevel
from ..action_registry import ActionDefinition,ActionParameter,ActionResult,ExecutionContext
class OrganizeFilesAction:
 EXCLUDED={".env","pyproject.toml","setup.py","setup.cfg","tox.ini","pytest.ini",".gitignore",".editorconfig"}
 def run(self,project_dir=".",context=None):
  ctx=context or ExecutionContext();root=resolve_safe_path(ctx.base_dir,project_dir)
  if not root.is_dir():return ActionResult(False,"Directory not found.")
  moves=[]
  for p in sorted(root.iterdir()):
   if p.name.startswith(".") or p.name in self.EXCLUDED or not p.is_file():continue
   dest="src" if p.suffix==".py" else "docs" if p.suffix.lower() in (".md",".rst",".txt") else "tests" if p.name.startswith("test_") else None
   if dest and p.parent.name!=dest:
    target=root/dest/p.name
    if not target.exists():moves.append((p,target))
  if ctx.output_fn:ctx.output_fn("Proposed moves:\n"+"\n".join(f"{a.relative_to(root)} -> {b.relative_to(root)}" for a,b in moves))
  if not moves:return ActionResult(True,"No safe moves proposed.")
  if not confirm_action("Apply all listed moves?",ctx.auto_confirm,ctx.input_fn):return ActionResult(False,"Cancelled; no files moved.")
  done=[]
  for src,dst in moves:
   # Resolved destination must remain inside the approved root; never overwrite.
   resolve_safe_path(root,dst);dst.parent.mkdir(exist_ok=True)
   if dst.exists():continue
   shutil.move(str(src),str(dst));done.append(str(dst))
  return ActionResult(True,f"Moved {len(done)} file(s).",modified_files=done)
def definition():return ActionDefinition("organize_files","Organize files","Preview and confirm safe moves into src/, docs/, or tests/.",["Organize files in my project"],[ActionParameter("project_dir",default=".")],RiskLevel.MEDIUM,True,lambda params,context:OrganizeFilesAction().run(**params,context=context))
