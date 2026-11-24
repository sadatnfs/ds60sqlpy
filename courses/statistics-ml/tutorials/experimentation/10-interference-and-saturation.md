# Direct effects, spillovers and full-rollout effects

Tutorial ID: `statistics-exp-010`. Prerequisites: `statistics-015`, `statistics-013`, `statistics-exp-001`. Complete example: [experiment_10.py](examples/experiment_10.py).

## Key terms

- **Interference:** One unit's assignment changing another unit's outcome, which breaks the assumption that each outcome depends only on its own assignment.
- **Exposure mapping:** A scientific modeling choice that summarizes own and neighbor assignments into a small set of exposure conditions.
- **Spillover effect:** The outcome change from changing only a neighbor's assignment, three points in the example.
- **Horvitz-Thompson mean:** An estimate of an exposure cell's mean that weights each observed unit by the inverse of its probability of receiving that exposure.
- **Cluster assignment:** Randomizing whole groups together, which targets the all-treated versus all-control contrast but cannot separately identify the direct effect at an untreated-neighbor exposure.

## Expand the potential outcome

One user's assignment can change another user's experience. Sharing, competition and common resources break the assumption that \(Y_i\) depends only on \(A_i\). An exposure mapping summarizes the relevant assignments of neighbors. It is a scientific modeling choice, not a trick that automatically removes interference.

Consider four users arranged in two disconnected pairs. Each has one neighbor. Let \(G_i\) be that neighbor's assignment and define

\[
Y_i(a,g)=b_i+2a+3g.
\]

The direct effect at fixed neighbor assignment is two. The spillover from changing only the neighbor is three. Moving from nobody treated to everyone treated changes each outcome by five. An individual mixed experiment's direct contrast and a full-rollout contrast therefore answer different questions even in this simple world.

## Enumerate the randomization space

Independent Bernoulli(.5) assignment gives 16 possible assignments for four users. Each user's joint exposure \((A_i,G_i)\) has probability .25 for each of its four possibilities. For an exposure cell \((a,g)\), the Horvitz-Thompson mean is

\[
\widehat\mu(a,g)=\frac1{4}\sum_i
\frac{\mathbf1\{A_i=a,G_i=g\}Y_i}{.25}.
\]

Some realized assignments contain no users in a particular cell, producing a zero contribution in that estimator, not evidence that the underlying potential-outcome mean is zero. Averaging over all assignments recovers the target cell mean. The code enumerates the full design and verifies that mean direct, spillover and rollout estimates equal two, three and five respectively.

This is a design-unbiasedness demonstration with known potential outcomes. It is not a variance estimator or evidence that four observed users would support a precise real result. Joint exposure probabilities, which matter for variance, become more complicated in larger networks.

## Change the assignment unit

Randomize each whole pair instead. There are only four cluster assignments, and neighbors always receive the same treatment. A policy-effect estimator based on cluster assignment now averages to five, the all-treated versus all-control effect. It cannot separately identify the direct effect at an untreated-neighbor exposure because the design never produces that exposure.

The second case shows why changing randomization level changes both information and identifiable questions. A cluster design can reduce contamination but does not create information about exposure combinations it excludes. Two clusters are far too few for routine large-cluster standard errors.

## Transfer to a marketplace

If treated buyers obtain scarce inventory that controls would otherwise receive, the mixed contrast may include displacement. Full rollout removes that same comparison and may change supply or pricing. Market clusters, two-sided designs, switchbacks or randomized saturation can target a better-defined policy, but each needs explicit exposure and boundary assumptions.

**Answered discussion: Can we discover the correct network solely from observed similarity?** No. Similar users may connect because of shared causes or selection. Missing edges can hide spillovers; observed edges can be irrelevant to the treatment. Explain which pathway the exposure mapping represents and test design sensitivity to plausible alternatives.

## Worked example: what difference in means estimates under spillover

The four-user toy world in `examples/experiment_10.py` has pairs (0, 1) and (2, 3) that influence each other. Instead of the Horvitz-Thompson contrasts, apply the naive treated-minus-control mean to every assignment that has at least one unit in each arm.

```python
neighbor = np.array([1, 0, 3, 2])
baseline = np.arange(4, dtype=float)
naive = []
for assignment in product([0, 1], repeat=4):
    a = np.array(assignment)
    if a.sum() in (0, 4):
        continue
    y = baseline + 2 * a + 3 * a[neighbor]
    naive.append(y[a == 1].mean() - y[a == 0].mean())
print("usable assignments:", len(naive))
print("mean naive difference:", round(np.mean(naive), 3))
```

```text
usable assignments: 14
mean naive difference: 1.0
```

Fourteen of the sixteen assignments are usable, and the naive contrast averages 1.0. That number is neither the direct effect of 2, the spillover of 3, nor the total of 5. Under this exposure model the naive estimator mixes the direct effect with a negative weight on the spillover: treated users are more often paired with controls in a mixed design, and controls more often receive spillover from treated partners, so the comparison subtracts part of the 3 the treatment actually creates. Randomization alone does not rescue it, because the estimand it targets is defined by the design, not by the product.

## Worked example: one assignment, four exposures

A single draw makes the exposure bookkeeping concrete. Here user 1 is the only control.

```python
import pandas as pd

neighbor = np.array([1, 0, 3, 2])
a = np.array([1, 0, 1, 1])
g = a[neighbor]
y = np.arange(4, dtype=float) + 2 * a + 3 * g
print(pd.DataFrame({"user": range(4), "own": a, "neighbor": g, "y": y}))
```

```text
   user  own  neighbor    y
0     0    1         0  2.0
1     1    0         1  4.0
2     2    1         1  7.0
3     3    1         1  8.0
```

User 0 is treated but has an untreated neighbor, so its outcome 2.0 contains baseline 0 plus the direct 2. User 1 is a control whose neighbor is treated, so its 4.0 is baseline 1 plus spillover 3; counting it as a clean control is the error. Users 2 and 3 are both treated with treated neighbors and each gains 5. Tabulating own and neighbor status per unit is how you see that only one exposure cell, "treated with treated neighbor", corresponds to a full launch.

## Assumptions and checks for interference designs

The exposure mapping is itself an assumption: here only one named neighbor matters, and the effect is additive. If the real network has longer paths or saturating effects, the four exposure cells are too coarse and estimates of 2, 3 and 5 are not guaranteed. Before the analysis, record the probability that each unit lands in each exposure cell; cells with zero probability cannot be estimated without modeling. Check that clusters capture most edges, for example the share of interactions that cross cluster boundaries, since leakage across clusters reintroduces the bias seen above. Expect fewer effective units after clustering, and size the experiment on clusters, not users.

Continue to [switchbacks](11-switchbacks-and-carryover.md). Primary reference: [multilevel designs for spillover effects](https://isps.yale.edu/resource/detecting-spillover-effects-design-and-analysis-of-multilevel-experiments). Related chapter: [networks](../../chapters/31-network-and-graph-analysis.md).
