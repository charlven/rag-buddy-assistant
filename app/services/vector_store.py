from functools import lru_cache

import chromadb
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from app.config import get_settings


def _collection_name(namespace: str) -> str:
    settings = get_settings()
    return f"{settings.collection_prefix}_{namespace}"


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    settings = get_settings()
    base_url = settings.openai_base_url or None
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
        base_url=base_url,
        chunk_size=settings.embedding_batch_size,
    )


def get_vector_store(namespace: str) -> Chroma:
    settings = get_settings()
    return Chroma(
        collection_name=_collection_name(namespace),
        persist_directory=str(settings.chroma_persist_directory),
        embedding_function=get_embeddings(),
    )


def reset_namespace(namespace: str) -> None:
    settings = get_settings()
    client = chromadb.PersistentClient(path=str(settings.chroma_persist_directory))
    target_name = _collection_name(namespace)
    collections = client.list_collections()
    names = {collection.name for collection in collections}
    if target_name in names:
        client.delete_collection(target_name)

