from __future__ import annotations

import argparse
from datetime import datetime

from mission_monitor.display import print_snapshot
from mission_monitor.monitor import MissionMonitor
from mission_monitor.report import save_report
from mission_monitor.scenarios import SCENARIOS


def run_steps(monitor: MissionMonitor, steps: int) -> None:
    for _ in range(max(1, steps)):
        snapshot = monitor.next_snapshot()
        print_snapshot(snapshot)


def interactive_loop(monitor: MissionMonitor) -> None:
    last_snapshot = None

    while True:
        print("\nMenu:")
        print("1 - Gerar nova leitura")
        print("2 - Trocar cenario")
        print("3 - Exportar ultimo relatorio (JSON)")
        print("4 - Gerar grafico do historico")
        print("0 - Sair")
        try:
            choice = input("Escolha: ").strip()
        except EOFError:
            print("\nEntrada nao disponivel neste ambiente. Use --steps para modo automatico.")
            break

        if choice == "1":
            last_snapshot = monitor.next_snapshot()
            print_snapshot(last_snapshot)

        elif choice == "2":
            print("\nCenarios disponiveis:")
            for name in SCENARIOS:
                print(f"  - {name}")
            scenario_name = input("Digite o cenario: ").strip()
            try:
                monitor.set_scenario(scenario_name)
                last_snapshot = None
                print("Cenario atualizado.")
            except ValueError as exc:
                print(exc)

        elif choice == "3":
            if last_snapshot is None:
                print("Gere uma leitura antes de exportar.")
                continue
            file_name = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_report(last_snapshot, file_name)

        elif choice == "4":
            steps_input = input("Quantas leituras para o grafico? [12]: ").strip()
            n = int(steps_input) if steps_input.isdigit() else 12
            try:
                from charts import collect_history, plot_dashboard
                history = collect_history(monitor.scenario.name, n)
                plot_dashboard(history)
            except ImportError:
                print("Instale matplotlib para gerar graficos: pip install matplotlib")

        elif choice == "0":
            break

        else:
            print("Opcao invalida.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor de missao espacial — Global Solution")
    parser.add_argument("--scenario", default="Operacao nominal", choices=list(SCENARIOS))
    parser.add_argument("--steps", type=int, default=0, help="Roda em modo automatico por N leituras.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    monitor = MissionMonitor(args.scenario)

    if args.steps > 0:
        run_steps(monitor, args.steps)
        return

    interactive_loop(monitor)


if __name__ == "__main__":
    main()
