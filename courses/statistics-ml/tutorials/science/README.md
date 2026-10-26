# Connected scientific case studies

These original worked cases join identification, estimation, computation and
interpretation. Complete code and answered discussions remain visible. No
exam, independent submission or hidden solution is required.

| Case | What is carried through | Runtime |
| --- | --- | --- |
| [Causal estimation](01-causal-estimation-and-sensitivity.md) | Cross-fitted nuisances, AIPW, overlap, interval and bias sensitivity | Python Core |
| [Posterior prediction](02-posterior-prediction-and-decision.md) | Exact partial pooling, prior sensitivity and asymmetric loss | Python Core |
| [Forecasting](03-vintage-aware-forecasting.md) | Multiple series, rolling origins, delayed labels and revisions | Python Core |
| [Survival](04-survival-and-competing-events.md) | Actual Cox/AFT fits, censoring likelihood and competing incidence | Python Core |
| [Ranking and decisions](05-ranking-policy-and-allocation.md) | NDCG, logged-policy weighting and constrained allocation | Python Core |
| [Research synthesis](06-research-synthesis.md) | Effect harmonization, heterogeneity, intervals and sensitivity | Python Core |
| [Scientific workflow](07-integrated-scientific-workflow.md) | Availability boundaries, artifact identity, delayed evaluation and rollback evidence | Python Core |
| [Longitudinal regimes](08-longitudinal-regimes-and-target-trials.md) | Treatment-confounder feedback, sequential weighting and target-trial timing | Python Core |
| [PyMC hierarchy](09-pymc-hierarchy-and-diagnostics.md) | Prior/posterior prediction, MCMC diagnostics and pooling | Separately prepared Bayesian CPU |

Every linked program is self-contained. The first eight use only the existing
scientific stack. The ninth explicitly requires the separate versioned profile;
it is never imported by ordinary examples. Opening a guide does not fetch
packages or data. The durable numerical source is
[science_casebook.py](../authoring/science_casebook.py).

The printed outputs are evidence about deliberately bounded synthetic models.
They are not records of a production deployment, real causal acceptance or
universal statistical guarantees. Reference figures can be drawn later from
these values, but no interactive plotting dependency is needed to follow the
worked reasoning.

Return to [book contents](../../README.md), [learning foundations](../learning/README.md)
or the [experiment lifecycle](../experimentation/README.md).
