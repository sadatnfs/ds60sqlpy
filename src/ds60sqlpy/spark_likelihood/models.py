"""Compatibility alias for ds60_spark_likelihood.models."""

import sys as _sys
from importlib import import_module as _import_module

_sys.modules[__name__] = _import_module("ds60_spark_likelihood.models")
