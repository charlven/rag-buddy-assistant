---
name: tester
description: "Run pre-push verification for API/UI availability and Python syntax integrity."
user-invocable: true
---

# Tester Skill

Use this skill before commit/push to verify the feature is working.

## Verification checklist

1. Run syntax checks:
   - `python -m compileall app scripts`
2. Start API server.
3. Verify:
   - `GET /health`
   - `GET /ui`
   - `GET /v1/models`
4. Stop the server cleanly.

## Pass criteria

- Compile step completes without Python syntax errors.
- `/health` returns status payload.
- `/ui` returns HTML content.
- `/v1/models` returns JSON list with at least one model id.
