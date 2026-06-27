# PID Tuning Notes

## Lab Goal

Tune a motor speed loop so the measured RPM reaches the target quickly without
large overshoot. Start in simulation, then copy conservative gains to firmware.

## Workflow

1. Run a baseline step response with no load.
2. Increase `kp` until the motor responds quickly but does not oscillate.
3. Add a small `ki` term to remove steady-state error.
4. Add `kd` only if overshoot is too high or the response is noisy.
5. Add load in simulation and confirm the controller still settles.
6. Flash firmware with lower gains than simulation, then tune upward on hardware.

## Sweep-Based Tuning

Use the sweep command to compare candidate gains before touching hardware. The
top row in `examples/sweep.csv` is not automatically perfect, but it is a good
starting point because it balances final error, overshoot, and settling time.

When moving from simulation to hardware, start below the simulated gains and
increase carefully while watching telemetry.

## Safety Notes

- Clamp PWM output before writing to the driver.
- Keep an emergency stop path when testing real motors.
- Log telemetry during tuning instead of relying only on sound or feel.
- Expect encoder noise; filter measurements before changing gains.
