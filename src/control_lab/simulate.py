from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path

from .filters import ExponentialMovingAverage
from .metrics import StepMetrics, summarize_step_response
from .pid import PIDController
from .plant import DCMotorPlant


@dataclass(frozen=True, slots=True)
class SimulationResult:
    times: list[float]
    commands: list[float]
    measurements: list[float]
    speeds: list[float]
    metrics: StepMetrics


def run_motor_step(
    target_rpm: float,
    seconds: float = 4.0,
    dt: float = 0.01,
    load: float = 0.0,
    noise_rpm: float = 0.0,
    seed: int = 7,
) -> SimulationResult:
    if seconds <= 0:
        raise ValueError("seconds must be positive")
    if target_rpm <= 0:
        raise ValueError("target_rpm must be positive")

    rng = random.Random(seed)
    controller = PIDController(kp=0.0012, ki=0.0025, kd=0.00008, dt=dt)
    plant = DCMotorPlant()
    sensor_filter = ExponentialMovingAverage(alpha=0.25)

    times: list[float] = []
    commands: list[float] = []
    measurements: list[float] = []
    speeds: list[float] = []

    steps = int(seconds / dt)
    for step in range(steps + 1):
        t = step * dt
        noisy_speed = plant.speed_rpm + rng.gauss(0.0, noise_rpm)
        measurement = sensor_filter.update(noisy_speed)
        command = controller.update(target_rpm, measurement)
        speed = plant.step(command, dt, load=load)

        times.append(t)
        commands.append(command)
        measurements.append(measurement)
        speeds.append(speed)

    metrics = summarize_step_response(times, speeds, target_rpm)
    return SimulationResult(times, commands, measurements, speeds, metrics)


def write_csv(path: Path, result: SimulationResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_s", "command", "measurement_rpm", "speed_rpm"])
        for row in zip(result.times, result.commands, result.measurements, result.speeds):
            writer.writerow([f"{row[0]:.4f}", f"{row[1]:.5f}", f"{row[2]:.3f}", f"{row[3]:.3f}"])

