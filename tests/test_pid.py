import unittest

from tests.conftest_imports import SRC  # noqa: F401
from control_lab import PIDController


class PIDControllerTest(unittest.TestCase):
    def test_output_is_clamped(self) -> None:
        controller = PIDController(kp=10.0, ki=0.0, kd=0.0, dt=0.1, output_min=-1.0, output_max=1.0)

        self.assertEqual(controller.update(target=10.0, measurement=0.0), 1.0)
        self.assertEqual(controller.update(target=-10.0, measurement=0.0), -1.0)

    def test_integral_recovers_after_reset(self) -> None:
        controller = PIDController(kp=0.0, ki=1.0, kd=0.0, dt=1.0, output_min=0.0, output_max=100.0)

        self.assertEqual(controller.update(target=10.0, measurement=0.0), 10.0)
        controller.reset()
        self.assertEqual(controller.update(target=10.0, measurement=0.0), 10.0)


if __name__ == "__main__":
    unittest.main()
