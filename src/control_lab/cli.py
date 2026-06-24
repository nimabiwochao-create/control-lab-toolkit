from __future__ import annotations

import argparse
from pathlib import Path

from .plotting import read_telemetry_csv, write_step_response_svg
from .simulate import run_motor_step, write_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="control-lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    simulate = subparsers.add_parser("simulate", help="run a motor step-response experiment")
    simulate.add_argument("--target-rpm", type=float, default=1200.0)
    simulate.add_argument("--seconds", type=float, default=4.0)
    simulate.add_argument("--dt", type=float, default=0.01)
    simulate.add_argument("--load", type=float, default=0.0)
    simulate.add_argument("--noise", type=float, default=0.0)
    simulate.add_argument("--csv", type=Path)
    simulate.add_argument("--plot", type=Path, help="write an SVG step-response plot")

    plot = subparsers.add_parser("plot", help="render a telemetry CSV as an SVG plot")
    plot.add_argument("csv", type=Path)
    plot.add_argument("--target-rpm", type=float)
    plot.add_argument("--output", type=Path, default=Path("examples/run.svg"))

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "simulate":
        result = run_motor_step(
            target_rpm=args.target_rpm,
            seconds=args.seconds,
            dt=args.dt,
            load=args.load,
            noise_rpm=args.noise,
        )
        if args.csv:
            write_csv(args.csv, result)
        if args.plot:
            write_step_response_svg(
                telemetry=read_telemetry_csv(args.csv) if args.csv else _result_to_telemetry(result),
                output_path=args.plot,
                target_rpm=args.target_rpm,
            )

        settling = (
            f"{result.metrics.settling_time_s:.2f}s"
            if result.metrics.settling_time_s is not None
            else "not settled"
        )
        print(
            "target_rpm="
            f"{args.target_rpm:.1f} final_rpm={result.metrics.final_rpm:.1f} "
            f"overshoot={result.metrics.overshoot_percent:.1f}% settling_time={settling}"
        )
        return 0

    if args.command == "plot":
        telemetry = read_telemetry_csv(args.csv)
        write_step_response_svg(telemetry, args.output, target_rpm=args.target_rpm)
        print(f"wrote plot: {args.output}")
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


def _result_to_telemetry(result):
    from .plotting import Telemetry

    return Telemetry(
        times=result.times,
        commands=result.commands,
        measurements=result.measurements,
        speeds=result.speeds,
    )
