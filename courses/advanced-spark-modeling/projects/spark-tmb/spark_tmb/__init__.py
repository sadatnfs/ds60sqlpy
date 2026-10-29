"""Scoped prepared TMB companion: import never starts R, Spark or compilation."""

from .registry import ModelContractError, load_registry, payload_for
from .runtime import describe_prepared, evaluate_prepared, fit_prepared, predict_prepared
from .spark import SparkTMBObjective

__all__ = [
    "ModelContractError",
    "SparkTMBObjective",
    "describe_prepared",
    "evaluate_prepared",
    "predict_prepared",
    "fit_prepared",
    "load_registry",
    "payload_for",
]
