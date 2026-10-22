"""Inspectable group/time evaluation without an estimator dependency."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from statistics import fmean


@dataclass(frozen=True)
class Observation:
    event_id: str
    entity_id: str
    observed_at: datetime
    feature_available_at: datetime
    label_available_at: datetime
    feature: float
    target: float


def _aware(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("timestamps must be aware")
    return value.astimezone(UTC)


def _finite(value: float) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_observations(rows: list[Observation]) -> None:
    seen: set[str] = set()
    for row in rows:
        if any(
            not isinstance(value, str) or not value or value != value.strip()
            for value in (row.event_id, row.entity_id)
        ):
            raise ValueError("identities must be nonempty trimmed text")
        if row.event_id in seen:
            raise ValueError("duplicate event id")
        seen.add(row.event_id)
        observed, feature_at, label_at = map(
            _aware, (row.observed_at, row.feature_available_at, row.label_available_at)
        )
        if feature_at > observed:
            raise ValueError("feature unavailable at prediction time")
        if label_at < observed:
            raise ValueError("label availability precedes observation")
        if not _finite(row.feature) or not _finite(row.target):
            raise ValueError("features and targets must be finite numbers")


def group_split(
    rows: list[Observation], held_out: set[str]
) -> tuple[list[Observation], list[Observation]]:
    validate_observations(rows)
    entities = {row.entity_id for row in rows}
    if not held_out or not held_out <= entities:
        raise ValueError("held-out entities must be a nonempty known subset")
    training = [row for row in rows if row.entity_id not in held_out]
    validation = [row for row in rows if row.entity_id in held_out]
    if not training or not validation:
        raise ValueError("training and validation must both be nonempty")
    return training, validation


def time_split(
    rows: list[Observation],
    cutoff: datetime,
    gap: timedelta = timedelta(0),
    end: datetime | None = None,
) -> tuple[list[Observation], list[Observation], int]:
    validate_observations(rows)
    cutoff = _aware(cutoff)
    end = _aware(end) if end is not None else None
    if gap < timedelta(0) or (end is not None and end <= cutoff):
        raise ValueError("gap must be nonnegative and end must follow cutoff")
    training = [
        row
        for row in rows
        if _aware(row.observed_at) < cutoff and _aware(row.label_available_at) < cutoff - gap
    ]
    validation = [
        row
        for row in rows
        if _aware(row.observed_at) >= cutoff and (end is None or _aware(row.observed_at) < end)
    ]
    if not training or not validation:
        raise ValueError("training and validation must both be nonempty")
    return training, validation, len(rows) - len(training) - len(validation)


def fit_mean(values: list[float]) -> float:
    if not values or not all(_finite(value) for value in values):
        raise ValueError("mean requires nonempty finite numbers")
    result = fmean(values)
    if not math.isfinite(result):
        raise ValueError("mean overflowed")
    return result


def mae(actual: list[float], predicted: list[float]) -> float:
    if (
        not actual
        or len(actual) != len(predicted)
        or not all(_finite(value) for value in actual + predicted)
    ):
        raise ValueError("MAE requires equal nonempty finite vectors")
    return fit_mean([abs(a - p) for a, p in zip(actual, predicted, strict=True)])


def evaluate_baseline(
    training: list[Observation], validation: list[Observation]
) -> dict[str, object]:
    validate_observations(training + validation)
    prediction = fit_mean([row.target for row in training])
    score = mae([row.target for row in validation], [prediction] * len(validation))
    return {
        "train_ids": [row.event_id for row in training],
        "validation_ids": [row.event_id for row in validation],
        "train_count": len(training),
        "validation_count": len(validation),
        "train_target_mean": prediction,
        "mae": score,
    }


if __name__ == "__main__":
    t = datetime(2026, 1, 1, tzinfo=UTC)
    rows = [
        Observation("A1", "A", t, t, t, 2.0, 0.0),
        Observation("B1", "B", t, t, t, 4.0, 0.0),
        Observation("C1", "C", t + timedelta(days=2), t, t + timedelta(days=3), 100.0, 100.0),
    ]
    training, validation = group_split(rows, {"C"})
    report = evaluate_baseline(training, validation)
    assert report["train_target_mean"] == 0.0 and report["mae"] == 100.0
    print(report)
