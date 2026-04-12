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
    chat_history: list[ChatMessage] = Field(default_factory=list)


class Citation(BaseModel):
    source: str
    chunk_id: str | None = None
    namespace: Namespace


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]


class IngestRequest(BaseModel):
    data_path: str = Field(min_length=1)
    namespace: Namespace
    recursive: bool = True
    reset_namespace: bool = False
    file_extensions: list[str] | None = None
    chunk_size: int | None = None
    chunk_overlap: int | None = None


class IngestResponse(BaseModel):
    namespace: Namespace
    indexed_chunks: int
    indexed_files: int


class OpenAIChatMessage(BaseModel):
    role: Role
    content: str


class OpenAIChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[OpenAIChatMessage]
    stream: bool = False
    namespaces: list[Namespace] = Field(default_factory=lambda: ["personal", "code"])


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
