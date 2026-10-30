"""Lightweight Python frontend for prepared Spark/JVM/native TMBad artifacts.

Importing this package does not import PySpark, create a Spark session, compile
models, load native libraries, or start processes. PySpark is needed only when
using the DataFrame API.
"""

from ._json import ContractError
from .client import FittedModel, GroupedModels, SparkTMBad
from .parameters import PreparedParameters
from .runtime import PreparedRuntime
from .spec import ModelSpec

__version__ = "0.2.0"

__all__ = [
    "ContractError",
    "FittedModel",
    "GroupedModels",
    "ModelSpec",
    "PreparedParameters",
    "PreparedRuntime",
    "SparkTMBad",
]
