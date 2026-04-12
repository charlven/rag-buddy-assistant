from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.models import (
    ChatRequest,
    ChatResponse,
    IngestRequest,
    IngestResponse,
    OpenAIChatCompletionChoice,
    OpenAIChatCompletionRequest,
    OpenAIChatCompletionResponse,
    OpenAIChatMessage,
    ProjectImportRequest,
    ProjectInfo,
)
from app.services.ingestion import ingest_path
from app.services.project_registry import list_projects, upsert_project
from app.services.retrieval import ask_rag
from app.services.vector_store import reset_namespace

app = FastAPI(title="LangChain RAG Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    if request.reset_namespace:
        reset_namespace(request.namespace)
    try:
        chunks, files = ingest_path(
            data_path=request.data_path,
            namespace=request.namespace,
            project_id=request.project_id,
            project_name=request.project_name,
            recursive=request.recursive,
            file_extensions=request.file_extensions,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return IngestResponse(
        namespace=request.namespace,
        project_id=request.project_id,
        indexed_chunks=chunks,
        indexed_files=files,
    )


@app.post("/projects/import", response_model=IngestResponse)
def import_project(request: ProjectImportRequest) -> IngestResponse:
    if request.reset_namespace:
        reset_namespace("code")

    project_name = request.project_name or request.project_id
    try:
        chunks, files = ingest_path(
            data_path=request.data_path,
            namespace="code",
            project_id=request.project_id,
            project_name=project_name,
            recursive=request.recursive,
            file_extensions=request.file_extensions,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    upsert_project(project_id=request.project_id, project_name=project_name, root_path=request.data_path)
    return IngestResponse(
        namespace="code",
        project_id=request.project_id,
        indexed_chunks=chunks,
        indexed_files=files,
    )


@app.get("/projects", response_model=list[ProjectInfo])
def projects() -> list[ProjectInfo]:
    return list_projects()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    history = [(msg.role, msg.content) for msg in request.chat_history]
    answer, citations = ask_rag(
        question=request.question,
        namespaces=request.namespaces,
        project_ids=request.project_ids,
        chat_history=history,
    )
    return ChatResponse(answer=answer, citations=citations)


@app.post("/v1/chat/completions", response_model=OpenAIChatCompletionResponse)
def openai_chat(request: OpenAIChatCompletionRequest) -> OpenAIChatCompletionResponse:
    if request.stream:
        raise HTTPException(
            status_code=400,
            detail="Streaming is not implemented in this starter. Use stream=false.",
        )

    user_messages = [m.content for m in request.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="messages must include at least one user message")

    question = user_messages[-1]
    history = [(m.role, m.content) for m in request.messages[:-1]]
    answer, _ = ask_rag(
        question=question,
        namespaces=request.namespaces,
        project_ids=request.project_ids,
        chat_history=history,
    )

    model_name = request.model or "rag-backend"
    return OpenAIChatCompletionResponse(
        id=f"chatcmpl-{uuid4().hex}",
        created=int(datetime.now(UTC).timestamp()),
        model=model_name,
        choices=[
            OpenAIChatCompletionChoice(
                index=0,
                message=OpenAIChatMessage(role="assistant", content=answer),
            )
        ],
    )


@app.get("/ui", response_class=HTMLResponse)
def ui() -> str:
    ui_path = Path(__file__).resolve().parent / "ui.html"
    return ui_path.read_text(encoding="utf-8")

