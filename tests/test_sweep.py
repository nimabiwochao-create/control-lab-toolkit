import tempfile
import unittest
from pathlib import Path

from tests.conftest_imports import SRC  # noqa: F401
from control_lab.sweep import parse_float_list, run_pid_sweep, write_sweep_csv


class SweepTest(unittest.TestCase):
    def test_parse_float_list(self) -> None:
        self.assertEqual(parse_float_list("0.1, 0.2,0.3"), [0.1, 0.2, 0.3])

    def test_sweep_returns_sorted_rows(self) -> None:
        rows = run_pid_sweep(
            target_rpm=1000.0,
            kp_values=[0.0008, 0.0012],
            ki_values=[0.0015],
            kd_values=[0.00004],
            seconds=1.0,
        )

        self.assertEqual(len(rows), 2)
        self.assertLessEqual(abs(rows[0].final_error_rpm), abs(rows[-1].final_error_rpm))

    def test_writes_sweep_csv(self) -> None:
        rows = run_pid_sweep(
            target_rpm=1000.0,
            kp_values=[0.0012],
            ki_values=[0.0020],
            kd_values=[0.00004],
            seconds=0.2,
        )
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "sweep.csv"
            write_sweep_csv(csv_path, rows)
            text = csv_path.read_text(encoding="utf-8")

        self.assertIn("kp,ki,kd", text)
        self.assertIn("overshoot_percent", text)


if __name__ == "__main__":
    unittest.main()
