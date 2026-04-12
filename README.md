# LangChain RAG Backend (for Open WebUI frontend)

This starter gives you a custom RAG backend for:
- Personal data indexing (`personal` namespace)
- Source code indexing (`code` namespace)
- Project-aware source code indexing (project/repository metadata)
- Chat answering with retrieval context and citations

You can use Open WebUI as frontend and point it to this backend via OpenAI-compatible API endpoint.

## 1) Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Recommended Python: **3.11 or 3.12** for the broadest package compatibility.

Edit `.env` and set your model provider values:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=
CHAT_MODEL=gpt-4.1-mini
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_BATCH_SIZE=64
```

For OpenAI, keep `OPENAI_BASE_URL` empty.

For GLM (OpenAI-compatible), set:

```env
OPENAI_API_KEY=your_glm_key
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
CHAT_MODEL=glm-4.5
EMBEDDING_MODEL=embedding-3
EMBEDDING_BATCH_SIZE=64
```

## 2) Start API

```powershell
uvicorn app.main:app --reload --port 8000
or
python -m uvicorn app.main:app --port 8000 *> .\server.log
```

Health check:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Built-in local UI:

```powershell
Start-Process "http://localhost:8000/ui"
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

### Index source code with project/repository identity (recommended)

```powershell
python .\scripts\index_data.py --data-path "D:\repos\order-service" --namespace code --project-id order-service --project-name "Order Service"
python .\scripts\index_data.py --data-path "D:\repos\billing-service" --namespace code --project-id billing-service --project-name "Billing Service"
```

Optional: choose file types

```powershell
python .\scripts\index_data.py --data-path "D:\my_source_code" --namespace code --extensions .py .ts .md
```

Default indexing behavior skips common generated/dependency folders such as `.git`, `node_modules`, `target`, `dist`, `build`, `.venv`, and `__pycache__`.

## 4) Chat directly with backend

```powershell
$body = @{
  question = "Which repository implements order cancellation and what is the request flow?"
  namespaces = @("code")
  project_ids = @("order-service")
  chat_history = @()
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/chat" -ContentType "application/json" -Body $body
```

## 5) Project import APIs (for custom UI/Open WebUI tooling)

Import a code repository:

```powershell
$body = @{
  data_path = "D:\repos\order-service"
  project_id = "order-service"
  project_name = "Order Service"
  recursive = $true
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/projects/import" -ContentType "application/json" -Body $body
```

List imported projects:

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/projects"
```

## 6) Connect Open WebUI

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
- Project registry is stored at `./data/projects.json`.
- This starter uses OpenAI-compatible APIs for both embeddings and chat model, so you can point it to OpenAI or GLM via `OPENAI_BASE_URL`.
- Add auth, audit logging, and PII controls before production use.
