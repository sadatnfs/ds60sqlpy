# Leakage-Resistant Evaluation Across Groups and Time: solution reasoning

Stable ID: `python-ml-02`.

Read the [guide](../companion-guides/py_ml_02_group_time_evaluation.md) and attempt the [learner artifact](../lessons/py_ml_02_group_time_evaluation.py) first. The [executable solution](py_ml_02_group_time_evaluation_solution.py) is a comparison implementation. It does not certify your changed program merely because its own demonstration succeeds. Copy the acceptance cases into your attempt, then change one input without changing the intended policy.

The reference separates source validation, split policy, fitted
state, and metric calculation. A constant predictor makes it possible to
check the entire experiment by hand. There is no estimator dependency and no
random split hiding membership. A production model can replace the baseline
later without changing the availability questions.

```python
permitted_targets = [0.0, 0.0]
prediction = sum(permitted_targets) / len(permitted_targets)
assert abs(100.0 - prediction) == 100.0
```

The report retains identities and population sizes beside the score. A score
from an empty set is rejected. Group and time splits remain separate because
the intended deployment question decides whether both constraints apply.
Membership evidence does not establish that the sampled population represents
future demand, nor does it prove causal effects.

## Exercise 1. Validate availability before splitting

Validate the whole source before choosing a subset. Event ids must be nonempty trimmed strings and unique; entity ids must be nonempty trimmed strings. Timestamps must have usable offsets and are compared as instants. A feature becoming usable after observation is future information. A label earlier than observation violates the teaching record contract. Equality is permitted at either availability boundary. Reject nonfinite features and targets, including booleans masquerading as numbers. These checks address representation and declared availability, not whether the recorded timestamps are factually accurate.

## Exercise 2. Hold out whole entities

The held-out set names entities, so every record for A enters validation and none enters training. Source ordering is preserved for inspectable comparisons. Requiring both sides to contain data prevents a meaningless score when the requested holdout is absent or includes the entire source. The reference also rejects unknown held-out entities, making a misspelled group visible. Entity intersection is checked independently of event-id intersection. A time split may legitimately retain the same returning entity on both sides, so keep the experiment question beside the membership assertions.

## Exercise 3. Enforce delayed-label time policy

Training requires observation before cutoff and label availability strictly before cutoff minus the nonnegative gap. The optional validation end must follow cutoff and is exclusive. A label exactly at the embargo threshold is excluded under the declared conservative rule; moving it one second earlier makes it eligible if observation also precedes cutoff. Records after the validation end or with unavailable training labels contribute to excluded_count. The source count must equal training plus validation plus excluded. This policy does not guess or backfill labels unavailable at the historical decision point.

## Exercise 4. Fit a transformation only on training

Fit the mean from training feature values two and four, yielding three. Subtract that already-fitted mean from both training and validation values. The validation value one hundred therefore becomes ninety-seven. Including it while fitting yields a different parameter and contaminates the experiment, even though no target was used. This is transformation leakage. Keep the learned state explicit so a test can inspect it. In a larger pipeline, fit imputation, scaling, feature selection, and other learned preprocessing inside each fold rather than once before splitting.

## Exercise 5. Calculate a transparent baseline

The training target mean of zero and zero is zero. Repeating that prediction for the validation target one hundred produces MAE one hundred. The metric validates equal nonzero lengths and finite numeric values before calculating. The report rejects shared event ids so a caller cannot score the exact same record it trained on. It does not require entity disjointness universally because a returning-entity time policy may allow overlap. A metric should report its unit and aggregation; MAE here has the target's units and weights each validation record equally.

## Exercise 6. Rehearse walk-forward windows

Build each forward fold with an explicit cutoff and next boundary. The half-open end prevents a shared-boundary event from appearing in both adjacent validation windows. Refit using the permitted past and the same availability predicate each time. An earlier validation event may later become legal training information once its label is available; that is normal walk-forward behavior rather than leakage. Preserve ids, exclusion counts, and fitted means in each report. These folds share history and may share entities, so treating their scores as independent observations for uncertainty would need additional justification.

## Exercise 7. Demonstrate a misleading improvement

The deliberately leaked training mean includes target one hundred and becomes roughly thirty-three and one third. Its validation absolute error becomes roughly sixty-six and two thirds, appearing better than the permitted error one hundred. That numerical improvement is produced by using the answer during fitting. The exercise is intentionally a scratch comparison, not a recommended implementation. Retain it as a diagnostic demonstration that model-selection pressure can reward invalid experiments. A model should never choose its own availability rules based on which rules produce the best held-out score.

## Exercise 8. Transfer to the deployment question

Returning-customer next-day prediction needs forward-time availability and may use prior records for the same customer. New-customer next-day prediction additionally needs customer-level exclusion so no historical record for that customer enters training. Both need feature availability checks, label delay policy, explicit gap where appropriate, and coverage reporting. A final test set protects against adapting repeatedly to validation results while selecting these policies. It cannot guarantee the future population remains unchanged. State that limitation and monitor deployment inputs rather than presenting a split as permanent acceptance evidence.

## Compare and transfer

Create a feature that was computed one day after prediction but carries an older source event date. Explain why filtering only on source date still leaks. Then compare entity-weighted and record-weighted evaluation for a customer with many events. Those are different estimands; write down the target question before choosing the metric weighting.
