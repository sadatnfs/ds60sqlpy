# science-004: Staggered adoption and uncontaminated group-time contrasts

Tutorial mode. Stage: beginner. Direct prerequisites: `science-001`, `statistics-016`.

## Different adoption times create different comparisons

A two-period difference-in-differences calculation compares the change in a treated group with the change in an untreated group. With staggered adoption, a unit can be untreated at one time and treated later. A regression that mechanically uses all other units as controls can therefore compare a newly treated group with a group whose treatment effect is already evolving.

Let \(G_i\) be the first treatment period and let \(Y_{it}\) be the observed outcome. For cohort \(g\) at time \(t\ge g\), a group-time contrast uses the last pretreatment baseline \(g-1\) and an eligible comparison group:

\[
\widehat{\operatorname{ATT}}(g,t)
=\overline{Y_t-Y_{g-1}}_{G=g}
-\overline{Y_t-Y_{g-1}}_{G>t}.
\]

The displayed expression is the simple unconditional comparison used by our fixture. Identification requires a suitable parallel-trends assumption, no anticipation, well-defined treatment and overlap. Conditional approaches may require additional outcome or propensity modeling. The formula is not a claim that every staggered design is identified by unconditional averaging.

## Key terms

- **Staggered adoption:** A design in which units start treatment at different times, so a unit can serve as untreated early and treated later.
- **Group-time ATT:** The average treatment effect on the treated for adoption cohort g at time t, contrasted against the last pretreatment period g - 1.
- **Eligible comparison group:** Units not yet treated by time t, so their change over the contrast window is not contaminated by their own treatment effects.
- **Parallel trends:** The assumption that treated and comparison groups would have changed by the same amount without treatment; a pretrend test cannot prove it.
- **No anticipation:** The assumption that outcomes do not respond to treatment before the adoption period.

## Worked case 1: recover cohort-specific dynamic effects

The six synthetic units belong to an early cohort adopting at time two, a later cohort adopting at time four, and a never-treated group. Untreated outcomes combine a unit intercept with a common linear time trend. Treatment effects begin at two and grow by two per exposed period. These mechanisms deliberately satisfy the simple identifying assumptions.

At time four, the early cohort's effect is six and the later cohort's effect is two. The function selects controls with \(G>t\), so neither cohort uses an already treated unit as an untreated comparison. The code recovers both effects exactly. It also verifies that the early cohort's first-period effect is two, checking the event-time indexing.

An event-time summary averages different cohort-time cells at a common number of periods since adoption. The available cohorts may differ at longer horizons. A plotted curve can therefore change because treatment effects evolve, because the composition of represented cohorts changes, or both. Report the aggregation weights and the support behind each horizon. Do not connect unsupported horizons with a smooth curve that implies evidence.

## Worked case 2: an already-treated control erases the effect

For the newly treated cohort at time four, the observed outcome change is three: one unit of background trend and two units of treatment effect. The early cohort also changes by three because its existing treatment effect grows by another two. Subtracting the early cohort's change produces zero, even though the new cohort's treatment effect is two.

This is a direct numerical demonstration of a contaminated comparison. It does not prove that every two-way fixed-effect estimate is biased in the same direction. The mixture of comparisons and weights depends on adoption timing, treatment-effect heterogeneity and specification. The lesson is to inspect which units act as controls for each contrast and what causal quantity their differences can identify.

The function refuses a comparison with no eligible controls, no target cohort or a time before adoption. A common implementation error is to substitute all other units when eligible controls vanish. That produces an answer by changing the comparison, not by recovering missing support.

## Diagnostics that support a design

Pretreatment outcomes can reveal incompatible trends, coding errors or anticipation. A nonsignificant pretrend test does not prove parallel trends: it may have low power, and the post-treatment counterfactual remains unobserved. Examine effect sizes and uncertainty, substantively relevant violations, timing definitions and selection into the analysis population.

Treatment can change covariates, survival in the sample or observation intensity. Conditioning on those post-treatment variables may undermine the intended contrast. Record whether the panel is balanced, why units enter or leave, and whether calendar effects differ across cohorts. Inference usually needs to respect the assignment level and serial dependence, often through clustered resampling or a design-specific procedure rather than treating every row as independent.

## Answered scientific discussion

