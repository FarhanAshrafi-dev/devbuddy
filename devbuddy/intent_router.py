
"""AI-assisted planning constrained to registered action IDs."""

import json
import re
from dataclasses import dataclass, field

from .ai.schemas import AIIntentResponse, validate_ai_response


@dataclass
class RoutingResult:
    matched_actions: list = field(default_factory=list)
    parameters: dict = field(default_factory=dict)
    confidence: float = 0.0
    clarification_questions: list = field(default_factory=list)
    explanation: str = ""
    used_ai: bool = False
    interpretation: str = ""


class IntentRouter:
    def __init__(self, registry, ai_client=None, config=None):
        self.registry = registry
        self.ai_client = ai_client
        self.config = config

    def _build_prompt(self, user_input):
        return (
            "Choose only registered actions and return JSON with interpretation, "
            "action_ids, parameters (keyed by action id), execution_order, "
            "confidence, clarification_questions, explanation. "
            "Extract explicit parameter values from the user's request. "
            "Actions:\n"
            + self.registry.to_prompt_description()
            + "\nUser request: "
            + user_input
        )

    def _parse_ai_response(self, response_text):
        try:
            data = json.loads(response_text)
        except (ValueError, TypeError) as exc:
            raise ValueError("AI response must contain valid JSON") from exc
        return validate_ai_response(data)

    def route(self, user_input):
        if (
            self.ai_client
            and self.config
            and getattr(self.config, "openrouter_api_key", "")
        ):
            try:
                response = self.ai_client.chat_completion(
                    [
                        {
                            "role": "system",
                            "content": (
                                "Plan using registered actions only. Return JSON, "
                                "never code. Extract explicit parameter values."
                            ),
                        },
                        {
                            "role": "user",
                            "content": self._build_prompt(user_input),
                        },
                    ],
                    response_format={"type": "json_object"},
                )
                parsed = self._parse_ai_response(response.content)

                if any(
                    self.registry.get(action_id) is None
                    for action_id in parsed.action_ids
                ):
                    raise ValueError("Unregistered action in AI plan")

                ids = parsed.execution_order or parsed.action_ids
                if set(ids) != set(parsed.action_ids):
                    raise ValueError("Invalid execution order")

                return RoutingResult(
                    ids,
                    parsed.parameters,
                    parsed.confidence,
                    parsed.clarification_questions,
                    parsed.explanation,
                    True,
                    parsed.interpretation,
                )
            except Exception as exc:
                return self._offline_fallback(
                    user_input,
                    reason=(
                        "AI unavailable; using offline matching "
                        f"({type(exc).__name__})."
                    ),
                )

        return self._offline_fallback(
            user_input, reason="Offline mode: AI is not configured."
        )

    def _offline_fallback(self, user_input, reason="Offline mode."):
        text = user_input.strip()
        lowered = text.lower()

        keywords = {
            "create_project": [
                "create project",
                "new project",
                "make project",
                "python project",
                "create a project",
                "create a python project",
                "start a new project",
            ],
            "create_readme": ["readme", "write documentation"],
            "check_project": ["check project", "inspect project", "syntax check"],
            "organize_files": ["organize files", "整理"],
            "explain_error": [
                "traceback",
                "explain error",
                "error message",
                "exception",
            ],
        }

        found = []
        parameters = {}

        for action in self.registry.list_all():
            terms = keywords.get(action.action_id, []) + [
                example.lower() for example in action.example_requests
            ]

            if not any(term in lowered for term in terms):
                continue

            found.append(action.action_id)
            action_params = {}

            if action.action_id == "create_project":
                # Accept: create project mmd
                # Accept: create a Python project named mmd
                patterns = [
                    r"\b(?:create|make|new|start)\s+(?:a\s+)?(?:python\s+)?project\s+(?:named\s+|called\s+)?([A-Za-z0-9_-]+)\b",
                    r"\bproject\s+(?:named\s+|called\s+)([A-Za-z0-9_-]+)\b",
                    r"\b(?:named|called)\s+([A-Za-z0-9_-]+)\b",
                ]

                project_name = None
                for pattern in patterns:
                    match = re.search(pattern, text, flags=re.IGNORECASE)
                    if match:
                        candidate = match.group(1)
                        if candidate.lower() not in {
                            "a", "the", "python", "project"
                        }:
                            project_name = candidate
                            break

                if project_name:
                    action_params["project_name"] = project_name

                # Only use template names that are explicitly mentioned.
                template_match = re.search(
                    r"\b(minimal|cli|tkinter)\b",
                    lowered,
                )
                if template_match:
                    action_params["template"] = template_match.group(1)

            parameters[action.action_id] = action_params

        if not found:
            return RoutingResult(
                clarification_questions=[
                    "I could not match that request. Which available action would you like?"
                ],
                explanation=(
                    reason + " Use 'menu' to see available actions."
                ),
                interpretation=text,
            )

        questions = []
        for action_id in found:
            action = self.registry.get(action_id)
            supplied = parameters.get(action_id, {})

            for parameter in action.parameters:
                if (
                    parameter.required
                    and parameter.name not in supplied
                    and parameter.default is None
                ):
                    questions.append(
                        f"What is the {parameter.name.replace('_', ' ')} "
                        f"for {action.name}?"
                    )

        return RoutingResult(
            matched_actions=found,
            parameters=parameters,
            confidence=0.7,
            clarification_questions=questions,
            explanation=(
                reason + " Matched by deterministic keywords."
            ),
            used_ai=False,
            interpretation=text,
        )