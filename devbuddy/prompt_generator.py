
"""Structured coding-agent prompt generation."""

from pathlib import Path


class PromptGenerator:
    def generate(self, project_description, answers=None, context=None):
        answers = answers or {}
        context = context or {}

        def show(value):
            if isinstance(value, (list, tuple)):
                return "\n".join(f"- {item}" for item in value) or "- None specified"
            return str(value) if value else "Not specified"

        confirmed_requirements = show(
            [
                f"{key.replace('_', ' ').title()}: {value}"
                for key, value in answers.items()
            ]
        )

        return f"""# Coding Agent Prompt

## Objective
{project_description}

## Confirmed requirements
{confirmed_requirements}

## Assumptions and open questions
Clearly identify unknowns; do not invent requirements. Ask targeted questions if essential.

## Intended behavior and features
{show(answers.get('features', []))}

## Technical stack and platform
- Stack: {answers.get('stack', 'Python 3.11+')}
- Platform: {answers.get('platform', 'Windows 11; cross-platform where practical')}

## Existing project context
{show(context)}

## File structure and expected modules
Inspect the workspace first, preserve unrelated user data, and propose a clear modular structure before changes.

## Dependencies, configuration, and API integration
Use only necessary dependencies. Document environment configuration; never commit secrets. Implement only explicitly requested provider integrations.

## Security constraints
Validate inputs and paths, protect credentials, and never execute arbitrary generated commands or code.

## Acceptance criteria
Implement confirmed requirements, document limitations, and do not claim features or tests that are unverified.

## Testing requirements
Add meaningful automated tests and run them; report actual results.

## Installation and execution
Provide reproducible setup and run instructions for the target platform.

Inspect the workspace before editing. Implement the solution rather than merely describing it, and summarize changed files and verification results.
"""

    def _ask_followup_questions(self, project_description):
        if project_description.strip():
            return {"questions": []}
        return {"questions": ["What would you like the project to do?"]}

    def save_to_file(self, prompt, path):
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(prompt, encoding="utf-8")
        return target


def generate_agent_prompt(project_info, existing_context=None):
    info = dict(project_info)
    description = info.pop("project_description", "A software project")
    return PromptGenerator().generate(description, info, existing_context)