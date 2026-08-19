"""Small helpers for persisting logcat captures as test artifacts."""
from __future__ import annotations

from pathlib import Path


def write_logcat_artifact(lines: list[str], out_dir: Path, name: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{name}.log"
    out_path.write_text("\n".join(lines) + "\n")
    return out_path
