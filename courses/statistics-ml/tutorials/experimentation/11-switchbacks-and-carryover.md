# A time block is an assignment, not a bag of independent sessions

Tutorial ID: `statistics-exp-011`. Prerequisites: `statistics-exp-009`, `statistics-012`, `statistics-025`. Complete example: [experiment_11.py](examples/experiment_11.py).

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

Continue to [ramping and decisions](12-ramping-and-decision-memo.md). Related chapters: [classical designs](../../chapters/13-classical-experimental-design.md), [time dependence](../../chapters/25-time-series-foundations-and-diagnostics.md).
