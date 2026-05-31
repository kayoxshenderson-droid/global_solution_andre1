"""Modelos simples usados pelo monitor."""

from dataclasses import dataclass, field


class Severity:
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class ModuleReading:
    name: str
    temperature_c: float
    energy_pct: float
    communication_ok: bool
    power_kw: float
    status: str = "OK"


@dataclass
class Alert:
    severity: str
    title: str
    detail: str
    action: str


@dataclass
class MissionSnapshot:
    timestamp: str
    scenario: str
    mission_state: str
    health_score: float
    battery_soc_pct: float
    generation_kw: float
    consumption_kw: float
    renewable_share_pct: float
    modules: list[ModuleReading] = field(default_factory=list)
    alerts: list[Alert] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScenarioProfile:
    name: str
    generation_multiplier: float
    consumption_multiplier: float
    temperature_bias: float
    communication_noise: float
    battery_start_pct: float
