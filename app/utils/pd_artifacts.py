from pathlib import Path
from datetime import datetime
from typing import Any
import json


def write_pd_artifact(
    base_dir: Path,
    environment: str,
    correlation_id: str,
    payload: dict[str, Any],
) -> Path:
    """
    Persist a NON-PHI PD execution artifact locally.
    Safe, idempotent, and production-friendly.
    """

    now = datetime.utcnow()

    artifact_dir = (
        base_dir
        / f"env={environment}"
        / f"{now.year}"
        / f"{now.month:02d}"
        / f"{now.day:02d}"
    )

    artifact_dir.mkdir(parents=True, exist_ok=True)

    artifact_path = artifact_dir / f"{correlation_id}.json"
    artifact_path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    return artifact_path
