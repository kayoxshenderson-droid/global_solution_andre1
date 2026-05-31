"""Geracao de alertas e tomada de decisao automatizada."""
from __future__ import annotations

from typing import Iterable

from mission_monitor.models import Alert, ModuleReading, Severity
from mission_monitor.scenarios import MODULE_LIMITS


def _unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def analyze(
    frame_modules: list[ModuleReading],
    battery: float,
    generation: float,
    consumption: float,
) -> tuple[list[Alert], list[str], str, float]:
    """Analisa os dados dos modulos e retorna alertas, decisoes, estado e saude."""
    alerts: list[Alert] = []
    decisions: list[str] = []
    penalties = 0.0

    for module in frame_modules:
        limits = MODULE_LIMITS[module.name]
        module_state = "OK"

        # --- Temperatura ---
        if module.temperature_c <= limits["temp_low"] or module.temperature_c >= limits["temp_high"]:
            alerts.append(Alert(
                severity=Severity.CRITICAL,
                title=f"{module.name}: temperatura critica",
                detail=f"Leitura de {module.temperature_c:.1f} C fora da faixa segura.",
                action="Ativar controle termico e reduzir carga do modulo.",
            ))
            module_state = "CRITICO"
            penalties += 18.0
        elif (
            module.temperature_c <= limits["temp_low"] + 2.5
            or module.temperature_c >= limits["temp_high"] - 3.0
        ):
            alerts.append(Alert(
                severity=Severity.WARNING,
                title=f"{module.name}: temperatura em atencao",
                detail=f"Leitura de {module.temperature_c:.1f} C proxima do limite operacional.",
                action="Acompanhar a tendencia nas proximas leituras.",
            ))
            module_state = "ATENCAO"
            penalties += 7.0

        # --- Energia ---
        if module.energy_pct <= limits["crit_energy"]:
            alerts.append(Alert(
                severity=Severity.CRITICAL,
                title=f"{module.name}: energia critica",
                detail=f"Reserva em {module.energy_pct:.1f}% abaixo do minimo seguro.",
                action="Entrar em modo economico e priorizar sistemas vitais.",
            ))
            module_state = "CRITICO"
            penalties += 18.0
        elif module.energy_pct <= limits["warn_energy"]:
            alerts.append(Alert(
                severity=Severity.WARNING,
                title=f"{module.name}: energia reduzida",
                detail=f"Reserva em {module.energy_pct:.1f}% exige acompanhamento.",
                action="Planejar recarga ou reduzir consumo nao essencial.",
            ))
            if module_state != "CRITICO":
                module_state = "ATENCAO"
            penalties += 7.0

        # --- Comunicacao ---
        if not module.communication_ok:
            severity = Severity.CRITICAL if module.name == "Comunicacao" else Severity.WARNING
            alerts.append(Alert(
                severity=severity,
                title=f"{module.name}: falha de comunicacao",
                detail="Pacotes de telemetria inconsistentes ou ausentes.",
                action=(
                    "Ativar antena reserva e reduzir transmissao nao essencial."
                    if severity == Severity.CRITICAL
                    else "Revalidar o enlace e repetir a amostragem."
                ),
            ))
            if severity == Severity.CRITICAL:
                module_state = "CRITICO"
            elif module_state != "CRITICO":
                module_state = "ATENCAO"
            penalties += 18.0 if severity == Severity.CRITICAL else 7.0

        module.status = module_state

    # --- Bateria global ---
    if battery <= 12.0:
        alerts.append(Alert(
            severity=Severity.CRITICAL,
            title="Bateria em nivel critico",
            detail=f"Carga remanescente de {battery:.1f}% compromete a autonomia da missao.",
            action="Desligar cargas secundarias e preservar os sistemas vitais.",
        ))
        decisions.append("Ativar modo de emergencia energetica.")
        penalties += 18.0
    elif battery <= 25.0:
        alerts.append(Alert(
            severity=Severity.WARNING,
            title="Bateria em atencao",
            detail=f"Carga remanescente de {battery:.1f}% precisa de recuperacao.",
            action="Aumentar captacao solar e reduzir consumo nao essencial.",
        ))
        decisions.append("Priorizar recarga do banco de baterias.")
        penalties += 7.0

    # --- Balanco energetico ---
    if generation < consumption:
        alerts.append(Alert(
            severity=Severity.WARNING if battery > 20.0 else Severity.CRITICAL,
            title="Deficit energetico",
            detail=f"Consumo supera a geracao em {abs(generation - consumption):.1f} kW.",
            action="Reduzir cargas e reorganizar o uso de energia.",
        ))
        decisions.append("Racionalizar o consumo eletrico.")
        penalties += 7.0 if battery > 20.0 else 18.0

    # --- Participacao renovavel ---
    renewable_share_pct = min(100.0, (generation / consumption) * 100.0)
    if renewable_share_pct < 55.0:
        alerts.append(Alert(
            severity=Severity.WARNING,
            title="Participacao renovavel abaixo da meta",
            detail=f"Apenas {renewable_share_pct:.1f}% da demanda coberta pela geracao solar.",
            action="Otimizar a orientacao dos paineis e a eficiencia energetica.",
        ))
        decisions.append("Otimizar a captacao solar.")
        penalties += 7.0

    if not decisions:
        decisions.append("Manter operacao nominal e registrar a eficiencia da missao.")

    # --- Health score ---
    health_score = 100.0 - penalties
    health_score -= max(0.0, 20.0 - renewable_share_pct) * 0.2
    health_score = max(0.0, min(100.0, round(health_score, 1)))

    critical_count = sum(1 for a in alerts if a.severity == Severity.CRITICAL)
    warning_count = sum(1 for a in alerts if a.severity == Severity.WARNING)

    if critical_count > 0 or health_score < 45.0:
        mission_state = "CRITICO"
    elif warning_count > 0 or health_score < 75.0:
        mission_state = "ATENCAO"
    else:
        mission_state = "OPERACIONAL"

    return alerts, _unique(decisions), mission_state, health_score
