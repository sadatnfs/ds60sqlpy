# 13. Classical Experimental Design

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-013`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

An experiment creates information through controlled variation. Randomization breaks systematic relationships between assignment and pre-existing potential outcomes in expectation; it does not guarantee perfect balance in every realized sample. Blocking uses known prognostic differences to improve precision before assignment. Replication estimates noise, and independent randomization units determine how much information an experiment contains.

### Main effects and interactions

For two factors coded A,B in {-1,+1}, write E[Y]=beta0+betaA*A+betaB*B+betaAB*\(A\cdot B\). Moving A from -1 to +1 at fixed B changes the response by 2*betaA+2*betaAB*B. The average main effect of A across balanced B levels is 2*betaA. A factorial experiment estimates interactions because it varies combinations, unlike changing one factor while holding all others at a baseline.

A fractional design saves runs by deliberately losing distinctions. If a third factor C is assigned as \(A\cdot B\), the C column equals the AB interaction column, so their effects are aliased. No regression package can separate them from that design alone. The scientific assumption that one is negligible creates the interpretation.

### Design precision before collection

For independent groups of equal size n and common SD sigma, the difference in means has \(\mathrm{SE}=\sigma\cdot \sqrt{\frac{2}{n}}\). A rough two-sided normal approximation gives \(n=\frac{2\sigma^2(z_{1-\alpha/2}+z_{\mathrm{power}})^2}{\delta^2}\) per group. This shows why halving the target effect needs about four times the sample. Clustering, attrition, unequal allocation and multiplicity must be added to the design, and simulation can evaluate realistic departures.

## Methods, mechanisms, and limits

### stat-13-01

**Randomized controlled trials**

Assign interventions using a known random mechanism and analyze the assignment-defined population. Randomization supports exchangeability in expectation, while consistency, interference, missing outcomes and adherence still determine the causal interpretation.

### stat-13-02

**Complete randomization**

Assign a fixed count of units to each arm uniformly over allowed allocations. This controls total allocation but can leave chance covariate imbalance. Use the same allocation space in randomization-based inference.

### stat-13-03

**Blocked randomization**

Form blocks using pretreatment prognostic variables, then randomize within them. Analyze with block awareness. Blocking on too many tiny categories can constrain assignment and complicate generalization.

### stat-13-04

**Matched-pair randomization**

Create similar pairs and randomly treat one member of each. Analyze within-pair contrasts and retain pair identifiers. Matching quality affects precision; treatment-dependent pairing would undermine the design.

### stat-13-05

**Cluster randomized trials**

Randomize groups to reduce contamination or respect operational delivery. Effective sample size depends strongly on cluster count and correlation. Account for unequal cluster sizes and whether the estimand weights clusters or individuals.

### stat-13-06

**Stratified randomization**

Randomize separately within prespecified strata to maintain balance on important categories. Unlike outcome-driven subgroup selection, strata precede treatment. Preserve their allocation probabilities and population weights in analysis.

### stat-13-07

**Factorial designs**

Vary all combinations of factor levels to estimate main and interaction effects efficiently. Balance provides useful orthogonality. Factorial main effects average over the other factor settings used in the design.

### stat-13-08

**Fractional factorial designs**

Select a principled subset of factorial combinations to reduce runs. The defining relation determines aliases and design resolution. A small experiment cannot estimate all effects merely by fitting a larger formula.

### stat-13-09

**Aliasing and confounding in designs**

Effects are aliased when their design columns are identical or linearly dependent. Confounding is then structural rather than a high correlation warning. Additional runs or substantive zero-effect assumptions are needed to separate them.

### stat-13-10

**Split-plot designs**

Randomize hard-to-change factors at whole-plot level and easier factors within plots. Different effects use different error strata. Treating all runs as independently assigned overstates precision for whole-plot factors.

### stat-13-11

**Latin square designs**

Arrange treatments so each occurs once in every row and column block. This controls two nuisance dimensions efficiently but assumes the relevant interaction structure is manageable. Randomize the permissible layout.

### stat-13-12

**Crossover designs**

Each unit receives multiple treatments in a randomized sequence across periods. Within-unit comparison improves precision when carryover is absent or modeled. Period effects and informative dropout can invalidate simple differences.

### stat-13-13

**Washout periods**

Allow enough time between treatments for relevant effects to dissipate. The duration must follow domain knowledge or evidence; a calendar gap alone does not prove carryover disappeared.

### stat-13-14

**Carryover effects**

Earlier treatment changes later responses beyond the current treatment. Detecting no significant carryover in a small study is weak assurance. Consider parallel designs when persistent effects are plausible.

### stat-13-15

**Stepped-wedge designs**

Randomize when clusters adopt an intervention, often eventually treating all. Calendar time can confound treatment exposure, so model secular trends and cluster dependence. Effects may vary with time since adoption.

### stat-13-16

**Response surface methodology**

Use local polynomial response models to search favorable factor settings. Start near a credible region and iterate; a fitted optimum outside the experimental range is unsupported extrapolation.

### stat-13-17

**Central composite designs**

Combine factorial points, center replicates and axial points to estimate quadratic curvature. Axial distance influences rotatability and feasible operating ranges. Repeated center points help assess pure error and lack of fit.

### stat-13-18

**Box–Behnken designs**

Use mid-edge combinations and center points for quadratic models without all extreme corners. This can avoid dangerous joint extremes, but omitted corners limit information about behavior there.

### stat-13-19

**Optimal experimental design**

Choose runs to maximize an information criterion under a specified model and feasible region. The optimal design is model-dependent; robust or sequential designs may be preferable when the response structure is uncertain.

### stat-13-20

**D-optimal design**

Maximize the determinant of \(X^{\mathsf T}X\), reducing the volume of a coefficient uncertainty ellipsoid under the model. A singular information matrix cannot estimate all coefficients, regardless of its individual diagonal entries.

### stat-13-21

**A-optimal design**

Minimize the trace of the inverse information matrix, targeting average coefficient variance. Parameter scaling affects this criterion, so choose scientifically meaningful units or standardized contrasts.

### stat-13-22

**Power and sample-size analysis**

Specify effect, variability, alpha, power, allocation and independent units before sizing. Small-cluster or rare-event settings often need simulation instead of a simple normal approximation.

### stat-13-23

**Simulation-based design**

Generate outcomes and assignment under realistic scenarios, analyze each with the planned method, and estimate operating characteristics. Include failure scenarios and Monte Carlo error; simulation proves only the scenarios implemented.

### stat-13-24

**Blinding**

Conceal assignment from participants, operators or assessors where feasible to reduce expectation and measurement effects. Blinding differs from allocation concealment before enrollment, and both address distinct bias pathways.

### stat-13-25

**Preregistration and analysis plans**

Prespecify estimands, metrics, exclusions, sample size, stopping and multiplicity before outcomes are inspected. Amendments can be valid when transparently dated and justified; concealment of outcome-informed changes undermines confirmation.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: optimize a process without confounding factors

A manufacturing team can change temperature and pressure, each at two settings. Changing temperature first at low pressure, then pressure at high temperature, confounds the pressure comparison with the changed temperature setting. A full two-by-two factorial measures all combinations, allowing a direct interaction contrast: the temperature effect at high pressure minus its effect at low pressure.

Suppose the four means at (low,low), (high,low), (low,high), (high,high) are 10,12,13,23. Temperature adds two at low pressure but ten at high pressure, so the interaction contrast is eight. Averaging temperature over equal pressure weights gives a main effect six. A one-factor-at-a-time conclusion that temperature adds two would miss the operating region with the largest benefit. Whether that region is safe and feasible remains an engineering constraint, not a statistical property of the fitted surface.

Replication at the same setting estimates noise, while varying settings identifies response structure. Repeating one corner 100 times does not identify a quadratic response over the entire region. Center points help reveal curvature, and a response-surface design adds settings to estimate it. If extreme corners are unsafe, a Box-Behnken design may be attractive, but conclusions about those omitted extremes remain limited. Optimal design should include the feasible region explicitly rather than suggest settings the process cannot tolerate.

### Case study: randomize at the level where intervention acts

Suppose a training program is delivered to whole teams. Team members share instructors, managers and communication, so an individual's outcome may depend on teammates' exposure. Randomizing individuals inside a team can contaminate the comparison. Randomizing teams preserves a cleaner delivery contrast but reduces the number of independent assignments.

If only eight teams exist, collecting hundreds of measurements per member cannot create dozens of independently randomized teams. Block teams on a few strong pretreatment predictors if justified, preserve the assignment scheme, and consider design-based inference or small-sample methods appropriate to the cluster count. Power calculations must include plausible intraclass correlation and unequal team sizes. A precise member-level regression that ignores those facts reports imaginary information.

The estimand also needs a weight choice. An average team effect weights small and large teams equally; an average employee effect weights by team size. If team size is associated with treatment effect, the answers differ. State the operational decision before choosing a convenient aggregate. Attrition at team and member level can further change which population remains observed.

### Case study: crossover efficiency and carryover risk

A crossover can compare two interfaces within the same participants, reducing stable participant-level variation. Randomizing sequence separates some treatment and period effects. But learning the first interface may change how a participant uses the second, and no short washout can necessarily remove learned skill. The potential outcome then depends on treatment history rather than only current treatment.

A paired analysis of final scores assumes away relevant carryover if it treats the two periods as interchangeable conditions. A larger sample narrows its interval around that wrong comparison. Alternatives include a parallel-arm design, a carefully modeled period/history estimand, or an intervention where carryover is scientifically negligible. Decide using the mechanism before calculating the efficiency benefit of pairing.

Stepped-wedge designs similarly combine treatment rollout with calendar time. They may be operationally appealing because all clusters eventually receive treatment, but later-treated clusters experience a different calendar environment. Secular trends, implementation learning and varying time since adoption need explicit modeling. A phased schedule is not automatically a well-randomized stepped-wedge study.

### From planning numbers to a defensible experiment

Sample-size formulas require an effect worth detecting, not merely the effect that makes the available sample look sufficient. Translate the smallest useful benefit into the measurement scale, estimate variance from relevant historical information, and include realistic attrition. If an outcome is rare or heavy-tailed, simulate plausible generating processes and evaluate the exact planned analysis.

A simulation-based design report should show power, false-positive behavior, bias, interval coverage and failure frequency across favorable and adverse scenarios. Report Monte Carlo uncertainty: estimating power from 100 replications is itself noisy. A design that works only when every assumption is exactly true may need a simpler estimand, better measurements or a larger independent sample rather than a more elaborate estimator.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_13.py](../examples/chapter_13.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_13.py
```

