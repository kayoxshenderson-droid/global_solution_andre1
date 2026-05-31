"""Cenarios de missao e limites operacionais dos modulos."""
from __future__ import annotations

from mission_monitor.models import ScenarioProfile

SCENARIOS: dict[str, ScenarioProfile] = {
    "Operacao nominal": ScenarioProfile("Operacao nominal", 1.00, 1.00, 0.0, 0.00, 78.0),
    "Baixa irradiacao": ScenarioProfile("Baixa irradiacao", 0.55, 1.02, -2.0, 0.05, 62.0),
    "Instabilidade de comunicacao": ScenarioProfile("Instabilidade de comunicacao", 0.92, 1.00, 1.0, 0.35, 74.0),
    "Estresse termico": ScenarioProfile("Estresse termico", 0.90, 1.08, 12.0, 0.08, 70.0),
    "Emergencia energetica": ScenarioProfile("Emergencia energetica", 0.32, 1.28, 6.0, 0.15, 30.0),
}

MODULE_LIMITS: dict[str, dict[str, float]] = {
    "Painel Solar":     {"temp_low": -15.0, "temp_high": 85.0, "warn_energy": 40.0, "crit_energy": 22.0},
    "Bateria":          {"temp_low":  -5.0, "temp_high": 55.0, "warn_energy": 28.0, "crit_energy": 14.0},
    "Habitat":          {"temp_low":  17.0, "temp_high": 27.0, "warn_energy": 35.0, "crit_energy": 18.0},
    "Comunicacao":      {"temp_low": -10.0, "temp_high": 50.0, "warn_energy": 30.0, "crit_energy": 14.0},
    "Controle Termico": {"temp_low": -10.0, "temp_high": 60.0, "warn_energy": 30.0, "crit_energy": 18.0},
}
