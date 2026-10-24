"""python-stats-01 learner lab: resampling and experiment decisions.

Professional learner deep dive (python-stats-01)
------------------------------------------------

Mental model:
Resampling approximates repeated sampling under an explicit scheme. A bootstrap samples
observational units with replacement to estimate an estimator's sampling variability. A
permutation test shuffles labels under an exchangeability/null assumption to build a reference
distribution. Clustered or temporal data needs cluster/block schemes.  In an experiment, the
estimand states the effect being targeted, such as difference in means under assigned treatment.
Random assignment supports causal interpretation when assignment, interference, attrition,
compliance, and measurement assumptions are credible. Observational adjustment does not recreate
randomization automatically.

API/boundary anatomy:
* resampling unit: matches the independent assignment/observation grain rather than blindly
  sampling rows.
* seeded bootstrap/permutation loop: produces a reproducible distribution of a declared
  statistic with Monte Carlo error.
* estimand + assignment mechanism: defines which causal contrast is identified and which
  assumptions support it.

Micro-example A — bootstrap a mean difference with a seeded generator::

    import numpy as np

    control = np.array([2.0, 2.5, 3.0, 3.5, 4.0])
    treatment = np.array([3.0, 3.5, 4.0, 4.5, 5.0])
    rng = np.random.default_rng(6101)
    draws = np.empty(5_000)
    for index in range(draws.size):
        c = rng.choice(control, size=control.size, replace=True)
        t = rng.choice(treatment, size=treatment.size, replace=True)
        draws[index] = t.mean() - c.mean()
    interval = np.quantile(draws, [0.025, 0.975])
    print({"estimate": treatment.mean() - control.mean(), "interval": interval})

Expected: The resampled interval describes uncertainty under independent within-group
          resampling; the small sample makes it wide/discrete.

Micro-example B — build a randomization-style null distribution::

    import numpy as np

    outcomes = np.array([1, 2, 3, 4, 7, 8, 9, 10], dtype=float)
    assigned = np.array([0, 0, 0, 0, 1, 1, 1, 1], dtype=int)
    observed = outcomes[assigned == 1].mean() - outcomes[assigned == 0].mean()
    rng = np.random.default_rng(6102)
    null = []
    for _ in range(5_000):
        shuffled = rng.permutation(assigned)
        null.append(
            outcomes[shuffled == 1].mean() - outcomes[shuffled == 0].mean()
        )
    p_value = np.mean(np.abs(null) >= abs(observed))
    print({"observed": observed, "two_sided_p": p_value})

Expected: The null distribution comes from assignments consistent with the shuffle rule, not
          from a parametric t formula.

Debugging rule: Write the estimand, unit, assignment/sampling mechanism, statistic, resampling
                rule, seed/runs, interval/test convention, and assumption violations.

The snippets demonstrate mechanics only. They do not complete the
numbered TODOs below; implement those from their stated contracts and
prove normal, boundary, and failure behavior.
"""

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
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 2 — Complete standardized effect
# Prompt: Use the pooled sample standard deviation. Reject groups smaller than two and
# zero pooled variance. Explain raw units and standardized units side by side.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 3 — Bootstrap the difference
# Prompt: Resample each arm independently with replacement, compute 2,000 differences,
# sort them, and select percentile endpoints. Repeat with the same seed and verify
# equality. Change the seed and expect small endpoint variation, not a different
# conclusion guaranteed by design.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 4 — Permute assignments
# Prompt: Pool outcomes and enumerate treatment-index combinations when feasible. Use a
# two-sided comparison to the observed absolute difference. For large data, use seeded
# Monte Carlo assignments and the plus-one p-value correction. State why permuting
# individual rows is invalid if assignment occurred by account or site.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 5 — Plan sample size
# Prompt: Use the Normal approximation for standardized effects 0.2, 0.5, and 0.8. Explain
# why variance uncertainty, clustering, attrition, noncompliance, and a binary metric
# require a more specific planner.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 6 — Control a comparison family
# Prompt: Complete `holm_adjust` for three p-values. Preserve original order and enforce
# monotonic adjusted values after sorting. Identify the family before viewing results;
# splitting an inconvenient family after analysis defeats control.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 7 — Check assignment and attrition
# Prompt: Compute baseline standardized difference by arm. Then remove outcomes
# selectively from one arm and explain how that affects causal credibility even if the
# remaining p-value is small.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 8 — Simulate peeking policy
# Prompt: Five ordinary looks each at alpha 0.05 are not one 0.05 decision. The lesson's
# simple Bonferroni per-look split illustrates the budget. Compare it with a single final
# look and research group-sequential designs before production use.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 9 — Bound the claim
# Prompt: Complete `claim_scope`. Randomization, intact allocation, and no severe
# attrition permit a causal interpretation under additional assumptions. Observational
# grouping, compromised randomization, or severe differential attrition returns an
# associational scope.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 10 — bootstrap clustered assignments
# Prompt: Extend the experiment fixture with multiple rows per account. Bootstrap
# accounts—not rows—within each arm and compare interval width with the incorrect row
# bootstrap.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 11 — bootstrap a ratio metric
# Prompt: Estimate treatment lift for revenue per active user, preserving each user's
# numerator and denominator. Handle a resample with zero denominator and compare ratio-of-
# sums with mean-of-user-ratios.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 12 — apply covariate adjustment without leakage
# Prompt: Use a pre-experiment outcome as a CUPED-style covariate. Estimate its adjustment
# coefficient without post-treatment information and compare unadjusted/adjusted variance
# and mean effect.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 13 — separate intention-to-treat from treatment-on-treated
# Prompt: Simulate assigned treatment with imperfect compliance. Compute the intention-to-
# treat effect by assignment and explain why comparing actual takers with non-takers is
# generally confounded.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 14 — perform missing-outcome sensitivity
# Prompt: Create differential attrition by arm. Report complete-case results and bounded
# best/worst-case outcomes under a declared feasible outcome range.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 15 — simulate sequential false positives
# Prompt: Under a true null, simulate repeated ordinary alpha=0.05 looks and estimate
# ever-reject probability. Compare one final look, the lesson's simple alpha split, and a
# clearly labeled exploratory monitor.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 16 — pre-specify heterogeneous effects
# Prompt: Choose two domain-motivated subgroups before analysis, estimate effects with
# uncertainty and support, and adjust the planned comparison family. Contrast this with
# mining many cuts for the largest lift.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 17 — run clustered randomization inference
# Prompt: For a site-randomized experiment, permute site assignments while keeping all
# rows within a site together. Compare with invalid row-level permutation and state the
# sharp-null interpretation.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 18 — produce an auditable analysis packet
# Prompt: Write a deterministic JSON/Markdown packet containing plan hash, data
# fingerprint, exclusions, assignment checks, attrition, estimand, effect, interval,
# adjusted p-values, claim scope, code version, and limitations.
# Verify: add a boundary check and explain the failure policy.
#
# === End numbered professional practice ===

if __name__ == "__main__":
    self_check()
