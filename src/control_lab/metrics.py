from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class StepMetrics:
    final_rpm: float
    overshoot_percent: float
    settling_time_s: float | None


def summarize_step_response(
    times: Sequence[float],
    speeds: Sequence[float],
    target_rpm: float,
    settling_band: float = 0.05,
) -> StepMetrics:
    if len(times) != len(speeds):
        raise ValueError("times and speeds must have the same length")
    if not times:
        raise ValueError("at least one sample is required")
    if target_rpm <= 0:
        raise ValueError("target_rpm must be positive")

    final_rpm = speeds[-1]
    peak = max(speeds)
    overshoot_percent = max(0.0, ((peak - target_rpm) / target_rpm) * 100.0)
    lower = target_rpm * (1.0 - settling_band)
    upper = target_rpm * (1.0 + settling_band)

    settling_time_s = None
    for index, speed in enumerate(speeds):
        if lower <= speed <= upper and all(lower <= later <= upper for later in speeds[index:]):
            settling_time_s = times[index]
            break

    return StepMetrics(final_rpm, overshoot_percent, settling_time_s)

