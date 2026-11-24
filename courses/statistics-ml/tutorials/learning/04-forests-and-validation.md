# Random forests: diversity is a mechanism to measure

Tutorial ID: `statistics-learning-004`. Prerequisites: `statistics-learning-001`, `statistics-019`, `statistics-022`. Complete program: [learning_04.py](examples/learning_04.py).

## Key terms

- **Bagging:** Fitting the same unstable learner on many bootstrap samples and averaging the predictions.
- **Bootstrap sample:** A same-size draw of training rows with replacement, which repeats some rows and omits others.
- **Out-of-bag estimate:** An internal evaluation that predicts each row using only trees that did not train on it; it does not replace grouped evaluation when rows share a person.
- **Error correlation:** The pairwise correlation \(\rho\) between tree errors, which leaves a variance floor \(\rho\sigma^2\) that adding more trees cannot remove.
- **Feature sampling:** Restricting the candidate features at each split, which can lower tree correlation but may weaken individual trees.

## Start with a tree's prediction rule

A regression leaf predicts the mean of the training outcomes assigned to it. A split is useful when its two child means reduce within-leaf squared error relative to one parent mean. Trying all eligible thresholds is a local greedy optimization; the best first split need not be part of the globally best deep tree. Small changes in rows can change early splits and many downstream predictions.

Bagging fits such unstable learners on bootstrap samples and averages them. A bootstrap sample contains repeated training indices and omits others. The program prints six sampled indices and the corresponding out-of-bag set for a six-row miniature. An omitted row can be predicted using trees that did not train on it. Other visits from the same person can still leak into those trees, so OOB is not a substitute for grouped evaluation.

## Derive the correlation floor

Suppose tree prediction errors have common variance \(\sigma^2\) and pairwise correlation \(\rho\). Expanding the variance of their average gives

\[
\operatorname{Var}\left(\frac1B\sum_bE_b\right)
=\sigma^2\left(\rho+\frac{1-\rho}{B}\right).
\]

More trees reduce the uncorrelated term. They cannot remove a common systematic error. Restricting candidate features at each split can lower correlation, but may weaken trees when useful information is concentrated in a few columns. Thus feature sampling is a statistical tradeoff, not only a performance setting.

## Fit a real multi-feature comparison

The complete fixture has six features, 360 independent rows, an additive linear signal plus a squared second-feature signal, and noise. Training uses 180 rows, validation uses 90, and the final test uses 90. Six forests compare candidate-feature counts 1,3,6 and minimum leaf sizes 2,8, with 48 trees each.

Validation MSE chooses the model. Only then does the program calculate test MSE. It independently reconstructs the forest prediction by averaging its constituent tree predictions and checks agreement with the API. It also calculates pairwise test error correlation and reports OOB R-squared. These values answer different questions: OOB is internal evaluation, validation selects, test evaluates the frozen choice, and correlation examines a proposed variance mechanism.

Do not assert that one feature-sampling setting must always win. A lower correlation can coexist with worse individual learners, and a low average error can hide a bad subgroup. The example reports measured tradeoffs rather than coding a universal ranking into its assertions.

## Change the deployment question

If rows are customer visits, split customers before fitting or tuning. If deployment predicts future months, preserve chronology in development as well as final evaluation. If a rising trend extends beyond observed predictor values, a standard forest usually predicts local training averages beyond the outermost splits; adding more trees does not give principled trend extrapolation.

Impurity importance rewards training split improvements and can favor variables with many split candidates. Held-out permutation importance measures reliance on disrupted information, but correlated predictors and implausible perturbations complicate interpretation. Neither is a causal effect.

**Answered discussion: Why keep a simple baseline?** A forest's absolute MSE does not show incremental value. Compare against a constant and an appropriate linear model under the same split, metric and tuning budget. The existing [Python Day 38](../../../../python/ds-60day/companion-guides/day38_tree_models_random_forest.md) supplies additional classifier and OOB practice.

