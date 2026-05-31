from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.gridspec import GridSpec
except ImportError:
    print("Instale matplotlib: pip install matplotlib")
    sys.exit(1)

from mission_monitor.monitor import MissionMonitor
from mission_monitor.models import MissionSnapshot, Severity
from mission_monitor.scenarios import SCENARIOS

# Paleta de cores
COLORS = {
    "generation":  "#2ECC71",
    "consumption": "#E74C3C",
    "battery":     "#3498DB",
    "health":      "#9B59B6",
    "renewable":   "#F39C12",
    "OPERACIONAL": "#2ECC71",
    "ATENCAO":     "#F39C12",
    "CRITICO":     "#E74C3C",
}

STATE_PT = {
    "OPERACIONAL": "Operacional",
    "ATENCAO":     "Atenção",
    "CRITICO":     "Crítico",
}


def collect_history(scenario_name: str, steps: int, seed: int = 42) -> list[MissionSnapshot]:
    monitor = MissionMonitor(scenario_name=scenario_name, seed=seed)
    return [monitor.next_snapshot() for _ in range(steps)]


def plot_dashboard(history: list[MissionSnapshot], output_path: str | None = None) -> None:
    steps = list(range(1, len(history) + 1))
    scenario = history[0].scenario

    generation   = [s.generation_kw      for s in history]
    consumption  = [s.consumption_kw     for s in history]
    battery      = [s.battery_soc_pct    for s in history]
    health       = [s.health_score       for s in history]
    renewable    = [s.renewable_share_pct for s in history]
    states       = [s.mission_state      for s in history]

    # Contagem de alertas por leitura
    critical_counts = [sum(1 for a in s.alerts if a.severity == Severity.CRITICAL) for s in history]
    warning_counts  = [sum(1 for a in s.alerts if a.severity == Severity.WARNING)  for s in history]

    fig = plt.figure(figsize=(16, 12), facecolor="#0D1117")
    fig.suptitle(
        f"Monitor de Missão Espacial — {scenario}",
        fontsize=16, fontweight="bold", color="white", y=0.98,
    )

    gs = GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35,
                  left=0.07, right=0.97, top=0.93, bottom=0.06)

    ax_energy   = fig.add_subplot(gs[0, 0])
    ax_battery  = fig.add_subplot(gs[0, 1])
    ax_health   = fig.add_subplot(gs[1, 0])
    ax_renew    = fig.add_subplot(gs[1, 1])
    ax_alerts   = fig.add_subplot(gs[2, 0])
    ax_state    = fig.add_subplot(gs[2, 1])

    _style_ax(ax_energy)
    _style_ax(ax_battery)
    _style_ax(ax_health)
    _style_ax(ax_renew)
    _style_ax(ax_alerts)
    _style_ax(ax_state)

    # --- 1. Geração vs Consumo ---
    ax_energy.plot(steps, generation,  color=COLORS["generation"],  lw=2, label="Geração (kW)", marker="o", ms=4)
    ax_energy.plot(steps, consumption, color=COLORS["consumption"], lw=2, label="Consumo (kW)", marker="s", ms=4)
    ax_energy.fill_between(steps, generation, consumption,
                           where=[g >= c for g, c in zip(generation, consumption)],
                           alpha=0.15, color=COLORS["generation"], label="Superávit")
    ax_energy.fill_between(steps, generation, consumption,
                           where=[g < c for g, c in zip(generation, consumption)],
                           alpha=0.15, color=COLORS["consumption"], label="Déficit")
    ax_energy.set_title("Geração vs Consumo Energético", color="white", fontsize=11)
    ax_energy.set_ylabel("kW", color="#AAAAAA")
    ax_energy.legend(fontsize=8, facecolor="#1A1F2C", labelcolor="white")

    # --- 2. Bateria ---
    ax_battery.plot(steps, battery, color=COLORS["battery"], lw=2, marker="D", ms=4)
    ax_battery.fill_between(steps, battery, alpha=0.20, color=COLORS["battery"])
    ax_battery.axhline(25, color=COLORS["consumption"], ls="--", lw=1, label="Limite WARNING (25%)")
    ax_battery.axhline(12, color="#8B0000",             ls="--", lw=1, label="Limite CRÍTICO (12%)")
    ax_battery.set_ylim(0, 105)
    ax_battery.set_title("Estado de Carga da Bateria", color="white", fontsize=11)
    ax_battery.set_ylabel("% SOC", color="#AAAAAA")
    ax_battery.legend(fontsize=8, facecolor="#1A1F2C", labelcolor="white")

    # --- 3. Saúde da Missão ---
    ax_health.plot(steps, health, color=COLORS["health"], lw=2, marker="^", ms=5)
    ax_health.fill_between(steps, health, alpha=0.18, color=COLORS["health"])
    ax_health.axhline(75, color=COLORS["renewable"], ls="--", lw=1, label="Meta operacional (75)")
    ax_health.axhline(45, color=COLORS["consumption"], ls="--", lw=1, label="Limite crítico (45)")
    ax_health.set_ylim(0, 105)
    ax_health.set_title("Health Score da Missão", color="white", fontsize=11)
    ax_health.set_ylabel("Score", color="#AAAAAA")
    ax_health.legend(fontsize=8, facecolor="#1A1F2C", labelcolor="white")

    # --- 4. Participação Renovável ---
    ax_renew.plot(steps, renewable, color=COLORS["renewable"], lw=2, marker="o", ms=4)
    ax_renew.fill_between(steps, renewable, alpha=0.20, color=COLORS["renewable"])
    ax_renew.axhline(55, color="#FFFFFF", ls="--", lw=1, alpha=0.4, label="Meta mínima (55%)")
    ax_renew.set_ylim(0, 115)
    ax_renew.set_title("Participação de Energia Renovável", color="white", fontsize=11)
    ax_renew.set_ylabel("% Cobertura Solar", color="#AAAAAA")
    ax_renew.legend(fontsize=8, facecolor="#1A1F2C", labelcolor="white")

    # --- 5. Contagem de Alertas ---
    width = 0.4
    x = [s - width / 2 for s in steps]
    ax_alerts.bar(x, critical_counts, width=width, color=COLORS["CRITICO"],  label="Crítico",  alpha=0.85)
    x2 = [s + width / 2 for s in steps]
    ax_alerts.bar(x2, warning_counts, width=width, color=COLORS["ATENCAO"],  label="Warning",  alpha=0.85)
    ax_alerts.set_title("Alertas por Leitura", color="white", fontsize=11)
    ax_alerts.set_ylabel("Qtd. Alertas", color="#AAAAAA")
    ax_alerts.legend(fontsize=8, facecolor="#1A1F2C", labelcolor="white")
    ax_alerts.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # --- 6. Estado da Missão (scatter colorido) ---
    state_y = {"OPERACIONAL": 3, "ATENCAO": 2, "CRITICO": 1}
    state_colors = [COLORS[s] for s in states]
    state_ys = [state_y[s] for s in states]
    ax_state.scatter(steps, state_ys, c=state_colors, s=90, zorder=3)
    for i, (step, sy, s) in enumerate(zip(steps, state_ys, states)):
        ax_state.plot([step, step], [0.5, sy], color=state_colors[i], lw=1, alpha=0.4)
    ax_state.set_yticks([1, 2, 3])
    ax_state.set_yticklabels(["CRÍTICO", "ATENÇÃO", "OPERACIONAL"], color="white", fontsize=9)
    ax_state.set_ylim(0.3, 3.7)
    ax_state.set_title("Estado da Missão por Leitura", color="white", fontsize=11)
    patches = [mpatches.Patch(color=COLORS[k], label=STATE_PT[k]) for k in STATE_PT]
    ax_state.legend(handles=patches, fontsize=8, facecolor="#1A1F2C", labelcolor="white")

    # Eixo X global
    for ax in [ax_energy, ax_battery, ax_health, ax_renew, ax_alerts, ax_state]:
        ax.set_xlabel("Leitura", color="#AAAAAA", fontsize=9)
        ax.tick_params(colors="#AAAAAA")
        ax.set_xticks(steps)

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"Grafico salvo em: {output_path}")
    else:
        out = f"dashboard_{scenario.replace(' ', '_')}.png"
        fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"Grafico salvo em: {out}")

    plt.close(fig)


def _style_ax(ax: plt.Axes) -> None:
    ax.set_facecolor("#1A1F2C")
    ax.spines["bottom"].set_color("#444")
    ax.spines["left"].set_color("#444")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.label.set_color("#AAAAAA")
    ax.title.set_color("white")
    ax.tick_params(colors="#AAAAAA", labelsize=8)
    ax.grid(color="#2A2F3C", linestyle="--", linewidth=0.6, alpha=0.7)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera dashboard grafico da missao espacial")
    parser.add_argument("--scenario", default="Operacao nominal", choices=list(SCENARIOS))
    parser.add_argument("--steps",    type=int, default=12, help="Numero de leituras a simular")
    parser.add_argument("--output",   default=None,         help="Caminho do arquivo PNG de saida")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Simulando {args.steps} leituras — cenario: {args.scenario} ...")
    history = collect_history(args.scenario, args.steps)
    plot_dashboard(history, args.output)


if __name__ == "__main__":
    main()
