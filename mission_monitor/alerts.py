"""Regras simples de alerta e decisão."""

from mission_monitor.models import Alert, ModuleReading, Severity
from mission_monitor.scenarios import MODULE_LIMITS


def analyze(
    frame_modules: list[ModuleReading],
    battery: float,
    generation: float,
    consumption: float,
) -> tuple[list[Alert], list[str], str, float]:
    alerts: list[Alert] = []
    decisions: list[str] = []
    penalties = 0.0

    for module in frame_modules:
        limits = MODULE_LIMITS[module.name]
        module_state = "OK"

        temp = module.temperature_c
        energy = module.energy_pct

        # Temperatura
        if temp <= limits["temp_low"] or temp >= limits["temp_high"]:
            alerts.append(
                Alert(
                    severity=Severity.CRITICAL,
                    title=f"{module.name}: temperatura critica",
                    detail=f"Leitura de {temp:.1f} C fora da faixa segura.",
                    action="Ativar controle termico e reduzir carga do modulo.",
                )
            )
            module_state = "CRITICO"
            penalties += 18.0
        elif temp <= limits["temp_low"] + 2.5 or temp >= limits["temp_high"] - 3.0:
            alerts.append(
                Alert(
                    severity=Severity.WARNING,
                    title=f"{module.name}: temperatura em atencao",
                    detail=f"Leitura de {temp:.1f} C proxima do limite operacional.",
                    action="Acompanhar a tendencia nas proximas leituras.",
                )
            )
            module_state = "ATENCAO"
            penalties += 7.0

        # Energia
        if energy <= limits["crit_energy"]:
            alerts.append(
                Alert(
                    severity=Severity.CRITICAL,
                    title=f"{module.name}: energia critica",
                    detail=f"Reserva em {energy:.1f}% abaixo do minimo seguro.",
                    action="Entrar em modo economico e priorizar sistemas vitais.",
                )
            )
            module_state = "CRITICO"
            penalties += 18.0
        elif energy <= limits["warn_energy"]:
            alerts.append(
                Alert(
                    severity=Severity.WARNING,
                    title=f"{module.name}: energia reduzida",
                    detail=f"Reserva em {energy:.1f}% exige acompanhamento.",
                    action="Planejar recarga ou reduzir consumo nao essencial.",
                )
            )
            if module_state != "CRITICO":
                module_state = "ATENCAO"
            penalties += 7.0

        # Comunicacao
        if not module.communication_ok:
            is_critical = module.name == "Comunicacao"
            alerts.append(
                Alert(
                    severity=Severity.CRITICAL if is_critical else Severity.WARNING,
                    title=f"{module.name}: falha de comunicacao",
                    detail="Pacotes de telemetria inconsistentes ou ausentes.",
                    action=(
                        "Ativar antena reserva e reduzir transmissao nao essencial."
                        if is_critical
                        else "Revalidar o enlace e repetir a amostragem."
                    ),
                )
            )
            if is_critical:
                module_state = "CRITICO"
                penalties += 18.0
            elif module_state != "CRITICO":
                module_state = "ATENCAO"
                penalties += 7.0

        module.status = module_state

    # Bateria geral
    if battery <= 12.0:
        alerts.append(
            Alert(
                severity=Severity.CRITICAL,
                title="Bateria em nivel critico",
                detail=f"Carga remanescente de {battery:.1f}% compromete a autonomia da missao.",
                action="Desligar cargas secundarias e preservar os sistemas vitais.",
            )
        )
        decisions.append("Ativar modo de emergencia energetica.")
        penalties += 18.0
    elif battery <= 25.0:
        alerts.append(
            Alert(
                severity=Severity.WARNING,
                title="Bateria em atencao",
                detail=f"Carga remanescente de {battery:.1f}% precisa de recuperacao.",
                action="Aumentar captacao solar e reduzir consumo nao essencial.",
            )
        )
        decisions.append("Priorizar recarga do banco de baterias.")
        penalties += 7.0

    # Equilibrio energetico
    if generation < consumption:
        is_critical = battery <= 20.0
        alerts.append(
            Alert(
                severity=Severity.CRITICAL if is_critical else Severity.WARNING,
                title="Deficit energetico",
                detail=f"Consumo supera a geracao em {abs(generation - consumption):.1f} kW.",
                action="Reduzir cargas e reorganizar o uso de energia.",
            )
        )
        decisions.append("Racionalizar o consumo eletrico.")
        penalties += 18.0 if is_critical else 7.0

    # Energia renovavel
    if consumption > 0:
        renewable_share_pct = min(100.0, (generation / consumption) * 100.0)
    else:
        renewable_share_pct = 0.0

    if renewable_share_pct < 55.0:
        alerts.append(
            Alert(
                severity=Severity.WARNING,
                title="Participacao renovavel abaixo da meta",
                detail=f"Apenas {renewable_share_pct:.1f}% da demanda coberta pela geracao solar.",
                action="Otimizar a orientacao dos paineis e a eficiencia energetica.",
            )
        )
        decisions.append("Otimizar a captacao solar.")
        penalties += 7.0

    if not decisions:
        decisions.append("Manter operacao nominal e registrar a eficiencia da missao.")

    health_score = 100.0 - penalties
    health_score -= max(0.0, 20.0 - renewable_share_pct) * 0.2
    health_score = round(max(0.0, min(100.0, health_score)), 1)

    critical_count = sum(1 for alert in alerts if alert.severity == Severity.CRITICAL)
    warning_count = sum(1 for alert in alerts if alert.severity == Severity.WARNING)

    if critical_count > 0 or health_score < 45.0:
        mission_state = "CRITICO"
    elif warning_count > 0 or health_score < 75.0:
        mission_state = "ATENCAO"
    else:
        mission_state = "OPERACIONAL"

    decisions = list(dict.fromkeys(decisions))
    return alerts, decisions, mission_state, health_score
