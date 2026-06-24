"""Control lab simulation and embedded control helpers."""

from .filters import ExponentialMovingAverage
from .metrics import StepMetrics
from .pid import PIDController
from .plant import DCMotorPlant

__all__ = [
    "DCMotorPlant",
    "ExponentialMovingAverage",
    "PIDController",
    "StepMetrics",
]

