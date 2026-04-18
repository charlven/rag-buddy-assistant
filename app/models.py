from typing import Literal

from pydantic import BaseModel, Field


Namespace = Literal["personal", "code"]
Role = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
    role: Role
    content: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    namespaces: list[Namespace] = Field(default_factory=lambda: ["personal", "code"])
    project_ids: list[str] = Field(default_factory=list)
    chat_history: list[ChatMessage] = Field(default_factory=list)


class Citation(BaseModel):
    source: str
    chunk_id: str | None = None
    namespace: Namespace
    project_id: str | None = None
    relative_path: str | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]


class IngestRequest(BaseModel):
    data_path: str = Field(min_length=1)
    namespace: Namespace
    project_id: str | None = None
    project_name: str | None = None
    recursive: bool = True
    reset_namespace: bool = False
    file_extensions: list[str] | None = None
    chunk_size: int | None = None
    chunk_overlap: int | None = None


class IngestResponse(BaseModel):
    namespace: Namespace
    project_id: str | None = None
    indexed_chunks: int
    indexed_files: int


class ProjectImportRequest(BaseModel):
    data_path: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    project_name: str | None = None
    recursive: bool = True
    file_extensions: list[str] | None = None
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    reset_namespace: bool = False


class ProjectInfo(BaseModel):
    project_id: str
    project_name: str
    namespace: Namespace = "code"
    root_path: str
    indexed_at: str


class OpenAIChatMessage(BaseModel):
    role: Role
    content: str


class OpenAIChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[OpenAIChatMessage]
    stream: bool = False
    namespaces: list[Namespace] = Field(default_factory=lambda: ["personal", "code"])
    project_ids: list[str] = Field(default_factory=list)


class OpenAIChatCompletionChoice(BaseModel):
    index: int
    message: OpenAIChatMessage
    finish_reason: str = "stop"


class OpenAIChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[OpenAIChatCompletionChoice]
    citations: list[Citation] = Field(default_factory=list)


class OpenAIModelInfo(BaseModel):
    id: str
    object: str = "model"
    owned_by: str = "rag-backend"


class OpenAIModelListResponse(BaseModel):
    object: str = "list"
    data: list[OpenAIModelInfo]
