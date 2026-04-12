from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.models import Citation
from app.services.vector_store import get_vector_store


def _format_history(history: list[tuple[str, str]]) -> str:
    if not history:
        return "No prior chat history."
    return "\n".join([f"{role}: {content}" for role, content in history])


def ask_rag(
    question: str,
    namespaces: list[str],
    chat_history: list[tuple[str, str]] | None = None,
) -> tuple[str, list[Citation]]:
    settings = get_settings()
    llm = ChatOpenAI(model=settings.chat_model, api_key=settings.openai_api_key, temperature=0)

    gathered_docs = []
    for namespace in namespaces:
        vector_store = get_vector_store(namespace=namespace)
        docs = vector_store.similarity_search(question, k=settings.top_k)
        for doc in docs:
            doc.metadata["namespace"] = namespace
        gathered_docs.extend(docs)

    if not gathered_docs:
        return (
            "I do not have relevant indexed context yet. Please ingest your data first.",
            [],
        )

    contexts = []
    citations: list[Citation] = []
    for index, doc in enumerate(gathered_docs, start=1):
        source = doc.metadata.get("source", "unknown")
        namespace = doc.metadata.get("namespace", "personal")
        if namespace not in {"personal", "code"}:
            namespace = "personal"
        contexts.append(f"[{index}] source={source}\n{doc.page_content}")
        citations.append(Citation(source=source, chunk_id=str(index), namespace=namespace))

    history = _format_history(chat_history or [])
    prompt = f"""
You are an assistant that answers only from retrieved context.
Use concise, direct answers. If context is insufficient, say so clearly.
Always include citation references like [1], [2] that map to provided chunks.

Chat history:
{history}

Retrieved context:
{chr(10).join(contexts)}

User question:
{question}
"""
    response = llm.invoke(prompt)
    answer = response.content if isinstance(response.content, str) else str(response.content)
    return answer, citations

