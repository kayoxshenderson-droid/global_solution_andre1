from __future__ import annotations

import unittest

from mission_monitor.monitor import MissionMonitor


class MissionMonitorTests(unittest.TestCase):
    def test_nominal_scenario_stays_operational(self) -> None:
        monitor = MissionMonitor("Operacao nominal")
        snapshot = monitor.next_snapshot()

        self.assertEqual(snapshot.mission_state, "OPERACIONAL")
        self.assertGreaterEqual(snapshot.health_score, 80.0)

    def test_emergency_scenario_generates_alerts(self) -> None:
        monitor = MissionMonitor("Emergencia energetica")
        snapshot = monitor.next_snapshot()

        self.assertTrue(snapshot.alerts)
        self.assertIn(snapshot.mission_state, {"ATENCAO", "CRITICO"})


if __name__ == "__main__":
    unittest.main()
