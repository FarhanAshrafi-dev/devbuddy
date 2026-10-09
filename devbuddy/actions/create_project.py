"""Create safe Python starter projects."""
from pathlib import Path
from ..safety import resolve_safe_path,validate_project_name,confirm_action
from ..action_registry import ActionDefinition,ActionParameter,ActionResult,ExecutionContext
from ..safety import RiskLevel
TEMPLATES={"minimal":{"main.py":"def main():\n    print('Hello from your new project!')\n\nif __name__ == '__main__':\n    main()\n"},"cli":{"main.py":"import argparse\n\ndef main():\n    parser = argparse.ArgumentParser(description='A small command-line application')\n    parser.parse_args()\n    print('Welcome!')\n\nif __name__ == '__main__':\n    main()\n"},"tkinter":{"main.py":"import tkinter as tk\n\nroot = tk.Tk()\nroot.title('My Application')\ntk.Label(root, text='Hello, Tkinter!').pack(padx=24, pady=24)\nroot.mainloop()\n"}}
GITIGNORE="__pycache__/\n*.py[cod]\n.venv/\nvenv/\n.env\n.pytest_cache/\ndist/\nbuild/\n"
class CreateProjectAction:
    def run(self, project_name, target_dir=".", template="minimal", description="", context=None):
        ctx=context or ExecutionContext(); base=Path(ctx.base_dir).resolve(); dest=resolve_safe_path(base,Path(target_dir)/project_name)
        if not validate_project_name(project_name): return ActionResult(False,"Invalid project name; use letters, numbers, hyphens, and underscores.")
        if template not in TEMPLATES:return ActionResult(False,"Unknown template.")
        if dest.exists():
            if not confirm_action(f"Project directory exists. Overwrite files? {dest}",ctx.auto_confirm,ctx.input_fn):return ActionResult(False,"Cancelled; existing files were not changed.")
        dest.mkdir(parents=True,exist_ok=True)
        readme=f"# {project_name}\n\n{description or 'A Python project.'}\n\n## Run\n\n```bash\npython main.py\n```\n"
        contents={**TEMPLATES[template],"README.md":readme,".gitignore":GITIGNORE}
        written=[]
        for name,text in contents.items():
            target=dest/name
            if target.exists() and not ctx.auto_confirm and not confirm_action(f"Overwrite {target}?",input_fn=ctx.input_fn): continue
            target.write_text(text,encoding="utf-8");written.append(str(target))
        return ActionResult(True,f"Created {template} project at {dest}",created_files=written,data={"path":str(dest)})
def definition():
    action=CreateProjectAction()
    return ActionDefinition("create_project","Create Python project","Generate a minimal, CLI, or Tkinter starter project.",["Create a Python project","Start a new CLI app"],[ActionParameter("project_name",required=True),ActionParameter("target_dir",description="Parent directory",default="."),ActionParameter("template",choices=list(TEMPLATES),default="minimal"),ActionParameter("description")],RiskLevel.MEDIUM,True,lambda params,context: action.run(**params,context=context))
