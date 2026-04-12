from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    ChatRequest,
    ChatResponse,
    IngestRequest,
    IngestResponse,
    OpenAIChatCompletionChoice,
    OpenAIChatCompletionRequest,
    OpenAIChatCompletionResponse,
    OpenAIChatMessage,
)
from app.services.ingestion import ingest_path
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
            recursive=request.recursive,
            file_extensions=request.file_extensions,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return IngestResponse(namespace=request.namespace, indexed_chunks=chunks, indexed_files=files)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    history = [(msg.role, msg.content) for msg in request.chat_history]
    answer, citations = ask_rag(
        question=request.question,
        namespaces=request.namespaces,
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

