# RAG Buddy Assistant + Open WebUI Integration Guide

This project uses:

- **Backend**: FastAPI RAG service (OpenAI-compatible API)
- **Frontend**: Open WebUI (Docker)

## 1) Integration Architecture

The backend exposes OpenAI-compatible endpoints:

- `GET /v1/models`
- `POST /v1/chat/completions` (supports `stream=true` and `stream=false`)

Open WebUI connects to that backend as an OpenAI provider.

When Open WebUI runs in Docker and backend runs on host, use:

- `http://host.docker.internal:8000/v1`

## 2) Start the Backend

```powershell
Set-Location "D:\path\rag-buddy-assistant"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health checks:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/v1/models
```

## 3) Start Open WebUI

```powershell
docker run -d --name open-webui -p 3000:8080 `
  -v open-webui:/app/backend/data `
  -e OPENAI_API_BASE_URLS="http://host.docker.internal:8000/v1" `
  -e OPENAI_API_KEYS="dummy-key" `
  ghcr.io/open-webui/open-webui:git-b993b66
```

Open:

- `http://localhost:3000`

First-time login:

- Click **Sign Up** and create the first account (Admin).

## 4) Open WebUI Configuration Checklist

In Open WebUI Admin settings:

1. OpenAI Base URL: `http://host.docker.internal:8000/v1`
2. OpenAI API Key: any non-empty value (for this backend setup)
3. Default model: value returned by `GET /v1/models` (example: `glm-4.7-flash`)

## 5) Operations & Maintenance Commands

Check status:

```powershell
docker ps -a --filter "name=open-webui"
```

View logs:

```powershell
docker logs -f open-webui
```

Restart:

```powershell
docker restart open-webui
```

Stop/Start:

```powershell
docker stop open-webui
docker start open-webui
```

Recreate container (keep history because volume is persisted):

```powershell
docker rm -f open-webui
docker run -d --name open-webui -p 3000:8080 `
  -v open-webui:/app/backend/data `
  -e OPENAI_API_BASE_URLS="http://host.docker.internal:8000/v1" `
  -e OPENAI_API_KEYS="dummy-key" `
  ghcr.io/open-webui/open-webui:git-b993b66
```

Update image:

```powershell
docker pull ghcr.io/open-webui/open-webui:latest
docker rm -f open-webui
docker run -d --name open-webui -p 3000:8080 `
  -v open-webui:/app/backend/data `
  -e OPENAI_API_BASE_URLS="http://host.docker.internal:8000/v1" `
  -e OPENAI_API_KEYS="dummy-key" `
  ghcr.io/open-webui/open-webui:latest
```

## 6) Backup and Restore Chat History

Backup:

```powershell
docker run --rm -v open-webui:/data -v "${PWD}:/backup" alpine `
  sh -c "cd /data && tar czf /backup/open-webui-backup.tgz ."
```

Restore:

```powershell
docker run --rm -v open-webui:/data -v "${PWD}:/backup" alpine `
  sh -c "cd /data && tar xzf /backup/open-webui-backup.tgz"
```

## 7) Quick Troubleshooting

- UI not reachable: check `docker ps` and port `3000`.
- Chat fails: check `docker logs -f open-webui` and backend `http://localhost:8000/health`.
- Model list empty: verify backend `GET /v1/models`.
- Backend unreachable from container: use `host.docker.internal`, not `localhost`.
