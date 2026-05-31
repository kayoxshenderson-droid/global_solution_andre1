from __future__ import annotations

import argparse
import sys

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
except ImportError:
    print("Instale matplotlib: pip install matplotlib")
    sys.exit(1)

from mission_monitor.models import MissionSnapshot, Severity
from mission_monitor.monitor import MissionMonitor
from mission_monitor.scenarios import SCENARIOS


COLORS = {
    "generation": "#2ECC71",
    "consumption": "#E74C3C",
    "battery": "#3498DB",
    "health": "#9B59B6",
    "renewable": "#F39C12",
    "OPERACIONAL": "#2ECC71",
    "ATENCAO": "#F39C12",
    "CRITICO": "#E74C3C",
}


STATE_LABELS = {
    "OPERACIONAL": "Operacional",
    "ATENCAO": "Atenção",
    "CRITICO": "Crítico",
}


def collect_history(scenario_name: str, steps: int, seed: int = 42) -> list[MissionSnapshot]:
    monitor = MissionMonitor(scenario_name=scenario_name, seed=seed)
    history = []

    for _ in range(steps):
        history.append(monitor.next_snapshot())

    return history


def plot_dashboard(history: list[MissionSnapshot], output_path: str | None = None) -> None:
    if not history:
        print("Nao ha dados para gerar o grafico.")
        return

    steps = list(range(1, len(history) + 1))
    scenario = history[0].scenario

    generation = [item.generation_kw for item in history]
    consumption = [item.consumption_kw for item in history]
    battery = [item.battery_soc_pct for item in history]
    health = [item.health_score for item in history]
    renewable = [item.renewable_share_pct for item in history]
    states = [item.mission_state for item in history]

    critical_counts = [sum(1 for alert in item.alerts if alert.severity == Severity.CRITICAL) for item in history]
    warning_counts = [sum(1 for alert in item.alerts if alert.severity == Severity.WARNING) for item in history]

    fig, axes = plt.subplots(3, 2, figsize=(15, 11), facecolor="#0D1117")
    fig.suptitle(f"Monitor de Missão Espacial - {scenario}", fontsize=16, color="white")

    ax_energy = axes[0, 0]
    ax_battery = axes[0, 1]
    ax_health = axes[1, 0]
    ax_renewable = axes[1, 1]
    ax_alerts = axes[2, 0]
    ax_state = axes[2, 1]

    _style_axis(ax_energy)
    _style_axis(ax_battery)
    _style_axis(ax_health)
    _style_axis(ax_renewable)
    _style_axis(ax_alerts)
    _style_axis(ax_state)

    ax_energy.plot(steps, generation, marker="o", color=COLORS["generation"], label="Geração")
    ax_energy.plot(steps, consumption, marker="s", color=COLORS["consumption"], label="Consumo")
    ax_energy.set_title("Geração x Consumo", color="white")
    ax_energy.set_ylabel("kW", color="#AAAAAA")
    ax_energy.legend(fontsize=8)

    ax_battery.plot(steps, battery, marker="D", color=COLORS["battery"])
    ax_battery.axhline(25, color=COLORS["consumption"], linestyle="--", linewidth=1)
    ax_battery.axhline(12, color="#8B0000", linestyle="--", linewidth=1)
    ax_battery.set_title("Bateria", color="white")
    ax_battery.set_ylabel("%", color="#AAAAAA")

    ax_health.plot(steps, health, marker="^", color=COLORS["health"])
    ax_health.axhline(75, color=COLORS["renewable"], linestyle="--", linewidth=1)
    ax_health.axhline(45, color=COLORS["consumption"], linestyle="--", linewidth=1)
    ax_health.set_title("Health Score", color="white")
    ax_health.set_ylabel("Score", color="#AAAAAA")

    ax_renewable.plot(steps, renewable, marker="o", color=COLORS["renewable"])
    ax_renewable.axhline(55, color="white", linestyle="--", linewidth=1, alpha=0.4)
    ax_renewable.set_title("Energia Renovável", color="white")
    ax_renewable.set_ylabel("%", color="#AAAAAA")

    ax_alerts.bar([step - 0.15 for step in steps], critical_counts, width=0.3, color=COLORS["CRITICO"], label="Crítico")
    ax_alerts.bar([step + 0.15 for step in steps], warning_counts, width=0.3, color=COLORS["ATENCAO"], label="Warning")
    ax_alerts.set_title("Alertas", color="white")
    ax_alerts.set_ylabel("Qtd.", color="#AAAAAA")
    ax_alerts.legend(fontsize=8)

    state_y = {"CRITICO": 1, "ATENCAO": 2, "OPERACIONAL": 3}
    state_colors = [COLORS[state] for state in states]
    state_values = [state_y[state] for state in states]
    ax_state.scatter(steps, state_values, c=state_colors, s=80)
    ax_state.set_yticks([1, 2, 3])
    ax_state.set_yticklabels(["CRÍTICO", "ATENÇÃO", "OPERACIONAL"], color="white")
    ax_state.set_title("Estado da Missão", color="white")
    legend_items = [mpatches.Patch(color=COLORS[key], label=STATE_LABELS[key]) for key in STATE_LABELS]
    ax_state.legend(handles=legend_items, fontsize=8)

    for axis in [ax_energy, ax_battery, ax_health, ax_renewable, ax_alerts, ax_state]:
        axis.set_xlabel("Leitura", color="#AAAAAA")
        axis.tick_params(colors="#AAAAAA")
        axis.set_xticks(steps)
        axis.grid(True, linestyle="--", alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    if output_path:
        plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor())
        print(f"Grafico salvo em: {output_path}")
    else:
        output_path = f"dashboard_{scenario.replace(' ', '_')}.png"
        plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor())
        print(f"Grafico salvo em: {output_path}")

    plt.close(fig)


def _style_axis(axis: plt.Axes) -> None:
    axis.set_facecolor("#1A1F2C")
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color("#444")
    axis.spines["bottom"].set_color("#444")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera o dashboard da missao espacial")
    parser.add_argument("--scenario", default="Operacao nominal", choices=list(SCENARIOS))
    parser.add_argument("--steps", type=int, default=12)
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Simulando {args.steps} leituras - cenario: {args.scenario}")
    history = collect_history(args.scenario, args.steps)
    plot_dashboard(history, args.output)


if __name__ == "__main__":
    main()
