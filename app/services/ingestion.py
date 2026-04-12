from collections.abc import Iterable
from os import walk
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.config import get_settings
from app.services.vector_store import get_vector_store

DEFAULT_EXTENSIONS = {
    ".txt",
    ".md",
    ".rst",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rs",
    ".c",
    ".cpp",
    ".cs",
    ".sql",
    ".html",
    ".css",
    ".pdf",
}

DEFAULT_EXCLUDED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
    "out",
    ".next",
    ".nuxt",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
}


def _iter_files(root: Path, recursive: bool, extensions: set[str]) -> Iterable[Path]:
    if recursive:
        for current_root, dir_names, file_names in walk(root):
            dir_names[:] = [name for name in dir_names if name.lower() not in DEFAULT_EXCLUDED_DIR_NAMES]
            current = Path(current_root)
            for file_name in file_names:
                path = current / file_name
                if path.suffix.lower() in extensions:
                    yield path
        return

    for path in root.glob("*"):
        if path.is_file() and path.suffix.lower() in extensions:
            yield path


def _read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def _build_documents(
    files: list[Path],
    namespace: str,
    source_root: Path,
    project_id: str | None,
    project_name: str | None,
) -> list[Document]:
    documents: list[Document] = []
    for file_path in files:
        try:
            content = _read_file(file_path)
        except Exception as err:
            raise ValueError(f"Failed to read file: {file_path}. Error: {err}") from err
        if not content.strip():
            continue
        relative_path = str(file_path.relative_to(source_root))
        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(file_path),
                    "relative_path": relative_path,
                    "file_name": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "namespace": namespace,
                    "project_id": project_id,
                    "project_name": project_name,
                },
            )
        )
    return documents


def ingest_path(
    data_path: str,
    namespace: str,
    project_id: str | None = None,
    project_name: str | None = None,
    recursive: bool = True,
    file_extensions: list[str] | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> tuple[int, int]:
    settings = get_settings()
    root = Path(data_path).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Path not found or not a directory: {root}")

    configured_extensions = file_extensions or list(DEFAULT_EXTENSIONS)
    extensions = {(ext if ext.startswith(".") else f".{ext}").lower() for ext in configured_extensions}
    files = list(_iter_files(root=root, recursive=recursive, extensions=extensions))

    docs = _build_documents(
        files=files,
        namespace=namespace,
        source_root=root,
        project_id=project_id,
        project_name=project_name,
    )
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.chunk_size,
        chunk_overlap=chunk_overlap or settings.chunk_overlap,
    )
    chunks = splitter.split_documents(docs)

    if chunks:
        vector_store = get_vector_store(namespace=namespace)
        try:
            vector_store.add_documents(chunks)
        except Exception as err:
            raise ValueError(f"Failed to index documents in namespace '{namespace}': {err}") from err

    return len(chunks), len(docs)

