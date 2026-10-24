"""Reference implementation for python-stats-01 using deterministic local data."""

from __future__ import annotations

import csv
import itertools
import math
import random
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist, mean, stdev
from typing import Literal, cast

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "data" / ("experiment_outcomes.csv")
Variant = Literal["control", "treatment"]
ClaimScope = Literal["causal", "associational"]


@dataclass(frozen=True)
class Observation:
    participant_id: str
    variant: Variant
    pre_score: float
    outcome: float
    completed: bool


@dataclass(frozen=True)
class Interval:
    lower: float
    estimate: float
    upper: float
    confidence: float


@dataclass(frozen=True)
class PermutationResult:
    observed_difference: float
    p_value: float
    permutations: int
    exact: bool


@dataclass(frozen=True)
class ExperimentPlan:
    assignment_unit: str
    primary_metric: str
    minimum_sample_per_arm: int
    alpha: float = 0.05

    def __post_init__(self) -> None:
        if not self.assignment_unit.strip() or not self.primary_metric.strip():
            raise ValueError("assignment unit and primary metric are required")
        if self.minimum_sample_per_arm < 2:
            raise ValueError("each arm needs at least two planned observations")
        if not 0 < self.alpha < 1:
            raise ValueError("alpha must be between zero and one")


def load_observations(path: Path = FIXTURE) -> list[Observation]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    observations: list[Observation] = []
    for row in rows:
        variant_text = row["variant"]
        if variant_text not in {"control", "treatment"}:
            raise ValueError(f"unknown variant: {variant_text}")
        variant = cast(Variant, variant_text)
        completed = row["completed"].lower()
        if completed not in {"true", "false"}:
            raise ValueError("completed must be true or false")
        observations.append(
            Observation(
                participant_id=row["participant_id"],
                variant=variant,
                pre_score=float(row["pre_score"]),
                outcome=float(row["outcome"]),
                completed=completed == "true",
            )
        )
    return observations


def split_outcomes(
    observations: Sequence[Observation],
) -> tuple[list[float], list[float]]:
    control = [
        observation.outcome
        for observation in observations
        if observation.completed and observation.variant == "control"
    ]
    treatment = [
        observation.outcome
        for observation in observations
        if observation.completed and observation.variant == "treatment"
    ]
    if len(control) < 2 or len(treatment) < 2:
        raise ValueError("each completed group needs at least two observations")
    return control, treatment


def difference_in_means(control: Sequence[float], treatment: Sequence[float]) -> float:
    if not control or not treatment:
        raise ValueError("both groups need observations")
    return mean(treatment) - mean(control)


def standardized_mean_difference(
    control: Sequence[float],
    treatment: Sequence[float],
) -> float:
    if len(control) < 2 or len(treatment) < 2:
        raise ValueError("effect size needs at least two observations per group")
    pooled_variance = (
        (len(control) - 1) * stdev(control) ** 2 + (len(treatment) - 1) * stdev(treatment) ** 2
    ) / (len(control) + len(treatment) - 2)
    if pooled_variance == 0:
        raise ValueError("standardized effect is undefined at zero variance")
    return difference_in_means(control, treatment) / math.sqrt(pooled_variance)


def bootstrap_difference_interval(
    control: Sequence[float],
    treatment: Sequence[float],
    *,
    resamples: int = 2_000,
    confidence: float = 0.95,
    seed: int = 20260730,
) -> Interval:
    if not control or not treatment:
        raise ValueError("both groups need observations")
    if resamples < 100:
        raise ValueError("use at least 100 bootstrap resamples")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between zero and one")
    generator = random.Random(seed)
    estimates: list[float] = []
    for _ in range(resamples):
        sampled_control = [generator.choice(control) for _ in control]
        sampled_treatment = [generator.choice(treatment) for _ in treatment]
        estimates.append(difference_in_means(sampled_control, sampled_treatment))
    estimates.sort()
    tail = (1.0 - confidence) / 2.0
    lower_index = max(0, math.floor(tail * resamples))
    upper_index = min(resamples - 1, math.ceil((1.0 - tail) * resamples) - 1)
    return Interval(
        lower=estimates[lower_index],
        estimate=difference_in_means(control, treatment),
        upper=estimates[upper_index],
        confidence=confidence,
    )


