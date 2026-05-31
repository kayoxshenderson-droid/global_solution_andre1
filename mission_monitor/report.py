"""Exportacao de relatorios em JSON."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from mission_monitor.models import MissionSnapshot


def save_report(snapshot: MissionSnapshot, file_path: str) -> None:
    """Salva o snapshot como arquivo JSON formatado."""
    data = asdict(snapshot)
    for alert in data["alerts"]:
        alert["severity"] = alert["severity"].value if hasattr(alert["severity"], "value") else alert["severity"]
    Path(file_path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Relatorio salvo em: {file_path}")
