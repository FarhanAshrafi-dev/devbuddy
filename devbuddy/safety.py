"""Filesystem and confirmation safety primitives."""
from enum import Enum
from pathlib import Path
import os
class UnsafePathError(ValueError): pass
class FileExistsSafetyError(FileExistsError): pass
class RiskLevel(Enum): LOW="low"; MEDIUM="medium"; HIGH="high"
def resolve_safe_path(base_dir: Path, relative_or_abs: str | Path) -> Path:
    base=Path(os.path.realpath(Path(base_dir).expanduser()))
    p=Path(relative_or_abs).expanduser()
    out=Path(os.path.realpath(p if p.is_absolute() else base/p))
    try: out.relative_to(base)
    except ValueError as exc: raise UnsafePathError(f"Path is outside the approved directory: {relative_or_abs}") from exc
    return out
def validate_safe_path(base_dir: Path, path: str | Path) -> Path: return resolve_safe_path(base_dir,path)
def validate_project_name(name: str) -> bool:
    return bool(name and len(name)<=100 and name not in (".","..") and all(c.isalnum() or c in "-_" for c in name))
def confirm_action(prompt: str, auto_yes: bool=False, input_fn=input) -> bool:
    return True if auto_yes else input_fn(prompt+" [y/N] ").strip().lower() in ("y","yes")
def ensure_no_overwrite(path: Path) -> None:
    if Path(path).exists(): raise FileExistsSafetyError(f"Refusing to overwrite existing file: {path}")
def safe_write(path: Path, content: str, *, approved: bool=False, input_fn=input) -> Path:
    path=Path(path)
    if path.exists() and not (approved or confirm_action(f"Overwrite {path}?",input_fn=input_fn)):
        raise FileExistsSafetyError(f"Overwrite not approved: {path}")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content,encoding="utf-8")
    return path
