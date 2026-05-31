"""Salva o snapshot em JSON."""

import json
from dataclasses import asdict
from pathlib import Path

from mission_monitor.models import MissionSnapshot


def save_report(snapshot: MissionSnapshot, file_path: str) -> None:
    data = asdict(snapshot)
    Path(file_path).write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Relatorio salvo em: {file_path}")
