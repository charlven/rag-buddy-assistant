import argparse

from app.services.ingestion import ingest_path
from app.services.vector_store import reset_namespace


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest files into the RAG vector database.")
    parser.add_argument("--data-path", required=True, help="Directory path to index.")
    parser.add_argument(
        "--namespace",
        choices=["personal", "code"],
        required=True,
        help="Target namespace/collection.",
    )
    parser.add_argument("--no-recursive", action="store_true", help="Disable recursive file walk.")
    parser.add_argument(
        "--reset-namespace",
        action="store_true",
        help="Delete the namespace collection before indexing.",
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        help="Optional file extensions (e.g. .md .py .txt). Defaults to built-in list.",
    )
    parser.add_argument("--project-id", default=None, help="Optional project/repository ID (recommended for code).")
    parser.add_argument("--project-name", default=None, help="Optional project display name.")
    parser.add_argument("--chunk-size", type=int, default=None)
    parser.add_argument("--chunk-overlap", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.reset_namespace:
        reset_namespace(args.namespace)

    chunks, files = ingest_path(
        data_path=args.data_path,
        namespace=args.namespace,
        project_id=args.project_id,
        project_name=args.project_name,
        recursive=not args.no_recursive,
        file_extensions=args.extensions,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    print(f"Indexed namespace={args.namespace} files={files} chunks={chunks}")


if __name__ == "__main__":
    main()

