import json
from datetime import UTC, datetime
from pathlib import Path

from app.config import get_settings
from app.models import ProjectInfo


def _registry_path() -> Path:
    settings = get_settings()
    path = settings.project_registry_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
    return path


def list_projects() -> list[ProjectInfo]:
    path = _registry_path()
    data = json.loads(path.read_text(encoding="utf-8"))
    return [ProjectInfo(**item) for item in data]


def upsert_project(project_id: str, project_name: str, root_path: str) -> ProjectInfo:
    path = _registry_path()
    current = json.loads(path.read_text(encoding="utf-8"))

    item = {
        "project_id": project_id,
        "project_name": project_name,
        "namespace": "code",
        "root_path": root_path,
        "indexed_at": datetime.now(UTC).isoformat(),
    }

    updated: list[dict] = [x for x in current if x.get("project_id") != project_id]
    updated.append(item)
    path.write_text(json.dumps(updated, indent=2), encoding="utf-8")
    return ProjectInfo(**item)

