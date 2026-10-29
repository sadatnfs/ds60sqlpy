"""Compatibility exports; canonical implementation is ds60_spark_likelihood."""

from importlib import import_module as _import_module

_canonical = _import_module("ds60_spark_likelihood")
__all__ = _canonical.__all__
for _name in __all__:
    globals()[_name] = getattr(_canonical, _name)
