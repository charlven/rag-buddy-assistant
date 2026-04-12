# LangChain RAG Backend (for Open WebUI frontend)

This starter gives you a custom RAG backend for:
- Personal data indexing (`personal` namespace)
- Source code indexing (`code` namespace)
- Chat answering with retrieval context

You can use Open WebUI as frontend and point it to this backend via OpenAI-compatible API endpoint.

## 1) Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Recommended Python: **3.11 or 3.12** for the broadest package compatibility.

Edit `.env` and set your `OPENAI_API_KEY`.

## 2) Start API

```powershell
uvicorn app.main:app --reload --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## 3) Ingest your data

### Index personal docs

```powershell
python .\scripts\index_data.py --data-path "D:\my_personal_docs" --namespace personal --reset-namespace
```

### Index source code

```powershell
python .\scripts\index_data.py --data-path "D:\my_source_code" --namespace code --reset-namespace
```

Optional: choose file types

```powershell
python .\scripts\index_data.py --data-path "D:\my_source_code" --namespace code --extensions .py .ts .md
```

## 4) Chat directly with backend

```powershell
$body = @{
  question = "Summarize my current project architecture"
  namespaces = @("personal", "code")
  chat_history = @()
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/chat" -ContentType "application/json" -Body $body
```

## 5) Connect Open WebUI

In Open WebUI:
1. Add an **OpenAI-compatible connection**.
2. Set base URL to your backend:
   - `http://host.docker.internal:8000/v1` (if Open WebUI runs in Docker and backend runs on host)
   - `http://localhost:8000/v1` (if both run on same host network)
3. API key can be any placeholder unless your Open WebUI requires a non-empty token.
4. Use non-streaming mode (`stream=false`) in this starter backend.

### OpenAI-compatible request supported

- `POST /v1/chat/completions`
- Expects `messages`
- Accepts optional `namespaces` field: `["personal"]`, `["code"]`, or both

## Notes

- Vector store is local Chroma at `./data/chroma`.
- This starter currently uses OpenAI for both embeddings and chat model.
- Add auth, audit logging, and PII controls before production use.
