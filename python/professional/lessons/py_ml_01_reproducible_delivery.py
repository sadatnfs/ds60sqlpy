"""python-ml-01 learner lab: reproducible local model delivery."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence

Scalar = str | int | float | bool | None


def canonical_record_hash(records: Sequence[Mapping[str, Scalar]]) -> str:
    """Return an order-independent SHA-256 snapshot identifier.

    TODO: require a unique ``record_id``, sort records by that ID, serialize
    canonical JSON, and hash UTF-8 bytes.
    """

    raise NotImplementedError("complete canonical_record_hash")


def hash_text(text: str) -> str:
    """Worked example: hashes identify bytes, not semantic equivalence."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def schema_compatible(
    expected: Sequence[tuple[str, str]],
    actual: Sequence[tuple[str, str]],
) -> bool:
    """TODO: require exact ordered names and types for this strict model."""

    raise NotImplementedError("complete schema_compatible")


def self_check() -> None:
    left = json.dumps({"x": 1, "y": 2})
    right = json.dumps({"y": 2, "x": 1})
    print("Worked raw hashes differ:", hash_text(left) != hash_text(right))
    for label, call in (
        (
            "canonical data snapshot",
            lambda: canonical_record_hash([{"record_id": "b", "x": 2}, {"record_id": "a", "x": 1}]),
        ),
        (
            "feature compatibility",
            lambda: schema_compatible([("x", "float")], [("x", "float")]),
        ),
    ):
        try:
            print(label, "->", call())
        except NotImplementedError:
            print("TODO:", label)


if __name__ == "__main__":
    self_check()
