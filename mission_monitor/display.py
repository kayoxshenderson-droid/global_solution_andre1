"""Mostra o snapshot no terminal."""

from mission_monitor.models import MissionSnapshot, Severity


def print_snapshot(snapshot: MissionSnapshot) -> None:
    state_color = {
        "OPERACIONAL": "\033[92m",
        "ATENCAO": "\033[93m",
        "CRITICO": "\033[91m",
    }
    severity_color = {
        Severity.INFO: "\033[94m",
        Severity.WARNING: "\033[93m",
        Severity.CRITICAL: "\033[91m",
    }
    reset = "\033[0m"

    color = state_color.get(snapshot.mission_state, "")

    print()
    print("=" * 68)
    print(f"Global Solution | {snapshot.timestamp}")
    print(f"Cenario: {snapshot.scenario}")
    print(f"Estado: {color}{snapshot.mission_state}{reset} | Saude: {snapshot.health_score:.1f}/100")
    print(
        f"Energia: bateria {snapshot.battery_soc_pct:.1f}% | "
        f"geracao {snapshot.generation_kw:.1f} kW | "
        f"consumo {snapshot.consumption_kw:.1f} kW | "
        f"renovavel {snapshot.renewable_share_pct:.1f}%"
    )
    print("=" * 68)

    print()
    print(f"{'Modulo':18} {'Temp':>7} {'Energia':>8} {'Com':>6} {'Potencia':>10} {'Status':>11}")
    print("-" * 68)
    for module in snapshot.modules:
        com = "OK" if module.communication_ok else "FALHA"
        print(
            f"{module.name:18} {module.temperature_c:6.1f}C "
            f"{module.energy_pct:7.1f}% {com:>6} "
            f"{module.power_kw:10.1f} {module.status:>11}"
        )

    print()
    print("Alertas:")
    if not snapshot.alerts:
        print("  Nenhum alerta ativo.")
    else:
        for alert in snapshot.alerts:
            color = severity_color.get(alert.severity, "")
            print(f"  {color}[{alert.severity}]{reset} {alert.title}")
            print(f"    {alert.detail}")
            print(f"    Acao: {alert.action}")

    print()
    print("Decisoes automatizadas:")
    for decision in snapshot.decisions:
        print(f"  - {decision}")
