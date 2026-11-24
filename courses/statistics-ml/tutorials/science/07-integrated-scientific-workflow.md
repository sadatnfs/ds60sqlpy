# Carry scientific evidence from data availability to a rollback decision

Tutorial ID: `statistics-science-007`. Prerequisites: `statistics-learning-003`, `statistics-learning-007`, `statistics-040`. Complete program: [science_07.py](examples/science_07.py).

## Key terms

- **Availability contract:** Rules stating when each label and feature becomes usable, so training and prediction use only information present at that time.
- **Mature label:** An outcome whose delay has elapsed by the evaluation cutoff; unmatured outcomes are excluded rather than treated as negative labels.
- **Artifact record:** The model definition, label delay, cutoff, row counts, coefficients and intercept stored together and hashed as canonical JSON to identify the fit.
- **Concept shift:** A change in the relationship between features and outcome while the deployed model stays frozen.
- **Rollback margin:** A prespecified loss deterioration, .1 here, beyond which the deployed model becomes a rollback candidate.

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

## Worked example: three ways to draw the training set

Using the seed and data of `examples/science_07.py`, compare the availability-based training set with two tempting shortcuts, scoring each on the same 77 held-out events.

```python
import numpy as np
from scipy import special
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

rng = np.random.default_rng(4007)
x = rng.normal(size=360)
y = rng.binomial(1, special.expit(1.8 * x))
event = np.arange(360)
test = (event > 240) & (event + 3 <= 320)
for name, train in (
    ("labels available by 240", event + 3 <= 240),
    ("all events up to 240", event <= 240),
    ("random 238 rows incl. test", np.isin(event, rng.choice(320, 238, replace=False))),
):
    model = LogisticRegression().fit(x[train, None], y[train])
    overlap = np.sum(train & test)
    print(
        f"{name:27s} rows {train.sum():3d} test overlap {overlap:2d} "
        f"loss {log_loss(y[test], model.predict_proba(x[test, None])[:, 1]):.3f}"
    )
```

```text
labels available by 240     rows 238 test overlap  0 loss 0.559
all events up to 240        rows 241 test overlap  0 loss 0.558
random 238 rows incl. test  rows 238 test overlap 56 loss 0.543
```

The availability rule yields 238 rows and a held-out log loss of 0.559. Selecting every event up to 240 adds three rows whose labels did not exist at the cutoff; the loss barely moves to 0.558, which is precisely why this leak is hard to notice: it does not show up in the score, only in an audit of what production could have known. Sampling 238 rows at random from the first 320 events puts 56 test rows into training and produces 0.543, a better number earned by memorizing evaluation outcomes. With a stronger model than one logistic coefficient, that gap would widen.

## Worked example: how much shift triggers the rule

The guide applies the rollback rule to one reversed population. Sweeping the true slope from the original 1.8 down to -1.8 shows where the margin of 0.1 above the coin-flip loss of 0.693 starts to fire.

```python
import numpy as np
from scipy import special
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

rng = np.random.default_rng(4007)
x = rng.normal(size=360)
y = rng.binomial(1, special.expit(1.8 * x))
model = LogisticRegression().fit(x[:238, None], y[:238])
for slope in (1.8, 0.9, 0.0, -0.9, -1.8):
    sx = rng.normal(size=500)
    sy = rng.binomial(1, special.expit(slope * sx))
    loss = log_loss(sy, model.predict_proba(sx[:, None])[:, 1])
    print(f"true slope {slope:5.1f}: model loss {loss:.3f} flag {loss > np.log(2) + 0.1}")
```

```text
true slope   1.8: model loss 0.478 flag False
true slope   0.9: model loss 0.678 flag False
true slope   0.0: model loss 1.095 flag True
true slope  -0.9: model loss 1.412 flag True
true slope  -1.8: model loss 1.693 flag True
```

With the original relationship the frozen model scores 0.478. Halving the slope to 0.9 raises the loss to 0.678, which is worse but still under the 0.793 threshold, so no flag appears even though the model is overconfident. At slope zero the feature is useless, the loss reaches 1.095 and the rule fires. The reversed case gives 1.693 here; the guide reports about 1.733 because its shifted sample comes from a later point in the random stream. The sweep shows that a fixed margin catches severe shift but stays silent through moderate decay, so a monitor should also track calibration and loss trend, not just a single threshold crossing.

## Failure modes in a delivery workflow

Feature tables rebuilt from current data can embed values that did not exist at prediction time. Labels counted as negative before they mature bias both training and monitoring toward the negative class. Hashes computed over a record that omits the data version give the same identity to two different models. A rollback rule evaluated on immature labels can trigger on noise.

Continue to [experiment decision memos](../experimentation/12-ramping-and-decision-memo.md). Scope reference: [Designing Machine Learning Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/titlepage01.html).
