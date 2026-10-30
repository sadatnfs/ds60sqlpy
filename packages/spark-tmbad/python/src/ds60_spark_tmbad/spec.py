"""Explicit native-field to DataFrame-column contracts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ._json import ContractError, copy_object, dumps, loads


def _name(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256 or "\x00" in value:
        raise ContractError(f"{field} must be a nonempty string without null characters")
    return value


def column_map(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{field} must map native field names to Spark column names")
    return {_name(key, field): _name(item, field) for key, item in value.items()}


def column_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, (list, tuple)):
        raise ContractError(f"{field} must be a list of column names")
    result = [_name(item, field) for item in value]
    if len(set(result)) != len(result):
        raise ContractError(f"{field} must not contain duplicate columns")
    return result


class ModelSpec:
    """Choose a prepared model and map its declared fields to Spark columns.

    ``id_columns`` identify rows, ``group_columns`` identify complete independent
    units, and ``order_columns`` define order within a unit. They are distinct
    from the native model's numerical inputs in ``columns``.
    """

    def __init__(
        self,
        model_id: str,
        columns: Mapping[str, str],
        *,
        id_columns: Sequence[str],
        group_columns: Sequence[str] = (),
        order_columns: Sequence[str] = (),
        weight_column: str | None = None,
    ) -> None:
        value = {
            "model_id": _name(model_id, "model_id"),
            "columns": column_map(columns, "columns"),
            "id_columns": column_list(id_columns, "id_columns"),
            "group_columns": column_list(group_columns, "group_columns"),
            "order_columns": column_list(order_columns, "order_columns"),
            "weight_column": None
            if weight_column is None
            else _name(weight_column, "weight_column"),
        }
        if not value["id_columns"]:
            raise ContractError("id_columns must contain at least one stable row identity column")
        if any(
            len(value[field]) > 64 for field in ("id_columns", "group_columns", "order_columns")
        ):
            raise ContractError("Identity, group and order keys allow at most 64 columns each")
        self._json = dumps(value)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> ModelSpec:
        obj = copy_object(value)
        fields = {
            "model_id",
            "columns",
            "id_columns",
            "group_columns",
            "order_columns",
            "weight_column",
        }
        unknown = set(obj) - fields
        if unknown:
            raise ContractError(f"Unknown model spec fields: {sorted(unknown)}")
        required = {"model_id", "columns", "id_columns"}
        if required - obj.keys():
            raise ContractError(f"Missing model spec fields: {sorted(required - obj.keys())}")
        return cls(**obj)

    @property
    def model_id(self) -> str:
        return self.to_dict()["model_id"]

    def to_dict(self) -> dict[str, Any]:
        return loads(self._json)

    def to_json(self) -> str:
        return self._json

    def __repr__(self) -> str:
        return f"ModelSpec({self.model_id!r}, columns={self.to_dict()['columns']!r})"

    def validate_descriptor(self, descriptor: Mapping[str, Any]) -> None:
        """Check declared fields and complete-unit structure before Spark execution."""
        value = self.to_dict()
        if descriptor.get("id") != self.model_id:
            raise ContractError("Model spec does not select this prepared descriptor")
        if set(value["columns"]) != set(descriptor["fit_fields"]):
            raise ContractError("columns must map exactly the prepared model's fit_fields")
        if descriptor["fit_kind"] == "unit" and not value["group_columns"]:
            raise ContractError("A complete-unit model requires explicit group_columns")
        if descriptor["ordered"] and not value["order_columns"]:
            raise ContractError("An ordered model requires explicit order_columns")
