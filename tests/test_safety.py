import pytest
from devbuddy.safety import *
def test_validate_safe_path(tmp_path):assert validate_safe_path(tmp_path,"folder/file")==tmp_path.resolve()/"folder/file"
def test_path_traversal_blocked(tmp_path):
 with pytest.raises(UnsafePathError):resolve_safe_path(tmp_path,"../escape")
def test_validate_project_name_valid():assert validate_project_name("good_project-12")
def test_validate_project_name_invalid():assert not validate_project_name("../bad")
def test_safe_write_requires_confirmation(tmp_path):
 p=tmp_path/"a";p.write_text("old")
 with pytest.raises(FileExistsSafetyError):safe_write(p,"new",input_fn=lambda _:"n")
 assert p.read_text()=="old"
