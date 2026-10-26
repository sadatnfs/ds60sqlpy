# Estimate an interaction and the uncertainty around it

Tutorial ID: `statistics-exp-009`. Prerequisites: `statistics-011`, `statistics-013`, `statistics-exp-006`. Complete example: [experiment_09.py](examples/experiment_09.py).

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

Continue to [interference](10-interference-and-saturation.md). Reference: [NIST factorial and fractional designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3.htm).
