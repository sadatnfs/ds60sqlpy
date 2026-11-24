# Estimate an interaction and the uncertainty around it

Tutorial ID: `statistics-exp-009`. Prerequisites: `statistics-011`, `statistics-013`, `statistics-exp-006`. Complete example: [experiment_09.py](examples/experiment_09.py).

## Key terms

- **Main effect:** The average change from switching one factor, averaged over equally weighted levels of the other factor; it equals \(2\beta_A\) with plus or minus one coding.
- **Interaction:** The difference between a factor's conditional effects at different levels of another factor, which can let a positive average hide harm at some settings.
- **Replication:** Repeated runs in each design cell, which supply residual degrees of freedom for estimating noise.
- **Aliasing:** Duplicated design columns, so only a combined effect is identified and more optimizer iterations cannot separate the parts.
- **Blocking:** Randomizing within shared batches, days or locations and keeping the block in the analysis.

## Vary combinations deliberately

Suppose a team changes both page layout and recommendation policy. Two separate tests at a single baseline do not reveal whether their effects depend on one another. A two-factor design observes all four combinations. Code each factor as -1 and +1 and write

\[
\mathbb E[Y\mid A,B]=\beta_0+\beta_AA+\beta_BB+\beta_{AB}AB.
\]

Changing \(A\) from -1 to +1 at fixed \(B\) changes the mean by \(2\beta_A+2\beta_{AB}B\). The average main effect over equally weighted \(B\) levels is \(2\beta_A\). The difference between the two conditional effects is \(4\beta_{AB}\). Those factors of two and four arise from coding; forgetting them gives correct coefficients but wrong substantive effects.

## Work a replicated design

The complete program uses \((\beta_0,\beta_A,\beta_B,\beta_{AB})=(10,2,3,4)\). Each of four cells has two observations with deviations -.5 and +.5. The fitted coefficients recover these values. The average A effect is four, its low-B effect is minus four, and its high-B effect is twelve. The interaction contrast is sixteen.

Eight observations and four coefficients leave four residual degrees of freedom. Residual SSE is two, so the common variance estimate is .5. Orthogonality gives coefficient variance \(.5/8\); the average A contrast has variance four times that quantity. Its 95% t interval is approximately [2.612,5.388]. The normal equal-variance independent-error assumptions justify that model-based reference distribution. Balanced cells alone do not guarantee those error assumptions.

This contrasts with an unreplicated four-run saturated design, which has no residual degrees of freedom. A perfect fit there does not prove no noise. Replication, a justified error model, or design-based inference supplies information about uncertainty.

## What a missing corner loses

With only three corners observed, separate A, B and AB coefficients cannot all be identified with an intercept. Changing A at low B still estimates an A effect conditional on low B. Changing B at high A still estimates a B effect conditional on high A. The problem is extrapolating those conditional comparisons into an interaction or balanced average without an assumption about the missing corner.

A fractional design can deliberately assign a third factor \(C=AB\). Its column is identical to the interaction column, so only a combined effect is identified. The program adds that duplicated column and checks rank four despite five columns. More optimizer iterations do not resolve an alias. Additional runs or a scientifically justified zero-effect restriction are needed.

## Respect blocks and overlap

If each pair of runs shares a batch, day or location effect, randomize within that block and preserve the block in analysis. An online portfolio can create a factorial overlap only when assignment and eligibility make the combinations interpretable. Untracked concurrent tests can change the treatment context without providing a balanced factorial design.

**Answered discussion: Can the positive average main effect justify every combination?** No. Here A harms at low B and helps at high B. The rollout must name the B setting or distribution it targets. Reporting only the positive average conceals a scientifically important interaction.

## Worked example: read the interaction from cell means

The fitted coefficients in `examples/experiment_09.py` summarize four cell means, so it helps to look at those means directly before trusting any slope. This snippet rebuilds the replicated two-factor table and pivots it so that rows are levels of B and columns are levels of A.

```python
import pandas as pd

cells = np.array(list(product([-1.0, 1.0], repeat=2)))
a, b = np.repeat(cells, 2, axis=0).T
y = 10 + 2 * a + 3 * b + 4 * a * b + np.tile([-0.5, 0.5], 4)
means = pd.DataFrame({"A": a, "B": b, "y": y}).groupby(["B", "A"]).y.mean().unstack()
print(means)
print("A effect at B=-1:", means.loc[-1, 1] - means.loc[-1, -1])
print("A effect at B=+1:", means.loc[1, 1] - means.loc[1, -1])
```

```text
A     -1.0   1.0
B
-1.0   9.0   5.0
 1.0   7.0  19.0
A effect at B=-1: -4.0
A effect at B=+1: 12.0
```

Each cell averages two replicates whose noise is plus and minus 0.5, so the means are exact: 9 and 5 when B is low, 7 and 19 when B is high. Moving A from low to high lowers the outcome by 4 under low B and raises it by 12 under high B. The coded A coefficient of 2 is half of the average of those two simple effects, (-4 + 12) / 2 = 4, and the interaction contrast is 12 - (-4) = 16. A report that says "A adds 4" is arithmetically true and practically misleading, because no real user ever experiences the average of the two B settings. When the simple effects differ in sign, the main effect describes a population mix, not a recommendation.

## Worked example: an alias splits one effect into two

Suppose a second treatment C was secretly assigned by the same rule as the A by B product. Adding it as a column produces a design matrix with five columns but only four distinct cells.

```python
cells = np.array(list(product([-1.0, 1.0], repeat=2)))
a, b = np.repeat(cells, 2, axis=0).T
y = 10 + 2 * a + 3 * b + 4 * a * b + np.tile([-0.5, 0.5], 4)
c = a * b
aliased = sm.OLS(y, np.column_stack([np.ones(8), a, b, a * b, c])).fit()
print("coefficients:", np.round(aliased.params, 3).tolist())
print("AB + C:", round(aliased.params[3] + aliased.params[4], 3))
```

```text
coefficients: [10.0, 2.0, 3.0, 2.0, 2.0]
AB + C: 4.0
```

Statsmodels does not raise an error; it uses a pseudo-inverse and divides the interaction of 4 evenly between the AB column and C, printing 2.0 for each. Only the sum, 4.0, is identified by the data. Nothing in the printed coefficients warns the reader, which is why the guide asks you to check the rank of the design before interpreting a table. The same symptom appears when two launches share a targeting rule, or when an experiment layer is assigned by a hash that is correlated with another layer.

## Diagnostics before writing the factorial readout

Check the rank of the design matrix and compare it with the number of columns; a shortfall means some contrast cannot be separated. Count units in every cell, because an unbalanced corner inflates the variance of exactly the interaction you most need. Print simple effects at each level of the other factor alongside the coded coefficients so a sign reversal is visible. Confirm residual degrees of freedom: the replicated design here has only four, so its t quantile is 2.776 rather than 1.96, and the main effect interval [2.612, 5.388] is wide for that reason. Finally, ask whether the factors were randomized independently; if layer assignments share a seed or a hash salt, the cell counts can look balanced while the factors remain dependent within user segments.

Continue to [interference](10-interference-and-saturation.md). Reference: [NIST factorial and fractional designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3.htm).
