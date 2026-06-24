import tempfile
import unittest
from pathlib import Path

from tests.conftest_imports import SRC  # noqa: F401
from control_lab.plotting import read_telemetry_csv, write_step_response_svg
from control_lab.simulate import run_motor_step, write_csv


class PlottingTest(unittest.TestCase):
    def test_writes_svg_from_telemetry_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            csv_path = tmp_path / "run.csv"
            svg_path = tmp_path / "run.svg"

            write_csv(csv_path, run_motor_step(target_rpm=1000.0, seconds=0.2))
            telemetry = read_telemetry_csv(csv_path)
            write_step_response_svg(telemetry, svg_path, target_rpm=1000.0)

            svg = svg_path.read_text(encoding="utf-8")
            self.assertIn("<svg", svg)
            self.assertIn("Motor Step Response", svg)
            self.assertIn("simulated RPM", svg)


if __name__ == "__main__":
    unittest.main()
