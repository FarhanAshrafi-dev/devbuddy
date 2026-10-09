"""Registry of explicitly permitted actions."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
from .safety import RiskLevel


@dataclass
class ActionParameter:
    name: str
    type: str = "string"
    required: bool = False
    description: str = ""
    choices: list | None = None
    default: Any = None


@dataclass
class ActionResult:
    success: bool
    message: str
    data: dict = field(default_factory=dict)
    created_files: list = field(default_factory=list)
    modified_files: list = field(default_factory=list)


@dataclass
class ExecutionContext:
    base_dir: Path = field(default_factory=Path.cwd)
    auto_confirm: bool = False
    input_fn: Callable = input
    output_fn: Callable = print
    extra: dict = field(default_factory=dict)


@dataclass
class ActionDefinition:
    action_id: str
    name: str
    description: str
    example_requests: list
    parameters: list
    risk_level: RiskLevel
    confirmation_required: bool
    executor: Callable

    @property
    def id(self):
        return self.action_id

    @property
    def examples(self):
        return self.example_requests

    @property
    def parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                p.name: {
                    "type": p.type,
                    "description": p.description,
                    **({"enum": p.choices} if p.choices else {}),
                }
                for p in self.parameters
            },
            "required": [p.name for p in self.parameters if p.required],
        }

    @property
    def handler(self):
        return self.executor


class ActionRegistry:
    def __init__(self):
        self._actions = {}

    def register(self, action: ActionDefinition):
        if action.action_id in self._actions:
            raise ValueError("Duplicate action: " + action.action_id)
        self._actions[action.action_id] = action

    def get(self, action_id):
        return self._actions.get(action_id)

    def find_by_id(self, action_id):
        return self.get(action_id)

    def list_actions(self):
        return list(self._actions.values())

    def list_all(self):
        return self.list_actions()

    def to_ai_catalog(self):
        return [
            dict(
                id=a.action_id,
                name=a.name,
                description=a.description,
                examples=a.example_requests,
                risk=a.risk_level.value,
                parameters=[
                    dict(
                        name=p.name,
                        type=p.type,
                        required=p.required,
                        description=p.description,
                        choices=p.choices,
                        default=p.default,
                    )
                    for p in a.parameters
                ],
            )
            for a in self.list_actions()
        ]

    def to_prompt_description(self):
        import json
        return json.dumps(self.to_ai_catalog(), indent=2, ensure_ascii=False)

    def validate_params(self, action_id, params):
        action = self.get(action_id)
        if not action:
            return False, ["Unknown action: " + action_id], {}
        if not isinstance(params, dict):
            return False, ["parameters must be an object"], {}

        errors = []
        cleaned = {}
        types = {
            "string": str,
            "int": int,
            "bool": bool,
            "path": (str, Path),
            "choice": str,
            "list": list,
            "number": (int, float),
        }

        for p in action.parameters:
            value = params.get(p.name, p.default)
            if value is None:
                if p.required:
                    errors.append("Missing required parameter: " + p.name)
                continue
            expected = types.get(p.type, str)
            if not isinstance(value, expected) or (p.type == "int" and isinstance(value, bool)):
                errors.append(f"{p.name} must be {p.type}")
                continue
            if p.choices is not None and value not in p.choices:
                errors.append(f"Invalid choice for {p.name}")
                continue
            cleaned[p.name] = Path(value) if p.type == "path" else value

        extras = set(params) - {p.name for p in action.parameters}
        if extras:
            errors.append("Unexpected parameters: " + ", ".join(sorted(extras)))

        return not errors, errors, cleaned


def build_default_registry() -> ActionRegistry:
    """Import all action modules and register their definitions."""
    from .actions.create_project import definition as create_project_def
    from .actions.create_readme import definition as create_readme_def
    from .actions.check_project import definition as check_project_def
    from .actions.organize_files import definition as organize_files_def
    from .actions.explain_error import definition as explain_error_def

    registry = ActionRegistry()
    for def_fn in (
        create_project_def,
        create_readme_def,
        check_project_def,
        organize_files_def,
        explain_error_def,
    ):
        registry.register(def_fn())

    return registry
