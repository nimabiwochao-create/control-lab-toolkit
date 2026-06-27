from __future__ import annotations

import csv
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Iterable

from .filters import ExponentialMovingAverage
from .metrics import summarize_step_response
from .pid import PIDController
from .plant import DCMotorPlant


@dataclass(frozen=True, slots=True)
class SweepRow:
    kp: float
    ki: float
    kd: float
    final_rpm: float
    final_error_rpm: float
    overshoot_percent: float
    settling_time_s: float | None


def parse_float_list(value: str) -> list[float]:
    values = [float(part.strip()) for part in value.split(",") if part.strip()]
    if not values:
        raise ValueError("at least one value is required")
    return values


def run_pid_sweep(
    target_rpm: float,
    kp_values: Iterable[float],
    ki_values: Iterable[float],
    kd_values: Iterable[float],
    seconds: float = 4.0,
    dt: float = 0.01,
    load: float = 0.0,
) -> list[SweepRow]:
    if target_rpm <= 0:
        raise ValueError("target_rpm must be positive")
    if seconds <= 0:
        raise ValueError("seconds must be positive")

    rows: list[SweepRow] = []
    for kp, ki, kd in product(kp_values, ki_values, kd_values):
        controller = PIDController(kp=kp, ki=ki, kd=kd, dt=dt)
        plant = DCMotorPlant()
        sensor_filter = ExponentialMovingAverage(alpha=0.25)
        times: list[float] = []
        speeds: list[float] = []

        for step in range(int(seconds / dt) + 1):
            time_s = step * dt
            measurement = sensor_filter.update(plant.speed_rpm)
            command = controller.update(target_rpm, measurement)
            speed = plant.step(command, dt, load=load)
            times.append(time_s)
            speeds.append(speed)

        metrics = summarize_step_response(times, speeds, target_rpm)
        rows.append(
            SweepRow(
                kp=kp,
                ki=ki,
                kd=kd,
                final_rpm=metrics.final_rpm,
                final_error_rpm=target_rpm - metrics.final_rpm,
                overshoot_percent=metrics.overshoot_percent,
                settling_time_s=metrics.settling_time_s,
            )
        )

    return sorted(rows, key=_score_row)


def write_sweep_csv(path: Path, rows: list[SweepRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "kp",
                "ki",
                "kd",
                "final_rpm",
                "final_error_rpm",
                "overshoot_percent",
                "settling_time_s",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    f"{row.kp:.6f}",
                    f"{row.ki:.6f}",
                    f"{row.kd:.6f}",
                    f"{row.final_rpm:.3f}",
                    f"{row.final_error_rpm:.3f}",
                    f"{row.overshoot_percent:.3f}",
                    "" if row.settling_time_s is None else f"{row.settling_time_s:.3f}",
                ]
            )


def _score_row(row: SweepRow) -> tuple[float, float, float]:
    settling_penalty = row.settling_time_s if row.settling_time_s is not None else 999.0
    return (abs(row.final_error_rpm), row.overshoot_percent, settling_penalty)