**Can we average the two recovered effects into four?** Only after specifying weights and the target. An equal-cohort average, an equal-unit average and an event-time average can differ in a real unbalanced panel. The numerical average is easy; the scientific interpretation requires the weighting rule.

**What does this program establish?** It shows that eligible-control group-time contrasts recover known effects under the constructed mechanism, and that one clearly invalid comparison fails. An external policy study still needs an argument for identification, appropriate uncertainty and a transparent aggregation strategy.

## Worked example: Event-time aggregation of clean group-time effects

```python
import numpy as np

# ATT(g, t) estimates from never-treated comparisons, keyed by cohort g and period t.
att = {(2, 2): 1.0, (2, 3): 2.0, (2, 4): 3.0, (3, 3): 0.5, (3, 4): 1.0, (4, 4): 0.2}
size = {2: 40, 3: 30, 4: 30}

for e in range(3):
    cells = [(g, t) for (g, t) in att if t - g == e]
    w = np.array([size[g] for g, _ in cells], float)
    vals = np.array([att[c] for c in cells])
    print(f"event time {e}: cohorts {[g for g, _ in cells]}, weighted ATT {w @ vals / w.sum():.3f}")

simple = np.mean(list(att.values()))
cohort_weighted = sum(size[g] * v for (g, _), v in att.items()) / sum(size[g] for g, _ in att)
print(f"unweighted mean of cells {simple:.3f}; cohort-size weighted {cohort_weighted:.3f}")
```

Observed output:

```text
event time 0: cohorts [2, 3, 4], weighted ATT 0.610
event time 1: cohorts [2, 3], weighted ATT 1.571
event time 2: cohorts [2], weighted ATT 3.000
unweighted mean of cells 1.283; cohort-size weighted 1.386
```

Each group-time cell was already estimated against never-treated units, so this example only decides how to summarize them. Event time 0 collects the first treated period of all three cohorts: \((40(1.0)+30(0.5)+30(0.2))/100=0.610\). Event time 1 has only cohorts 2 and 3 because cohort 4 is not observed one period after adoption, giving \((40(2.0)+30(1.0))/70=1.571\). Event time 2 rests on cohort 2 alone, so its 3.000 is a statement about the earliest adopters, not about everyone. The rising profile 0.61, 1.57, 3.00 mixes two things: effects that grow with exposure, and a changing composition of which cohorts contribute. The two single summaries also disagree, 1.283 unweighted versus 1.386 weighted by cohort size, because the large early cohort has the largest effects and the most cells. Reporting the event-time profile with its contributing cohorts is more honest than either single number. If cohort 4 had 300 units instead of 30, the event-time 0 average would fall toward 0.2.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def group_time_effect(outcomes, first_treated, group, time):
    y = np.asarray(outcomes, float)
    g = np.asarray(first_treated)
    if y.ndim != 2 or len(g) != len(y) or not 1 <= group <= time < y.shape[1]:
        raise ValueError("Use a valid pretreatment baseline and observed follow-up time")
    baseline = group - 1
    target = g == group
    controls = g > time
    if not target.any() or not controls.any() or time < group:
        raise ValueError("Need a treated cohort, pretreatment baseline and eligible controls")
    return float(
        (y[target, time] - y[target, baseline]).mean()
        - (y[controls, time] - y[controls, baseline]).mean()
    )


def run_cases():
    g = np.array([2, 2, 4, 4, 99, 99])
    periods = np.arange(6)
    baseline = np.arange(6.0)[:, None] + periods[None, :]
    y = baseline.copy()
    for i, entry in enumerate(g):
        if entry < 99:
            y[i, entry:] += np.arange(1, 7 - entry) * 2
    early = group_time_effect(y, g, 2, 4)
    late = group_time_effect(y, g, 4, 4)
    contaminated = float(
        (y[g == 4, 4] - y[g == 4, 3]).mean() - (y[g == 2, 4] - y[g == 2, 3]).mean()
    )
    assert early == 6 and late == 2 and contaminated == 0
    assert group_time_effect(y, g, 2, 2) == 2
    return dict(
        early_cohort_at_t4=early, late_cohort_at_t4=late, already_treated_comparison=contaminated
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-004 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Callaway and Sant Anna, group-time identification](https://arxiv.org/abs/1803.09015)
- [Causal Inference: What If, author resource](https://miguelhernan.org/whatifbook)
