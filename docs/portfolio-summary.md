# Portfolio Summary

## What This Shows

- Control theory basics: PID, settling time, overshoot, saturation
- Embedded thinking: PWM output, encoder input, fixed sample time, telemetry
- Software discipline: package layout, CLI, tests, docs, reproducible examples

## Interview Talking Points

- Why output clamping needs anti-windup
- Why measured RPM should be filtered before feeding the controller
- How simulation gains differ from safe hardware gains
- How CSV telemetry helps tune a physical system

## Next Improvements

- Add a serial parser that reads Arduino telemetry into Python
- Add a live plotter for command and RPM
- Add parameter sweep scripts for PID tuning
- Add a hardware wiring diagram

