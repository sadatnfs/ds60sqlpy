## Predictive evaluation needs a held-out unit

A posterior predictive density evaluated on data used for fitting can be optimistic as a measure of future performance. Leave-one-out evaluation instead refits or approximates the posterior after removing a specified unit, then evaluates that unit's predictive density. The definition of the unit is fundamental: a row, user, cluster or time block can represent very different prediction questions.

The example compares an intercept-only normal model with a linear normal model on 12 synthetic observations. Observation scale is known, and both coefficient priors are normal. This creates an analytic refitting oracle in addition to actual PyMC sampling and ArviZ's Pareto-smoothed importance-sampling approximation.

## Worked case 1: compare PSIS with exact refitting

Both models produce pointwise log-likelihood arrays, and `az.loo` returns an estimated expected log predictive density together with Pareto-k diagnostics. Large Pareto-k values indicate unreliable importance-weight behavior for the approximation. A returned score is not automatically a trustworthy estimate merely because the function completed.

The program independently removes each observation and calculates the conjugate coefficient posterior from the remaining data. The held-out predictive distribution is normal with mean \(x_i^{\mathsf T}m_{-i}\) and variance \(\sigma^2+x_i^{\mathsf T}V_{-i}x_i\). Summing those held-out log densities gives an exact leave-one-out value for this model family.

The linear model has better exact predictive performance in the constructed relationship. The program reports each PSIS approximation error relative to the exact result and retains the warning flag and maximum Pareto k. The misspecified constant model can produce a particularly problematic approximation, demonstrating why diagnostic review must precede a model-selection interpretation.

In a general model, exact analytic refitting is unavailable. Targeted refits, a suitable alternative cross-validation design or other reviewed methods may be needed. A different estimator should be chosen because it addresses the observed problem, not because it produces a preferred model ranking.

## Worked case 2: change the predictive unit

For two outcomes sharing the same uncertain parameters, a joint posterior predictive density averages their likelihood product over the same posterior draw. Multiplying two marginal posterior predictive densities instead averages each separately. These operations generally differ:

\[
\log\mathbb E[p(y_1\mid\theta)p(y_2\mid\theta)\mid y]
\ne
\log\mathbb E[p(y_1\mid\theta)\mid y]
+\log\mathbb E[p(y_2\mid\theta)\mid y].
\]

The code calculates both quantities with stable log-sum-exp operations and checks that they are not equal. This is a dependency calculation, not a substitute for actually leaving a group out. It explains why the factorization and held-out unit must be reviewed before applying a row-wise evaluation tool.

Repeated observations from an existing user differ from observations for a new user whose latent effect has not been learned. Time forecasting differs from removing a random point in the middle of an otherwise observed series. Cross-validation must reproduce the relevant information boundary rather than defaulting to whichever factorization is easiest to obtain.

## Interpret predictive scores with uncertainty

A larger ELPD means a larger average log predictive density under the stated evaluation scheme. It does not automatically establish a practically important improvement or a causal benefit from deploying the model. Model differences, their uncertainty and the target population should be considered together.

Selecting repeatedly among many models using the same cross-validation results introduces selection. Preserve the search procedure and consider an independent final assessment where appropriate. A score for one fitted model is not automatically an unbiased evaluation of all the analyst decisions that produced it.

The demonstration uses short chains and retains imperfect diagnostics. The exact conjugate oracle is the source of its reliable comparison, while sampled PSIS values illustrate approximation behavior. Do not turn the tutorial's successful execution into a claim that every reported Monte Carlo score is suitable for a deployment decision.

## Answered scientific discussion

**Is a high Pareto k merely a warning to hide in the appendix?** It can challenge the numerical reliability of the approximation itself. Investigate influential observations, model misspecification and the need for a different evaluation computation.

**Why calculate exact leave-one-out in a small example?** It supplies an independent reference that reveals approximation error. The same discipline can be applied through targeted refits or simplified models when developing a larger Bayesian evaluation workflow.
