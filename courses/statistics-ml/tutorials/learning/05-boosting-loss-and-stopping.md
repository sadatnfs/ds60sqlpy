# Boosting: follow the objective across stages

Tutorial ID: `statistics-learning-005`. Prerequisites: `statistics-learning-003`, `statistics-learning-004`. Complete program: [learning_05.py](examples/learning_05.py).

## Key terms

- **Negative gradient:** The direction each new tree fits; for half squared loss it is the residual \(y_i-F(x_i)\).
- **Learning rate:** The shrinkage factor that scales each tree's update before it is added to the current prediction.
- **Newton leaf weight:** The leaf value \(-G/(H+\lambda)\) from summed gradients, summed curvature and an L2 penalty, added on the score scale rather than to probabilities.
- **Split gain:** The improvement in the regularized objective from replacing one leaf by two, less the complexity penalty gamma.
- **Early stopping:** Choosing the number of boosting stages by validation loss across staged predictions, without consulting the test set.

## Fit the correction rather than the labels again

For half squared loss, the derivative with respect to the current prediction is \(F(x_i)-y_i\). A new tree approximates its negative, the residual. Add a shrunken update \(F_m=F_{m-1}+\eta h_m\). Initialization is part of the model: a constant mean minimizes initial squared error, while a constant log-odds score minimizes initial binary logistic loss.

Six observations have outcomes 0,0,0,6,6,6. The initial mean prediction is three and MSE is nine. A stump exactly fits residuals -3 and +3. With learning rate .5, the first update has MSE 2.25. Each subsequent exact half correction divides residuals by two and MSE by four. The complete trace is 9,2.25,.5625,.140625,.03515625. The program verifies this geometric relationship across four stages rather than only one training-loss decrease.

This noiseless easy fixture isolates optimization. It cannot establish the best stage count for noisy data. Continued training can chase noise; a validation procedure is needed for model selection.

## Derive a logistic leaf update

Use a score \(F\) with probability \(p=\sigma(F)\). Logistic loss has first derivative \(g_i=p_i-y_i\) and second derivative \(h_i=p_i(1-p_i)\). For a leaf with total gradient \(G\), total curvature \(H\), and L2 penalty \(\lambda\), the local quadratic objective is

\[
Gw+\frac12(H+\lambda)w^2,
\qquad w^*=-\frac{G}{H+\lambda}.
\]

At initial probability .5, three negative labels give \(G=1.5,H=.75\). With lambda one the leaf weight is about -.857; the positive-label leaf has +.857. Multiplying by the .5 learning rate updates scores, then the sigmoid produces probabilities. Adding .429 directly to probability would implement a different, potentially invalid model.

The gain for splitting one parent into two leaves is half the sum of the two child scores minus the parent score, less a leaf-complexity penalty gamma. Lambda controls leaf magnitude; gamma controls whether extra structure pays. Neither replaces validation. Very small logistic curvature also motivates minimum-information constraints and careful numerical handling.

## Select stages without consulting the test

The second case fits 100 shallow boosted trees on 180 rows of the nonlinear six-feature fixture. `staged_predict` evaluates every stage on a separate 90-row validation set. The minimum selects stage count; an otherwise identical model with that count is refit on the same training rows and evaluated on 90 untouched test rows.

The validation minimum contains selection noise. Its reported score is not the final performance estimate. Learning rate, depth, leaf restrictions and stage count interact: comparing only equal stage counts can give an unfair optimization budget. Real early stopping should preserve the full preprocessing and split boundary.

**Answered discussion: Is this the XGBoost package?** The leaf calculation teaches its regularized objective, and the staged example uses scikit-learn. Real optional XGBoost/LightGBM practice already exists in [Python Day 39](../../../../python/ds-60day/companion-guides/day39_gradient_boosting_xgboost_lightgbm.md). Use its declared environment; this tutorial does not import either optional package.

## Worked example: the L2 penalty on a logistic leaf

The guide derives \(w^*=-G/(H+\lambda)\). Varying \(\lambda\) on the six-label miniature from `examples/learning_05.py` shows what that penalty does to an actual probability.

```python
import numpy as np
from scipy import special

labels = np.array([0, 0, 0, 1, 1, 1])
p = special.expit(np.zeros(6))
g, h = p - labels, p * (1 - p)
for lam in (0.0, 1.0, 10.0):
    w = -g[:3].sum() / (h[:3].sum() + lam)
    print(
        f"lambda={lam:4.1f} left weight={w:.3f} "
        f"left probability after rate .5: {special.expit(0.5 * w):.3f}"
    )
```

```text
lambda= 0.0 left weight=-2.000 left probability after rate .5: 0.269
lambda= 1.0 left weight=-0.857 left probability after rate .5: 0.394
lambda=10.0 left weight=-0.140 left probability after rate .5: 0.483
```

With no penalty, the left leaf takes the full Newton step of -2.000; after the 0.5 learning rate, its probability drops from 0.500 to 0.269. The guide setting \(\lambda=1\) gives -0.857 and a probability of 0.394. At \(\lambda=10\) the leaf barely moves, to 0.483. The gradient sum is the same 1.5 in all three rows; only the denominator changes. That matters most when a leaf holds few rows or rows with probabilities near zero or one, where \(H\) is tiny and an unpenalized step can become very large.

## Worked example: learning rate and the stopping stage

Run the staged validation curve at two learning rates on the nonlinear fixture.

```python
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error

rng = np.random.default_rng(1903)
x = rng.normal(size=(360, 6))
y = 3 * x[:, 0] + 2 * x[:, 1] ** 2 + rng.normal(scale=0.5, size=len(x))
for rate in (0.08, 0.3):
    model = GradientBoostingRegressor(
        n_estimators=100, learning_rate=rate, max_depth=2, random_state=4
    ).fit(x[:180], y[:180])
    val = [mean_squared_error(y[180:270], p) for p in model.staged_predict(x[180:270])]
    best = int(np.argmin(val)) + 1
    print(
        f"rate={rate}: stage 10={val[9]:.2f} stage 50={val[49]:.2f} "
        f"stage 100={val[99]:.2f} best stage={best} ({val[best - 1]:.2f})"
    )
```

```text
rate=0.08: stage 10=9.05 stage 50=2.07 stage 100=1.28 best stage=100 (1.28)
rate=0.3: stage 10=2.60 stage 50=1.23 stage 100=1.25 best stage=51 (1.22)
```

At rate 0.08, validation MSE falls from 9.05 at stage 10 to 2.07 at stage 50 and 1.28 at stage 100, and the best stage is 100, the last one allowed. A minimum at the edge of the search means the budget, not the data, chose the stopping point; extend the stage grid before trusting it. At rate 0.3 the curve is steeper, reaching 2.60 by stage 10, and its minimum of 1.22 occurs at stage 51; by stage 100 it has drifted back up only slightly, to 1.25. The two settings reach similar validation error, so the honest comparison is between tuned pairs of rate and stage count, not between equal numbers of trees.

## Failure modes when stopping boosting

Selecting the stage on the test rows turns the test score into a validation score. A minimum on the grid boundary signals an unfinished search. A very flat validation curve makes the chosen stage unstable across seeds, so report the curve, not only its argmin. Retraining on train plus validation with the same stage count changes the effective amount of fitting, because more rows support more stages.

Continue to [PCA](06-pca-compression-and-prediction.md). Primary derivation: [XGBoost boosted-tree tutorial](https://xgboost.readthedocs.io/en/stable/tutorials/model.html).