## Worked example: decorrelation versus tree strength

The variance formula above predicts that lowering \(\rho\) helps only if individual trees do not get much worse. Using the same fixture and split as `examples/learning_04.py`, this snippet fits the two extreme candidate-feature settings and measures both ingredients on the 90 test rows.

```python
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

rng = np.random.default_rng(1903)
x = rng.normal(size=(360, 6))
y = 3 * x[:, 0] + 2 * x[:, 1] ** 2 + rng.normal(scale=0.5, size=len(x))
for candidates in (1, 6):
    forest = RandomForestRegressor(
        n_estimators=48, max_features=candidates, min_samples_leaf=2, random_state=1903
    ).fit(x[:180], y[:180])
    trees = np.array([t.predict(x[270:]) for t in forest.estimators_])
    errors = trees - y[270:]
    rho = np.corrcoef(errors)[np.triu_indices(48, 1)].mean()
    tree_mse = np.mean(errors**2, axis=1).mean()
    print(
        f"max_features={candidates}: mean tree MSE={tree_mse:.2f} "
        f"error corr={rho:.2f} forest MSE={mean_squared_error(y[270:], forest.predict(x[270:])):.2f}"
    )
```

```text
max_features=1: mean tree MSE=16.66 error corr=0.40 forest MSE=6.74
max_features=6: mean tree MSE=5.19 error corr=0.37 forest MSE=2.04
```

Restricting each split to one random feature barely changes the pairwise error correlation, 0.40 against 0.37, but it triples the average single-tree error from 5.19 to 16.66. With only two of six features carrying signal, a one-feature tree usually splits on noise, and averaging cannot recover information the trees never used: the forest MSE is 6.74 against 2.04. On data with many weak, redundant signals the balance can reverse. The point is to measure \(\sigma^2\) and \(\rho\) instead of assuming that more randomness is always better. (The test rows appear here only to illustrate the mechanism; the guide program still selects on validation.)

## Worked example: a forest meets values it never saw

Train on a single predictor drawn from [0, 1] with a linear trend of slope three, then ask for predictions inside and beyond that range.

```python
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

rng = np.random.default_rng(4)
x = rng.uniform(0, 1, size=(200, 1))
y = 3 * x[:, 0] + rng.normal(scale=0.1, size=200)
forest = RandomForestRegressor(n_estimators=100, random_state=4).fit(x, y)
line = LinearRegression().fit(x, y)
grid = np.array([[0.5], [1.0], [1.5], [2.0]])
print("x      forest  line")
for point, f, l in zip(grid[:, 0], forest.predict(grid), line.predict(grid)):
    print(f"{point:.1f}  {f:7.2f} {l:6.2f}")
```

```text
x      forest  line
0.5     1.65   1.50
1.0     2.94   3.03
1.5     2.94   4.55
2.0     2.94   6.08
```

Inside the training range the forest and the line agree closely: 1.65 and 1.50 at 0.5, 2.94 and 3.03 at 1.0. Beyond it, every tree sends the point to its rightmost leaf, so the forest repeats 2.94 at 1.5 and at 2.0 while the line continues to 4.55 and 6.08. The forest is not wrong about the data it saw; it simply has no mechanism for trend. If deployment will push a feature beyond its training range, such as price after inflation or tenure in a young product, check the share of new rows outside the observed range before trusting tree predictions there.

## Diagnostics worth printing beside the forest score

Report mean single-tree error and mean pairwise error correlation alongside ensemble error, since together they explain the result. Compare OOB, validation and test estimates; a large gap between OOB and grouped validation hints at leakage through repeated entities. List feature ranges in training and in scoring data. Check residuals by subgroup, because averaging trees can hide a region where every tree makes the same mistake.

Continue to [boosting](05-boosting-loss-and-stopping.md). Official reference: [RandomForestRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html).
