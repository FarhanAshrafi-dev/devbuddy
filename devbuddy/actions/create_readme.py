"""Preview and create a project README."""
from pathlib import Path
from ..safety import resolve_safe_path,confirm_action,RiskLevel
from ..action_registry import ActionDefinition,ActionParameter,ActionResult
class CreateReadmeAction:
    def __init__(self,ai_client=None):self.ai_client=ai_client
    def run(self,project_name,description,project_dir=".",features=None,context=None):
        from ..action_registry import ExecutionContext
        ctx=context or ExecutionContext();root=resolve_safe_path(ctx.base_dir,project_dir);path=root/"README.md"
        features=features or []; feature_md="\n".join(f"- {f}" for f in features) or "- Not specified"
        text=f"# {project_name}\n\n## Overview\n{description}\n\n## Features\n{feature_md}\n\n## Requirements\nPython 3.11+\n\n## Installation\nClone the repository and install documented dependencies.\n\n## Usage\nSee the project entry point and run instructions.\n\n## Configuration\nNo configuration specified.\n\n## License\nMIT (update if different).\n"
        if ctx.output_fn:ctx.output_fn(text)
        if path.exists() and not confirm_action(f"Overwrite {path}?",ctx.auto_confirm,ctx.input_fn):return ActionResult(False,"Cancelled; README was not changed.")
        root.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding="utf-8");return ActionResult(True,"README created.",created_files=[str(path)])
def definition():
 a=CreateReadmeAction();return ActionDefinition("create_readme","Create README","Generate a factual README with standard sections.",["Write a README","Create project documentation"],[ActionParameter("project_name",required=True),ActionParameter("description",required=True),ActionParameter("project_dir",default="."),ActionParameter("features",type="list",default=[])],RiskLevel.MEDIUM,True,lambda params,context:a.run(**params,context=context))
