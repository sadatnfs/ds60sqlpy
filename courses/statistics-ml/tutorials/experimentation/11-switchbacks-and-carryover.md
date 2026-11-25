# A time block is an assignment, not a bag of independent sessions

Tutorial ID: `statistics-exp-011`. Prerequisites: `statistics-exp-009`, `statistics-012`, `statistics-025`. Complete example: [experiment_11.py](examples/experiment_11.py).

## Key terms

- **Switchback design:** Assigning policies to time blocks, often within a location, with randomized order rather than a fixed alternation.
- **Adjacent block pair:** Two neighboring blocks whose AB or BA order is chosen by a coin; the pair, not each session, is the independent assignment unit.
- **Paired block difference:** Treatment minus control within one pair, which removes the baseline level the two blocks share.
- **Carryover:** A treatment effect that persists into the following block, so the current assignment alone no longer describes the outcome.
- **Washout:** A transition period excluded from analysis by advance rule to limit carryover, which changes the analysis horizon.

## Why alternate treatment over time?

A shared system may be unable to serve treatment and control simultaneously without interference. A switchback assigns a policy to time blocks, often within a location. Randomize the order rather than equating treatment with every busy evening. The analysis unit must preserve the assignment and temporal dependence.

The worked design has 30 pairs of adjacent blocks. In each pair, a coin determines AB or BA order. Each block has a baseline trend, an independent block shock and treatment increment 1.5. The two blocks within a pair share their baseline level. These assumptions make paired block differences useful; they do not describe every operational time series.

## Work a pair and aggregate pairs

For pair \(j\), calculate \(D_j=Y_{j,T}-Y_{j,C}\). With independent pairs and a stable mean contrast,

\[
\widehat\tau=\bar D,\qquad
\widehat{\operatorname{SE}}(\bar D)=\frac{s_D}{\sqrt J}.
\]

Pairing removes the common pair baseline. The fixture gives effect about 1.492, SE .226 and a t interval [1.030,1.954]. The point estimate differs from the synthetic 1.5 because block shocks remain. Normal independent pair differences justify the displayed small-sample t calculation in this constructed model.

## Manufacture false precision

Now repeat each block outcome 40 times as if there were 40 sessions. A naive independent-session comparison gives SE about .041. It reports more than five times too much precision because it treats repeated copies of a shared block shock as new randomized information. The number of logged sessions is not the number of independent assignments.

Real sessions need not be identical for this problem to occur. Positive within-block dependence still changes uncertainty. Aggregation, block-aware randomization inference, cluster covariance or a justified time-series analysis must match the design. Having many blocks is insufficient if adjacent blocks retain long dependence.

## Introduce carryover

The contrasting case adds .8 to a block outcome when the preceding block was treated. The ordinary treatment-control contrast falls to about .985. The current assignment alone no longer describes the outcome: treatment history matters. Random order removes some time confounding, but does not erase a physical effect that persists into the next block.

Possible responses include longer blocks, a justified transition exclusion or washout, a treatment-history estimand, and a model/design that identifies it. Excluding transition periods changes the analysis horizon and must be defined in advance. More rapid switching increases the number of labels but can leave less uncontaminated information.

For geography, replace time blocks with markets only if the relevant spillovers stay sufficiently within boundaries. Few heterogeneous markets demand balance planning and uncertainty reflecting their count. A million customers in four geographies is still four independent geographic assignments.

**Answered discussion: Can we increase power by dividing each hour into minute rows?** Only if the new design creates additional independent, interpretable assignments and the system can respond on that timescale. Relabeling existing logs cannot increase information and may worsen carryover.

## Worked example: what pairing buys in precision

The switchback simulation in `examples/experiment_11.py` alternates arms within 30 adjacent pairs of periods. Analyzing the same 60 periods as if they were two independent samples ignores the slow baseline drift that pairing removes.

```python prelude=examples/experiment_11.py
rng = np.random.default_rng(1111)
pairs = 30
order = rng.binomial(1, 0.5, pairs)
treatment = np.column_stack([order, 1 - order]).ravel()
baseline = np.repeat(np.linspace(10, 12, pairs), 2)
outcome = baseline + 1.5 * treatment + rng.normal(size=2 * pairs)
_, unpaired_se, _ = welch_summary(outcome[treatment == 1], outcome[treatment == 0])
diffs = np.where(order == 1, outcome[0::2] - outcome[1::2], outcome[1::2] - outcome[0::2])
print(f"unpaired SE={unpaired_se:.3f} paired SE={diffs.std(ddof=1) / np.sqrt(pairs):.3f}")
```

```text
unpaired SE=0.266 paired SE=0.226
```

The within-pair standard error is 0.226 against 0.266 for the unpaired Welch comparison, a reduction of about 15 percent. The gain is modest because the baseline drifts only from 10 to 12 across the whole run, so neighboring periods differ little either way. On a marketplace with strong daily cycles the difference grows, which is why the pair, not the period, is the unit of analysis. Both numbers are honest about the 30 or 60 period outcomes; the false precision of 0.041 in the guide comes from treating repeated rows inside a period as independent, which is a different and larger mistake.

## Worked example: modeling one period of carryover

If the previous period leaves a residue of 0.8, one diagnostic is to regress the outcome on the current and the lagged assignment together, holding the baseline trend fixed.

```python
import statsmodels.api as sm

rng = np.random.default_rng(1111)
pairs = 30
order = rng.binomial(1, 0.5, pairs)
treatment = np.column_stack([order, 1 - order]).ravel()
baseline = np.repeat(np.linspace(10, 12, pairs), 2)
outcome = baseline + 1.5 * treatment + rng.normal(size=2 * pairs)
previous = np.r_[0, treatment[:-1]]
carryover = outcome + 0.8 * previous
design = sm.add_constant(np.column_stack([treatment, previous, baseline]))
fit = sm.OLS(carryover, design).fit()
print("current, previous:", np.round(fit.params[1:3], 3).tolist())
print("SEs:", np.round(fit.bse[1:3], 3).tolist())
```

```text
current, previous: [1.834, 1.34]
SEs: [0.3, 0.3]
```

The model returns 1.834 for the current effect and 1.34 for the carryover, each with a standard error of 0.3. Both are within roughly 1.1 standard errors of the true 1.5 and 0.8, so the regression is unbiased but noisy. The noise comes from design: in a strict pair alternation the current and previous arms have a correlation of about -0.63, so the two columns compete for the same variation. A design with some repeated arms in a row, or with washout periods dropped from analysis, separates the two quantities more cleanly than adding a lag term after the fact.

## Failure modes in switchback analysis

Choosing a period shorter than the system memory guarantees carryover, and the bias points toward zero when arms alternate. Counting events or users inside a period as independent replicates produces the 40-fold overstated precision shown earlier. Randomizing the order within pairs protects against linear drift, but a regular weekly cycle aligned with the period length can still confound arms. Check residual autocorrelation across pairs, compare estimates with and without the first part of each period, and report the number of pairs as the sample size.

Continue to [ramping and decisions](12-ramping-and-decision-memo.md). Related chapters: [classical designs](../../chapters/13-classical-experimental-design.md), [time dependence](../../chapters/25-time-series-foundations-and-diagnostics.md).