def permutation_test(
    control: Sequence[float],
    treatment: Sequence[float],
    *,
    maximum_exact: int = 100_000,
    monte_carlo_resamples: int = 10_000,
    seed: int = 20260730,
) -> PermutationResult:
    if not control or not treatment:
        raise ValueError("both groups need observations")
    pooled = tuple(control) + tuple(treatment)
    treatment_size = len(treatment)
    observed = difference_in_means(control, treatment)
    combination_count = math.comb(len(pooled), treatment_size)

    def permuted_difference(treatment_indices: set[int]) -> float:
        permuted_treatment = [
            value for index, value in enumerate(pooled) if index in treatment_indices
        ]
        permuted_control = [
            value for index, value in enumerate(pooled) if index not in treatment_indices
        ]
        return difference_in_means(permuted_control, permuted_treatment)

    if combination_count <= maximum_exact:
        extreme = 0
        total = 0
        for indices in itertools.combinations(range(len(pooled)), treatment_size):
            total += 1
            if abs(permuted_difference(set(indices))) >= abs(observed) - 1e-12:
                extreme += 1
        return PermutationResult(observed, extreme / total, total, True)

    generator = random.Random(seed)
    extreme = 0
    shuffled_indices = list(range(len(pooled)))
    for _ in range(monte_carlo_resamples):
        generator.shuffle(shuffled_indices)
        treatment_indices = set(shuffled_indices[:treatment_size])
        if abs(permuted_difference(treatment_indices)) >= abs(observed) - 1e-12:
            extreme += 1
    p_value = (extreme + 1) / (monte_carlo_resamples + 1)
    return PermutationResult(observed, p_value, monte_carlo_resamples, False)


def minimum_sample_per_arm(
    standardized_effect: float,
    *,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    if standardized_effect <= 0:
        raise ValueError("standardized_effect must be positive")
    if not 0 < alpha < 1 or not 0 < power < 1:
        raise ValueError("alpha and power must be between zero and one")
    normal = NormalDist()
    z_alpha = normal.inv_cdf(1 - alpha / 2)
    z_power = normal.inv_cdf(power)
    approximate = 2 * ((z_alpha + z_power) / standardized_effect) ** 2
    return math.ceil(approximate)


def holm_adjust(p_values: Sequence[float]) -> list[float]:
    if any(not 0 <= value <= 1 for value in p_values):
        raise ValueError("p-values must be between zero and one")
    count = len(p_values)
    ordered = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [0.0] * count
    running = 0.0
    for rank, (original_index, value) in enumerate(ordered):
        candidate = min(1.0, (count - rank) * value)
        running = max(running, candidate)
        adjusted[original_index] = running
    return adjusted


def standardized_balance_difference(
    control: Sequence[float],
    treatment: Sequence[float],
) -> float:
    return standardized_mean_difference(control, treatment)


def per_look_alpha(alpha: float, planned_looks: int) -> float:
    if not 0 < alpha < 1 or planned_looks < 1:
        raise ValueError("alpha and planned_looks must be valid")
    return alpha / planned_looks


def claim_scope(
    *,
    randomized: bool,
    allocation_intact: bool,
    severe_attrition: bool,
) -> ClaimScope:
    if randomized and allocation_intact and not severe_attrition:
        return "causal"
    return "associational"


def main() -> int:
    observations = load_observations()
    control, treatment = split_outcomes(observations)
    interval = bootstrap_difference_interval(control, treatment)
    test = permutation_test(control, treatment)
    print("difference:", difference_in_means(control, treatment))
    print("standardized effect:", round(standardized_mean_difference(control, treatment), 3))
    print("bootstrap interval:", interval)
    print("permutation:", test)
    print("sample per arm for d=0.5:", minimum_sample_per_arm(0.5))
    print("Holm:", holm_adjust([0.01, 0.04, 0.03]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
