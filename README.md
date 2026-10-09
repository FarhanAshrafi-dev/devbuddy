# DevBuddy 🐍

DevBuddy is a terminal-based developer helper for creating starter Python projects, drafting documentation, checking code without running it, planning safe file organization, explaining errors, and producing coding-agent prompts. AI planning uses OpenRouter only; deterministic offline features work without credentials.

## Features
- Explicit registry: AI can select only registered Python actions; it cannot run generated shell commands or code.
- Minimal, CLI, and Tkinter project templates.
- Read-only syntax and documentation checks using `ast.parse`.
- Preview-first file organization and documentation generation.
- Traceback explanations and structured coding-agent prompt generation.
- Confirmation and path traversal protections.

## Screenshots
Screenshots are planned; none are included yet.

## Requirements and installation
Python 3.11+ is required. From PowerShell in the repository directory:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python -m devbuddy
```

Or install dependencies with `python -m pip install httpx python-dotenv rich pydantic`.

## OpenRouter setup
Set `OPENROUTER_API_KEY` in your local `.env` file. Never commit it. Optionally set `OPENROUTER_SITE_URL` and `OPENROUTER_APP_NAME`. The default model setting is configurable by `OPENROUTER_MODEL`; select a currently listed free model in your OpenRouter account/model catalog and put its exact model ID there. Model availability, rate limits, and uptime are not guaranteed. DevBuddy does not silently switch to a paid model. `AI_TIMEOUT` and `AI_MAX_RETRIES` configure bounded requests/retries (maximum two retries).

Without a key, the CLI explicitly works in offline mode.

## Usage
Run `python -m devbuddy` or, after editable installation, `devbuddy`. Try natural requests such as “create a Python project”, “check project”, “explain this error”, or “organize files”. Use `help`, `menu`, `status`, `cancel`, and `exit`. Confirmations are requested before write/move operations. Available templates are `minimal`, `cli`, and `tkinter`.

## Security model and limitations
AI is a planner, not a security boundary. Registry membership, parameter validation, path resolution, and confirmations are enforced by Python. The project checker never runs project code. Organizing only proposes moves for top-level visible files and never deletes or overwrites. AI-dependent explanations/planning require OpenRouter; offline keyword routing is deliberately basic. README and project actions use truthful template text rather than claiming unverified project features.

## Tests
Run `python -m pytest tests/ -v`. Tests mock HTTP calls and require neither API credentials nor network access.

## Contributing
Contributions are welcome. Please add focused tests, preserve the explicit-action security model, avoid logging secrets, and document behavior changes.

## License
MIT; see [LICENSE](LICENSE).
