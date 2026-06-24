from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PIDController:
    """Discrete PID controller with simple clamping anti-windup."""

    kp: float
    ki: float
    kd: float
    dt: float
    output_min: float = 0.0
    output_max: float = 1.0
    _integral: float = field(default=0.0, init=False, repr=False)
    _previous_error: float | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.dt <= 0:
            raise ValueError("dt must be positive")
        if self.output_min >= self.output_max:
            raise ValueError("output_min must be less than output_max")
        self.reset()

    def reset(self) -> None:
        self._integral = 0.0
        self._previous_error = None

    def update(self, target: float, measurement: float) -> float:
        error = target - measurement
        derivative = 0.0
        if self._previous_error is not None:
            derivative = (error - self._previous_error) / self.dt

        proposed_integral = self._integral + error * self.dt
        raw = self.kp * error + self.ki * proposed_integral + self.kd * derivative
        output = min(self.output_max, max(self.output_min, raw))

        saturated_high = raw > self.output_max and error > 0
        saturated_low = raw < self.output_min and error < 0
        if not (saturated_high or saturated_low):
            self._integral = proposed_integral

        self._previous_error = error
        return output
