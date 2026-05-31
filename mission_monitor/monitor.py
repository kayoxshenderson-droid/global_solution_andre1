"""Classe principal de monitoramento da missao espacial."""
from __future__ import annotations

import math
import random
from datetime import datetime

from mission_monitor.alerts import analyze
from mission_monitor.models import MissionSnapshot, ModuleReading
from mission_monitor.scenarios import SCENARIOS


class MissionMonitor:
    """Simula e monitora os sistemas energeticos de uma missao espacial."""

    def __init__(self, scenario_name: str = "Operacao nominal", seed: int = 42) -> None:
        self.random = random.Random(seed)
        self.set_scenario(scenario_name)

    def set_scenario(self, scenario_name: str) -> None:
        if scenario_name not in SCENARIOS:
            raise ValueError(f"Cenario invalido: {scenario_name}")
        self.scenario = SCENARIOS[scenario_name]
        self.step_index = 0
        self.battery_soc_pct = self.scenario.battery_start_pct

    def next_snapshot(self) -> MissionSnapshot:
        self.step_index += 1

        sunlight = 0.55 + 0.45 * math.sin(self.step_index / 3.0)
        generation_kw = max(
            0.6,
            (15.0 * sunlight * self.scenario.generation_multiplier) + self.random.uniform(-0.5, 0.8),
        )
        consumption_kw = max(
            5.0,
            (9.2 * self.scenario.consumption_multiplier) + self.random.uniform(-0.4, 0.6),
        )
        net_kw = generation_kw - consumption_kw

        self.battery_soc_pct = max(
            0.0,
            min(100.0, self.battery_soc_pct + (net_kw * 1.8) + self.random.uniform(-0.6, 0.4)),
        )

        modules = [
            ModuleReading(
                name="Painel Solar",
                temperature_c=32.0 + (10.0 * sunlight) + self.scenario.temperature_bias + self.random.uniform(-1.5, 1.5),
                energy_pct=max(0.0, min(100.0, 70.0 + (25.0 * sunlight) + self.random.uniform(-2.0, 2.0))),
                communication_ok=True,
                power_kw=round(generation_kw, 1),
            ),
            ModuleReading(
                name="Bateria",
                temperature_c=23.0 + (self.scenario.temperature_bias * 0.3) + self.random.uniform(-1.0, 1.2),
                energy_pct=round(self.battery_soc_pct, 1),
                communication_ok=True,
                power_kw=0.0,
            ),
            ModuleReading(
                name="Habitat",
                temperature_c=22.0 + (self.scenario.temperature_bias * 0.15) + self.random.uniform(-1.0, 1.0),
                energy_pct=max(20.0, min(100.0, self.battery_soc_pct - 8.0 + self.random.uniform(-3.0, 2.5))),
                communication_ok=True,
                power_kw=round(-(consumption_kw * 0.40), 1),
            ),
            ModuleReading(
                name="Comunicacao",
                temperature_c=27.0 + (self.scenario.temperature_bias * 0.10) + self.random.uniform(-1.2, 1.8),
                energy_pct=max(18.0, min(100.0, 82.0 - (self.step_index * 0.7) + self.random.uniform(-3.0, 3.0))),
                communication_ok=self.random.random() > self.scenario.communication_noise,
                power_kw=-1.1,
            ),
            ModuleReading(
                name="Controle Termico",
                temperature_c=25.0 + self.scenario.temperature_bias + self.random.uniform(-1.0, 1.5),
                energy_pct=max(24.0, min(100.0, 88.0 - (consumption_kw * 1.1) + self.random.uniform(-2.5, 2.0))),
                communication_ok=True,
                power_kw=round(-(consumption_kw * 0.20), 1),
            ),
        ]

        alerts, decisions, mission_state, health_score = analyze(
            frame_modules=modules,
            battery=self.battery_soc_pct,
            generation=generation_kw,
            consumption=consumption_kw,
        )
        renewable_share_pct = round(min(100.0, (generation_kw / consumption_kw) * 100.0), 1)

        return MissionSnapshot(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            scenario=self.scenario.name,
            mission_state=mission_state,
            health_score=health_score,
            battery_soc_pct=round(self.battery_soc_pct, 1),
            generation_kw=round(generation_kw, 1),
            consumption_kw=round(consumption_kw, 1),
            renewable_share_pct=renewable_share_pct,
            modules=modules,
            alerts=alerts,
            decisions=decisions,
        )
