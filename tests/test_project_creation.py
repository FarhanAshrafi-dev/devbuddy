from devbuddy.actions.create_project import CreateProjectAction
from devbuddy.action_registry import ExecutionContext
def test_create_minimal_project(tmp_path):
 r=CreateProjectAction().run("demo",template="minimal",context=ExecutionContext(tmp_path));assert r.success and (tmp_path/"demo"/"main.py").exists()
def test_create_cli_project(tmp_path):
 r=CreateProjectAction().run("cliapp",template="cli",context=ExecutionContext(tmp_path));assert r.success and "argparse" in (tmp_path/"cliapp"/"main.py").read_text()
def test_creates_gitignore(tmp_path):
 CreateProjectAction().run("sample",context=ExecutionContext(tmp_path));assert (tmp_path/"sample"/".gitignore").exists()
def test_does_not_overwrite_without_confirmation(tmp_path):
 d=tmp_path/"exists";d.mkdir();(d/"keep").write_text("yes")
 ctx=ExecutionContext(tmp_path,auto_confirm=False,input_fn=lambda _:"n")
 result=CreateProjectAction().run("exists",context=ctx);assert not result.success and (d/"keep").read_text()=="yes"
