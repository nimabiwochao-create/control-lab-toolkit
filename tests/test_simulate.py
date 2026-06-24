import unittest

from tests.conftest_imports import SRC  # noqa: F401
from control_lab.simulate import run_motor_step


class SimulationTest(unittest.TestCase):
    def test_motor_reaches_near_target(self) -> None:
        result = run_motor_step(target_rpm=1200.0, seconds=4.0)

        self.assertGreater(result.metrics.final_rpm, 1100.0)
        self.assertLess(result.metrics.final_rpm, 1300.0)
        self.assertLess(result.metrics.overshoot_percent, 15.0)

    def test_load_reduces_final_speed(self) -> None:
        no_load = run_motor_step(target_rpm=1500.0, seconds=3.0, load=0.0)
        loaded = run_motor_step(target_rpm=1500.0, seconds=3.0, load=0.25)

        self.assertLess(loaded.metrics.final_rpm, no_load.metrics.final_rpm)


if __name__ == "__main__":
    unittest.main()
