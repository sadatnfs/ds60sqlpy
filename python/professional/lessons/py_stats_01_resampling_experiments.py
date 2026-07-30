"""python-stats-01 learner lab: resampling and experiment decisions."""

from __future__ import annotations

from collections.abc import Callable, Sequence
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
    checks: tuple[tuple[str, Callable[[], object]], ...] = (
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
    )
    for label, call in checks:
        try:
            print(label, "->", call())
        except NotImplementedError:
            print("TODO:", label)


# === Numbered professional practice ===
#
# Attempt every exercise before opening solutions. Keep evidence in a copy
# under .learning/ or in tests; do not overwrite the reference solution.
# Full acceptance checks and progressive hints:
# companion-guides/py_stats_01_resampling_experiments.md
#
# Exercise 1 — Define the experiment before analysis
# Prompt: Write an `ExperimentPlan` containing: - assignment unit, - one primary metric
# and window, - minimum sample per arm, - alpha, - intended analysis, - planned
# stopping/looks, and - missing-outcome handling. Do this before computing outcomes.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 2 — Complete standardized effect
# Prompt: Use the pooled sample standard deviation. Reject groups smaller than two and
# zero pooled variance. Explain raw units and standardized units side by side.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 3 — Bootstrap the difference
# Prompt: Resample each arm independently with replacement, compute 2,000 differences,
# sort them, and select percentile endpoints. Repeat with the same seed and verify
# equality. Change the seed and expect small endpoint variation, not a different
# conclusion guaranteed by design.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 4 — Permute assignments
# Prompt: Pool outcomes and enumerate treatment-index combinations when feasible. Use a
# two-sided comparison to the observed absolute difference. For large data, use seeded
# Monte Carlo assignments and the plus-one p-value correction. State why permuting
# individual rows is invalid if assignment occurred by account or site.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 5 — Plan sample size
# Prompt: Use the Normal approximation for standardized effects 0.2, 0.5, and 0.8. Explain
# why variance uncertainty, clustering, attrition, noncompliance, and a binary metric
# require a more specific planner.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 6 — Control a comparison family
# Prompt: Complete `holm_adjust` for three p-values. Preserve original order and enforce
# monotonic adjusted values after sorting. Identify the family before viewing results;
# splitting an inconvenient family after analysis defeats control.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 7 — Check assignment and attrition
# Prompt: Compute baseline standardized difference by arm. Then remove outcomes
# selectively from one arm and explain how that affects causal credibility even if the
# remaining p-value is small.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 8 — Simulate peeking policy
# Prompt: Five ordinary looks each at alpha 0.05 are not one 0.05 decision. The lesson's
# simple Bonferroni per-look split illustrates the budget. Compare it with a single final
# look and research group-sequential designs before production use.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 9 — Bound the claim
# Prompt: Complete `claim_scope`. Randomization, intact allocation, and no severe
# attrition permit a causal interpretation under additional assumptions. Observational
# grouping, compromised randomization, or severe differential attrition returns an
# associational scope.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 10 — bootstrap clustered assignments
# Prompt: Extend the experiment fixture with multiple rows per account. Bootstrap
# accounts—not rows—within each arm and compare interval width with the incorrect row
# bootstrap.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 11 — bootstrap a ratio metric
# Prompt: Estimate treatment lift for revenue per active user, preserving each user's
# numerator and denominator. Handle a resample with zero denominator and compare ratio-of-
# sums with mean-of-user-ratios.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 12 — apply covariate adjustment without leakage
# Prompt: Use a pre-experiment outcome as a CUPED-style covariate. Estimate its adjustment
# coefficient without post-treatment information and compare unadjusted/adjusted variance
# and mean effect.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 13 — separate intention-to-treat from treatment-on-treated
# Prompt: Simulate assigned treatment with imperfect compliance. Compute the intention-to-
# treat effect by assignment and explain why comparing actual takers with non-takers is
# generally confounded.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 14 — perform missing-outcome sensitivity
# Prompt: Create differential attrition by arm. Report complete-case results and bounded
# best/worst-case outcomes under a declared feasible outcome range.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 15 — simulate sequential false positives
# Prompt: Under a true null, simulate repeated ordinary alpha=0.05 looks and estimate
# ever-reject probability. Compare one final look, the lesson's simple alpha split, and a
# clearly labeled exploratory monitor.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 16 — pre-specify heterogeneous effects
# Prompt: Choose two domain-motivated subgroups before analysis, estimate effects with
# uncertainty and support, and adjust the planned comparison family. Contrast this with
# mining many cuts for the largest lift.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 17 — run clustered randomization inference
# Prompt: For a site-randomized experiment, permute site assignments while keeping all
# rows within a site together. Compare with invalid row-level permutation and state the
# sharp-null interpretation.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 18 — produce an auditable analysis packet
# Prompt: Write a deterministic JSON/Markdown packet containing plan hash, data
# fingerprint, exclusions, assignment checks, attrition, estimand, effect, interval,
# adjusted p-values, claim scope, code version, and limitations.
# Evidence: add a boundary check and explain the failure policy.
#
# === End numbered professional practice ===

if __name__ == "__main__":
    self_check()
