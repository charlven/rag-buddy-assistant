# RAG Buddy Assistant

RAG Buddy Assistant is an open-source, OpenAI-compatible RAG backend for **code intelligence** and **personal knowledge assistance**.  
It works with Open WebUI and any client that supports the OpenAI Chat Completions API.

## What it does

- Indexes personal documents (`personal` namespace)
- Indexes source code (`code` namespace)
- Supports project-aware retrieval (`project_id`, `project_name`)
- Answers with grounded context and citations
- Supports OpenAI-compatible `stream=true` and `stream=false`

## Architecture

- **API server**: FastAPI (`app/main.py`)
- **Embeddings + chat model**: OpenAI-compatible provider (`langchain-openai`)
- **Vector DB**: Chroma (`./data/chroma`)
- **Project registry**: JSON store (`./data/projects.json`)
- **Frontend (optional)**: Open WebUI

## Quick start

### 1) Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Recommended Python: **3.11 or 3.12**.

### 2) Configure model provider

Update `.env`:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=
CHAT_MODEL=gpt-4.1-mini
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_BATCH_SIZE=64
```

For GLM (or other OpenAI-compatible providers), set `OPENAI_BASE_URL` accordingly.

### 3) Run the API

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Index data

### Personal documents

```powershell
python .\scripts\index_data.py --data-path "D:\my_personal_docs" --namespace personal --reset-namespace
```

### Source code

```powershell
python .\scripts\index_data.py --data-path "D:\my_source_code" --namespace code --reset-namespace
```

### Source code with project identity (recommended)

```powershell
python .\scripts\index_data.py --data-path "D:\repos\order-service" --namespace code --project-id order-service --project-name "Order Service"
python .\scripts\index_data.py --data-path "D:\repos\billing-service" --namespace code --project-id billing-service --project-name "Billing Service"
```

Optional file filters:

```powershell
python .\scripts\index_data.py --data-path "D:\my_source_code" --namespace code --extensions .py .ts .md
```

Default ingestion skips common generated/dependency folders such as `.git`, `node_modules`, `target`, `dist`, `build`, `.venv`, and `__pycache__`.

## API overview

### Core endpoints

- `GET /health`
- `POST /ingest`
- `POST /projects/import`
- `GET /projects`
- `POST /chat` (native request/response format)

### OpenAI-compatible endpoints

- `GET /v1/models`
- `POST /v1/chat/completions`
  - Expects `messages`
  - Supports `stream=true` and `stream=false`
  - Accepts optional `namespaces` and `project_ids`

### Example: native chat endpoint

```powershell
$body = @{
  question = "Which repository implements order cancellation and what is the request flow?"
  namespaces = @("code")
  project_ids = @("order-service")
  chat_history = @()
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/chat" -ContentType "application/json" -Body $body
```

## Open WebUI integration

Use Open WebUI as the frontend and configure it as an OpenAI provider.

- If Open WebUI runs in Docker and backend runs on host:
  - `http://host.docker.internal:8000/v1`
- If both run on the same host network:
  - `http://localhost:8000/v1`

Detailed setup and maintenance commands are in:

- [`OPEN_WEBUI_INTEGRATION_GUIDE.md`](./OPEN_WEBUI_INTEGRATION_GUIDE.md)

## Built-in local UI

For quick local testing:

- `http://localhost:8000/ui`

## Production notes

- Add authentication and authorization
- Add audit logging and PII controls
- Restrict CORS and secure secrets management
- Add monitoring and rate limiting

## Community

- [Contributing Guide](./CONTRIBUTING.md)
- [Code of Conduct](./CODE_OF_CONDUCT.md)
- [Security Policy](./SECURITY.md)
