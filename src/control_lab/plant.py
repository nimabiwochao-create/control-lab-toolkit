from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DCMotorPlant:
    """First-order DC motor speed model.

    The model is intentionally simple:

        speed_dot = (target_speed - speed) / tau

    A normalized command in [0, 1] maps to max_rpm. The load parameter removes a
    fraction of available torque, which makes the controller work harder.
    """

    max_rpm: float = 3000.0
    tau: float = 0.28
    speed_rpm: float = 0.0

    def __post_init__(self) -> None:
        if self.max_rpm <= 0:
            raise ValueError("max_rpm must be positive")
        if self.tau <= 0:
            raise ValueError("tau must be positive")

    def step(self, command: float, dt: float, load: float = 0.0) -> float:
        if dt <= 0:
            raise ValueError("dt must be positive")

        command = min(1.0, max(0.0, command))
        load = min(0.95, max(0.0, load))
        target_speed = self.max_rpm * command * (1.0 - load)
        self.speed_rpm += (target_speed - self.speed_rpm) * (dt / self.tau)
        return self.speed_rpm

