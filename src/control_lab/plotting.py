from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Telemetry:
    times: list[float]
    commands: list[float]
    measurements: list[float]
    speeds: list[float]


def read_telemetry_csv(path: Path) -> Telemetry:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        times: list[float] = []
        commands: list[float] = []
        measurements: list[float] = []
        speeds: list[float] = []
        for row in reader:
            times.append(float(row["time_s"]))
            commands.append(float(row["command"]))
            measurements.append(float(row["measurement_rpm"]))
            speeds.append(float(row["speed_rpm"]))

    if not times:
        raise ValueError("telemetry CSV has no samples")

    return Telemetry(times, commands, measurements, speeds)


def write_step_response_svg(
    telemetry: Telemetry,
    output_path: Path,
    target_rpm: float | None = None,
    width: int = 960,
    height: int = 540,
) -> None:
    if width < 320 or height < 240:
        raise ValueError("plot size is too small")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    margin_left = 76
    margin_right = 32
    margin_top = 44
    margin_bottom = 64
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    max_time = max(telemetry.times)
    rpm_values = telemetry.speeds + telemetry.measurements
    if target_rpm is not None:
        rpm_values.append(target_rpm)
    max_rpm = max(rpm_values) * 1.12
    if max_rpm <= 0:
        max_rpm = 1.0

    def x_for(time_s: float) -> float:
        return margin_left + (time_s / max_time) * plot_width if max_time else margin_left

    def y_for(rpm: float) -> float:
        return margin_top + plot_height - (rpm / max_rpm) * plot_height

    def polyline(values: list[float]) -> str:
        return " ".join(
            f"{x_for(time_s):.2f},{y_for(value):.2f}"
            for time_s, value in zip(telemetry.times, values)
        )

    grid_lines: list[str] = []
    for index in range(6):
        fraction = index / 5
        y = margin_top + plot_height - fraction * plot_height
        rpm = fraction * max_rpm
        grid_lines.append(
            f'<line x1="{margin_left}" y1="{y:.2f}" x2="{width - margin_right}" y2="{y:.2f}" '
            'stroke="#d7dde5" stroke-width="1"/>'
        )
        grid_lines.append(
            f'<text x="{margin_left - 12}" y="{y + 5:.2f}" text-anchor="end" '
            'font-size="13" fill="#44505f">'
            f"{rpm:.0f}</text>"
        )

    command_points = " ".join(
        f"{x_for(time_s):.2f},{margin_top + plot_height - command * plot_height:.2f}"
        for time_s, command in zip(telemetry.times, telemetry.commands)
    )

    target_line = ""
    if target_rpm is not None:
        target_y = y_for(target_rpm)
        target_line = (
            f'<line x1="{margin_left}" y1="{target_y:.2f}" x2="{width - margin_right}" '
            f'y2="{target_y:.2f}" stroke="#ef4444" stroke-width="2" stroke-dasharray="7 7"/>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <text x="{margin_left}" y="28" font-size="22" font-weight="700" fill="#172033">Motor Step Response</text>
  <text x="{margin_left}" y="{height - 18}" font-size="14" fill="#44505f">time (s)</text>
  <text x="20" y="{margin_top + 20}" font-size="14" fill="#44505f" transform="rotate(-90 20 {margin_top + 20})">RPM</text>
  {"".join(grid_lines)}
  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" stroke="#172033" stroke-width="1.5"/>
  <line x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" stroke="#172033" stroke-width="1.5"/>
  {target_line}
  <polyline points="{polyline(telemetry.measurements)}" fill="none" stroke="#94a3b8" stroke-width="2" opacity="0.75"/>
  <polyline points="{polyline(telemetry.speeds)}" fill="none" stroke="#2563eb" stroke-width="3"/>
  <polyline points="{command_points}" fill="none" stroke="#16a34a" stroke-width="2.5" opacity="0.85"/>
  <g font-size="14" fill="#172033">
    <rect x="{width - 245}" y="34" width="188" height="86" rx="6" fill="#ffffff" stroke="#d7dde5"/>
    <line x1="{width - 225}" y1="58" x2="{width - 185}" y2="58" stroke="#2563eb" stroke-width="3"/>
    <text x="{width - 175}" y="63">simulated RPM</text>
    <line x1="{width - 225}" y1="84" x2="{width - 185}" y2="84" stroke="#94a3b8" stroke-width="2"/>
    <text x="{width - 175}" y="89">measured RPM</text>
    <line x1="{width - 225}" y1="110" x2="{width - 185}" y2="110" stroke="#16a34a" stroke-width="2.5"/>
    <text x="{width - 175}" y="115">PWM command</text>
  </g>
</svg>
"""
    output_path.write_text(svg, encoding="utf-8")

