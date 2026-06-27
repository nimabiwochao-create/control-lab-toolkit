#!/usr/bin/env bash
set -euo pipefail

python -m control_lab sweep \
  --target-rpm 1200 \
  --load 0.10 \
  --kp 0.0008,0.0010,0.0012 \
  --ki 0.0015,0.0020,0.0025 \
  --kd 0.00004,0.00008 \
  --csv examples/sweep.csv
