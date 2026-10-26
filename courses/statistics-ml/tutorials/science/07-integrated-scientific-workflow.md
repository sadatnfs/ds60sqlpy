# Carry scientific evidence from data availability to a rollback decision

Tutorial ID: `statistics-science-007`. Prerequisites: `statistics-learning-003`, `statistics-learning-007`, `statistics-040`. Complete program: [science_07.py](examples/science_07.py).

## Begin with an availability contract

A predictive system receives events at time t, but labels become available at t+3. At training cutoff 240, only labels with availability at or before 240 can be used. A feature computed ten steps after the prediction event is also unavailable at prediction time, even if it appears beside the correct event timestamp in a current table.

The example constructs event and availability arrays, forms the training boundary, and rejects the future-derived feature by its availability rule. The test set uses later events whose labels have matured by a later evaluation cutoff. It contains 77 records; the training set contains 238. Unmatured outcomes are excluded from this defined evaluation rather than silently treated as negative labels.

## Fit and record a bounded artifact

A logistic model predicts a binary synthetic outcome from one available feature. The artifact record contains the model definition, label delay, cutoff, row counts, coefficients and intercept. Canonical JSON is hashed to identify that precise record. The code keeps the object in memory and prints the identity; it does not publish a model or claim a durable registry exists.

In a real pipeline, identity should also include input dataset/version, feature definitions, environment and code revision. A hash is a provenance handle, not proof that the underlying computation is correct. A reproducibly leaked model is still leaked.

The held-out log loss is about .559. That supports one prediction claim for the specified split and generating process. It does not establish that an intervention based on the score improves outcomes. An action that changes who receives service or labels can alter future training data and require causal evaluation.

## Change the environment and evaluate a response

The next synthetic population reverses the relationship between feature and outcome while the deployed model stays frozen. Its log loss rises to about 1.733, worse than an uninformed .5-probability baseline at .693. A prespecified margin .1 flags a rollback candidate.

This is a known concept-shift stress case. It demonstrates the measurement and decision calculation, not automatic production rollback. Real safeguards need enough mature labels, uncertainty around paired loss differences, subgroup checks, operational owners and an executable deployment mechanism. A data pipeline failure can mimic model drift, so diagnose data integrity before choosing the remedy.

## Connect existing engineering material

The repository already teaches [Arrow and DuckDB](../../../../python/professional/companion-guides/py_data_01_arrow_duckdb.md), [MLflow tracking](../../../../python/ds-60day/companion-guides/day53_mlops_mlflow_experiment_tracking.md) and [Prefect orchestration](../../../../python/ds-60day/companion-guides/day56_orchestration_prefect_intro.md). Use those declared environments to extend this in-memory case into data processing, artifact tracking and scheduling. Their existence should not be mistaken for evidence that this particular model was tracked, scheduled or deployed.

Keep source, run result, artifact identity, acceptance decision and actual deployment state distinct. A workflow can succeed operationally while its statistical assumptions fail. Conversely, a correct scientific calculation can fail to reach users because of a delivery defect. A useful investigation follows both chains without substituting one evidence type for the other.

**Answered discussion: Does a successful rerun establish recurrence?** It establishes that one execution completed under its recorded inputs and environment. Recurrence needs repeated scheduled executions and readback of their outputs. The example intentionally performs neither deployment nor scheduling.

Continue to [experiment decision memos](../experimentation/12-ramping-and-decision-memo.md). Scope reference: [Designing Machine Learning Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/titlepage01.html).