### Estimate an interaction and expose an alias

The four-run factorial recovers coefficients 10,2,3,4. The main A effect is four because coded levels differ by two, while its conditional effects depend strongly on B. Adding \(C=A\cdot B\) makes a fifth coefficient impossible to identify from four independent directions. Rank reveals the design limitation exactly.

### Randomize within prognostic groups

Each block has four units and exactly two receive treatment. The fixed seed makes this illustration reproducible, but a real assignment system must also protect allocation integrity and avoid rerandomizing until a favorable sample appears.

### Budget precision

The normal approximation requires about 63 observations per arm for SD two, effect one, two-sided alpha .05 and power .8. Halving the effect requires about 252. These are planning approximations for independent observations, not a valid calculation for 63 highly correlated records from one cluster.

### Complete executable example

```python
import numpy as np
from itertools import product
from scipy.stats import norm


def factorial_and_alias():
    ab = np.array(list(product([-1.0, 1.0], repeat=2)))
    a, b = ab.T
    design = np.column_stack([np.ones(4), a, b, a * b])
    y = 10 + 2 * a + 3 * b + 4 * a * b
    beta = np.linalg.solve(design, y)
    assert np.allclose(beta, [10, 2, 3, 4])
    assert np.isclose(y[a == 1].mean() - y[a == -1].mean(), 4)
    c = a * b
    alias = np.column_stack([np.ones(4), a, b, c, a * b])
    assert np.linalg.matrix_rank(alias) == 4 and alias.shape[1] == 5
    print("Factorial coefficients:", beta, "C and AB are identical:", np.array_equal(c, a * b))


def blocked_assignment():
    rng = np.random.default_rng(13)
    blocks = np.repeat(np.arange(4), 4)
    treatment = np.zeros(16, dtype=int)
    for block in np.unique(blocks):
        rows = np.flatnonzero(blocks == block)
        treatment[rng.choice(rows, 2, replace=False)] = 1
    assert all(treatment[blocks == b].sum() == 2 for b in range(4))
    print("Treated per block:", [int(treatment[blocks == b].sum()) for b in range(4)])


def sample_size():
    sigma, delta = 2.0, 1.0
    n = 2 * sigma**2 * (norm.ppf(0.975) + norm.ppf(0.8)) ** 2 / delta**2
    half_effect = 2 * sigma**2 * (norm.ppf(0.975) + norm.ppf(0.8)) ** 2 / (delta / 2) ** 2
    assert np.isclose(half_effect, 4 * n)
    print("Approximate per-arm n:", int(np.ceil(n)), "half effect:", int(np.ceil(half_effect)))


def main():
    factorial_and_alias()
    blocked_assignment()
    sample_size()


if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Why use a factorial experiment rather than several one-factor studies?** It can estimate interactions and reuse control information across combinations. If one factor's benefit depends on another, isolated baseline changes can miss the relevant operating setting. Feasibility and interference still constrain the design.

**Interview: What does aliasing mean operationally?** Two proposed effects make the same predictions at every chosen run. Additional numerical precision cannot distinguish them. Add design points or state which effect is assumed negligible.

**Interview: Is balanced assignment enough to establish an experiment was randomized?** No. Deterministic alternation or a flawed hash can produce balanced counts while correlating assignment with arrival or identity. Inspect the mechanism, logging and implementation as well as realized balance.

## Primary sources and official APIs

- [NIST choosing an experimental design](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3.htm).

- [NIST response-surface design comparison](https://itl.nist.gov/div898/handbook/pri/section3/pri3363.htm).

## Reading connections

[Previous chapter](12-regression-diagnostics-multilevel-models-and-longitudinal-analysis.md) | [Book contents](../README.md) | [Next chapter](14-online-experimentation-and-a-b-testing.md)
