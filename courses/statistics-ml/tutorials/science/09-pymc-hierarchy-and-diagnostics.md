# Fit a hierarchical model and inspect what the sampler actually learned

Tutorial ID: `statistics-science-009`. Prerequisites: `statistics-science-002`, `statistics-018`. Complete program: [science_09.py](examples/science_09.py). Execution profile: **bayesian-cpu**, with deliberately pinned PyMC 5.28.5 and ArviZ 0.23.4. This is a separately prepared optional scientific runtime; reading the tutorial does not install or execute anything.

## Define a complete generative model

Six groups have unequal sample sizes 3,5,8,10,12,15. Observations vary around group means with common noise. Instead of treating population center and variances as known, estimate them jointly:

\[
\mu\sim N(0,2^2),\quad \tau\sim\operatorname{HalfNormal}(1),\quad
z_j\sim N(0,1),\quad \theta_j=\mu+\tau z_j,
\]
\[
\sigma\sim\operatorname{HalfNormal}(2),\qquad
Y_{ij}\sim N(\theta_j,\sigma^2).
\]

The noncentered z representation can improve geometry when group information is weak. It is not universally superior; informative groups can favor other parameterizations. The prior scales are in outcome units, so rescaling observations requires reconsidering the priors.

## Simulate before conditioning

Prior predictive draws generate population parameters, group means and complete outcomes. Inspect their spread and tails against what the measurement scale permits. A mathematically proper prior can still imply absurd datasets. The example reports prior predictive spread, then samples the posterior using two chains, 600 warmup iterations and 600 retained draws per chain, with one CPU process and a fixed seed.

These bounded settings support a small teaching case. They are not a general recommendation for every posterior. The first invocation may compile model operations, while later process behavior depends on the prepared runtime's cache contract. Do not claim an interactive session persists across classroom Run actions.

## Distinguish sampling diagnostics from model adequacy

ArviZ's summary reports rank-based R-hat, bulk and tail effective sample sizes, and Monte Carlo SE. R-hat near one is useful evidence that chains behave similarly; it does not prove they explored every isolated mode. Effective sample size differs from raw draw count because draws are autocorrelated. Monte Carlo SE measures simulation error in posterior summaries, not scientific uncertainty in the parameter.

The program reports divergences and preserves diagnostic values even when they are unfavorable. It does not assert that a finite posterior mean or a successful sampler return establishes convergence. Divergences can reveal difficult posterior geometry; inspect parameterization, priors and the model before simply increasing the acceptance target or discarding problematic draws.

For example, a bounded run can report no divergences while its maximum R-hat is about 1.02 and minimum bulk effective sample size is only about 133. That is useful runtime and diagnostic evidence, but it is not adequate grounds to claim a well-explored posterior. More chains/draws, diagnostic inspection and a model-appropriate investigation are needed before relying on precise posterior summaries. A CPU execution or a successful assertion must not erase this limitation.

This route intentionally uses the PyMC 5 / ArviZ 0.x `InferenceData` contract. PyMC 6 / ArviZ 1.x introduce a different data-object ecosystem. Do not combine current-major example snippets with this pinned environment without a deliberate migration and new qualification.

## Check predictive behavior and pooling

Posterior predictive draws add new observation noise to posterior parameter draws. Compare observed and predicted spread, group means, outliers and any decision-relevant tails. The example prints observed group means beside posterior group means, making shrinkage visible, and reports predictive versus observed spread. An overall SD agreement alone is a deliberately limited check; it can hide wrong subgroup tails or missing time structure.

The preceding exact-normal unit varies prior scale and computes a decision loss. Carry those questions into this fitted hierarchy: does stronger shrinkage change the action, and does the result remain stable under a scientifically plausible alternative likelihood? Comparing pooled and unpooled models should include predictive checks and the target decision, not just which table has narrower intervals.

**Answered discussion: What does the program's successful assertion establish?** It verifies the expected data structure, available diagnostics, finite predictive values and matching observation dimensions. It does not certify posterior convergence or that the normal model is adequate for a real dataset. Interpret the printed diagnostic evidence explicitly.

Versioned reference: [ArviZ 0.23.4 summary](https://python.arviz.org/en/v0.23.4/api/generated/arviz.summary.html). Model/API source: [PyMC 5.28.5 release](https://github.com/pymc-devs/pymc/releases/tag/v5.28.5). Return to [scientific cases](README.md).
