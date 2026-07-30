"""python-stats-01 learner lab: resampling and experiment decisions."""

from __future__ import annotations

from collections.abc import Sequence
from statistics import mean
from typing import Literal


def difference_in_means(control: Sequence[float], treatment: Sequence[float]) -> float:
    """Worked example: treatment mean minus control mean."""

    if not control or not treatment:
        raise ValueError("both groups need observations")
    return mean(treatment) - mean(control)


def standardized_mean_difference(
    control: Sequence[float],
    treatment: Sequence[float],
) -> float:
    """TODO: divide the mean difference by the pooled sample standard deviation."""

    raise NotImplementedError("complete standardized_mean_difference")


def holm_adjust(p_values: Sequence[float]) -> list[float]:
    """TODO: control family-wise error with Holm's step-down procedure."""

    raise NotImplementedError("complete holm_adjust")


def claim_scope(
    *,
    randomized: bool,
    allocation_intact: bool,
    severe_attrition: bool,
) -> Literal["causal", "associational"]:
    """TODO: permit a causal claim only when all design protections hold."""

    raise NotImplementedError("complete claim_scope")


def self_check() -> None:
    control = [10.0, 11.0, 9.0]
    treatment = [12.0, 13.0, 11.0]
    print("Worked mean difference:", difference_in_means(control, treatment))
    for label, call in (
        ("effect size", lambda: standardized_mean_difference(control, treatment)),
        ("multiple comparisons", lambda: holm_adjust([0.01, 0.04, 0.03])),
        (
            "claim boundary",
            lambda: claim_scope(
                randomized=True,
                allocation_intact=True,
                severe_attrition=False,
            ),
        ),
    ):
        try:
            print(label, "->", call())
        except NotImplementedError:
            print("TODO:", label)


if __name__ == "__main__":
    self_check()
