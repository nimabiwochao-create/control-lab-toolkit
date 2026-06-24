#!/usr/bin/env bash
set -euo pipefail

python -m control_lab simulate --target-rpm 1200 --seconds 4 --load 0.10 --noise 10 --csv examples/run.csv

