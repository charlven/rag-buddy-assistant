# Contributing to RAG Buddy Assistant

Thanks for contributing to **RAG Buddy Assistant**.

## Development setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Pull request guidelines

1. Keep changes focused and scoped to one topic.
2. Update documentation for behavior/config/API changes.
3. Preserve OpenAI-compatible API behavior for `/v1/models` and `/v1/chat/completions`.
4. Avoid breaking ingestion and retrieval flows unless intentionally changing behavior.

## Coding guidelines

- Follow existing project structure and naming.
- Prefer clear, explicit error messages.
- Avoid unrelated refactors in feature/bugfix PRs.

## Before opening a PR

1. Ensure the backend starts successfully.
2. Verify health endpoint: `GET /health`.
3. Verify chat endpoint behavior for both:
   - `stream=false`
   - `stream=true`
4. Verify Open WebUI integration still works with:
   - `http://host.docker.internal:8000/v1` (Docker frontend -> host backend)

## Reporting issues

Please include:

- What you expected vs what happened
- Steps to reproduce
- Relevant logs
- Environment details (OS, Python version, provider/model config)
