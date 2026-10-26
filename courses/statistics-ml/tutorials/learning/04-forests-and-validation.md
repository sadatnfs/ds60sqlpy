# Random forests: diversity is a mechanism to measure

Tutorial ID: `statistics-learning-004`. Prerequisites: `statistics-learning-001`, `statistics-019`, `statistics-022`. Complete program: [learning_03.py](examples/learning_03.py).

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

Continue to [boosting](05-boosting-loss-and-stopping.md). Official reference: [RandomForestRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html).
