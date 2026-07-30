# Resampling and experiments solution reasoning

Attempt `python-stats-01` before opening
[`py_stats_01_resampling_experiments_solution.py`](py_stats_01_resampling_experiments_solution.py).

The bootstrap resamples each observed arm independently and reports a
percentile interval for the difference in means. It quantifies sampling
uncertainty under an exchangeability assumption; it does not repair biased
assignment or missing outcomes. The permutation test pools outcomes under the
sharp null, enumerates all assignments when feasible, and otherwise uses a
seeded Monte Carlo estimate with a plus-one correction.

Standardized mean difference communicates effect magnitude in standard
deviation units. The Normal approximation gives a planning estimate, not a
guaranteed achieved power; final plans should reflect the actual metric,
variance, attrition, clustering, and test.

Holm adjustment controls family-wise error while being less conservative than
plain Bonferroni. Repeated unplanned peeking is another multiplicity problem;
the simple per-look alpha split illustrates planning but is not a substitute
for a designed group-sequential method.

Randomization supports causal claims only when assignment was implemented,
units did not interfere, outcome handling remained credible, and attrition did
not destroy comparability. Observational differences remain associational even
when bootstrap intervals are narrow.

Edge cases include zero variance, tiny groups, a metric chosen after seeing
results, assignment and analysis units that differ, cluster correlation,
noncompliance, missing outcomes, many secondary metrics, and stopping early
because an ordinary p-value crossed 0.05.

