"""Independent custom likelihood estimation with optional Spark and Torch backends.

Importing this module does not import Spark, Torch, NumPy, SciPy or a classroom.
"""

from ._version import __version__ as __version__
from .contracts import (
    ObjectiveError,
    ObjectiveEvaluation,
    PartitionSummary,
    combine_summaries,
    finite_vector,
    parameter_digest,
)
from .optimization import minimize_lbfgsb
from .prediction import predict_batch
from .registry import (
    PredictionTarget,
    RegisteredModel,
    describe_model,
    register_model_factory,
    resolve_model,
)
from .spark_backend import SparkObjective
from .spark_units import SparkUnitObjective, UnitObjectiveEvaluation
from .torch_backend import TorchLoss
from .unit_backend import CompleteUnit, TorchUnitLoss

__all__ = [
    "__version__",
    "ObjectiveError",
    "ObjectiveEvaluation",
    "PartitionSummary",
    "combine_summaries",
    "finite_vector",
    "parameter_digest",
    "minimize_lbfgsb",
    "predict_batch",
    "PredictionTarget",
    "RegisteredModel",
    "describe_model",
    "register_model_factory",
    "resolve_model",
    "SparkObjective",
    "SparkUnitObjective",
    "UnitObjectiveEvaluation",
    "TorchLoss",
    "TorchUnitLoss",
    "CompleteUnit",
]
