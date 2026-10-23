# Leakage-Resistant Evaluation Across Groups and Time

**Stable ID:** `python-ml-02`

**Estimated time:** 270 minutes, split across sessions as needed.

## Level and prerequisites

Advanced. Direct catalog prerequisites: `python-35`, `python-data-02`.

You know evaluation, cross-validation, and explicit time boundaries. No deep-learning or NLP lessons are required. Python Day 50 is an optional forecasting follow-up. This lab uses a constant baseline and small records so evaluation policy can be inspected independently of model complexity.

## Learning objectives

- Choose held-out groups or forward time windows from the deployment question.
- Separate observation time, feature availability, and label availability.
- Fit preprocessing and baselines only from permitted training records.
- Audit fold membership, coverage, and error without treating one score as proof of deployment validity.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional native notebook/editor route:** the instructions below describe
separately prepared host tools. They are useful alternatives, not prerequisites
for opening this lesson in the Docker classroom.

Use the repository folder in VS Code. The rendered lesson page is a preview;
edit the actual [learner script](../lessons/py_ml_02_group_time_evaluation.py). Copy it to an ignored
folder under `.learning/` first if you want to keep your attempt across course
updates. Use the interpreter from setup. These examples need only Python's
standard library, have no network calls, and use the same inputs on each run.

Windows PowerShell:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython python\professional\lessons\py_ml_02_group_time_evaluation.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_ml_02_group_time_evaluation.py
```

The terminal shows a small worked example and the remaining TODO count.
TODOs are the starting exercise state. Write predictions before changing
code. Run after one change, save the observed value or exception, and compare
with the exercise's acceptance check. A successful example does not mean the
unfinished exercises are complete. Keep the separate
[explanatory solutions](../solutions/py_ml_02_group_time_evaluation_solutions.md) and
[runnable solution](../solutions/py_ml_02_group_time_evaluation_solution.py) closed until you have an
attempt and evidence, or deliberately ask for a worked comparison.

## Vocabulary and concepts

A test set represents a future decision, not merely a random fraction of
rows. If the system must predict for new customers, holding out rows from
customers already seen during training can answer the wrong question. If it
must operate next month, training on records whose labels arrived after the
decision date gives it information unavailable at the time. Start by naming
the information a real predictor would possess at its prediction instant.

- **Leakage:** information entering training or evaluation that would not
  have been available under the intended prediction conditions.
- **Group holdout:** keeping all records for selected entities outside
  training, used to study generalization to those unseen entities.
- **Observation time:** the instant at which the predictor must make its
  decision for a record in this lab.
- **Feature availability:** the earliest instant an input value is usable,
  which may be later than its source event time.
- **Label availability:** the instant the true target becomes known.
- **Embargo gap:** a declared interval before validation during which labels
  are not allowed into this training fold.
- **Walk-forward evaluation:** repeated training on permitted past data and
  scoring successive future windows.

Each Observation has an event id, entity id, observation instant, feature
availability instant, label availability instant, numeric feature, and target.
All timestamps must be aware. Features must be available by the observation
instant, and labels cannot become available before observation. Numeric values
must be finite. Event identities are unique. These are teaching assumptions,
not a claim that all applications reveal labels only after prediction.

Group holdout and time holdout answer different questions. The first excludes
entities globally; the second may allow returning entities whose past records
are legitimate training information. Neither split automatically proves the
other policy. If deployment requires both new entities and future time,
compose both constraints and audit the resulting smaller training set. Do not
claim group independence simply because row identities are disjoint.

## Worked example / walkthrough

### Example A: entity overlap can hide behind different row ids

```python
training = [{"event": "a1", "entity": "A"}, {"event": "b1", "entity": "B"}]
validation = [{"event": "a2", "entity": "A"}]
train_ids = {row["event"] for row in training}
test_ids = {row["event"] for row in validation}
train_entities = {row["entity"] for row in training}
test_entities = {row["entity"] for row in validation}
assert not train_ids & test_ids
assert train_entities & test_entities == {"A"}
```

Set intersection `&` reveals shared membership. Different event ids do not
guarantee different entities. Expected observation: no row overlap, but entity
A appears on both sides. That is a defect for an unseen-entity question and
may be allowed for a returning-entity future-time question. The score alone
cannot decide which question the experiment actually answers.

### Example B: delayed labels change the legal training set

```python
from datetime import datetime, timedelta, timezone

cutoff = datetime(2026, 1, 5, tzinfo=timezone.utc)
gap = timedelta(days=1)
label_available = datetime(2026, 1, 4, tzinfo=timezone.utc)
assert not (label_available < cutoff - gap)
assert label_available < cutoff
```

Expected observation: the label is earlier than validation but lies exactly
at the embargo boundary, so the declared strict-before training policy excludes
it. In this lab, training requires observation before cutoff and label
availability strictly before cutoff minus gap. Validation owns observations
in `[cutoff, end)` when an end is supplied. Excluded records are counted,
not silently forgotten. The boundary is conservative and explicit; other
applications can choose differently if they test and justify their policy.

### A baseline makes the experiment inspectable

Fit the constant prediction as the mean of permitted training targets. Score
mean absolute error on validation targets. This baseline is intentionally
simple enough to calculate by hand. For training targets zero and zero with a
held-out target one hundred, the permitted prediction is zero and the test
error is one hundred. Including the held-out target when fitting the mean
would improve that same test score, but make the experiment invalid.

The same restriction applies to feature scaling, imputation, feature selection,
and threshold tuning. Fit each learned transformation inside its training fold.
The reference mean-centering exercise checks feature fitting separately from
target fitting so these two uses of a mean are not confused. A final untouched
test set is still needed after selecting among modeling policies.

### Report coverage beside error

Each fold report should list training ids, validation ids, excluded count,
permitted training target mean, and validation MAE. Empty train or validation
sets fail visibly; a zero denominator does not become a fake score of zero.
When comparing policies, retain their membership and coverage so different
scores cannot conceal different evaluated populations. Repeated walk-forward
scores share training history and may share entities, so they are not automatic
independent confidence-interval samples. State those limits with the result.

## Exercises

1. **Validate availability before splitting.** Implement `validate_observations` to reject duplicate ids, naive timestamps, nonfinite numbers, features available after observation, and labels available before observation.

   **Verify:** Each rule has a named test that captures ValueError. Equality at feature availability and equality at label availability both complete validation without exceptions.

   **Hint:** The source boundary is checked before either split can hide an invalid record.

2. **Hold out whole entities.** Implement `group_split(rows, held_out)` using explicit entity ids. Preserve source order and require nonempty training and validation sets.

   **Verify:** Assert validation ids [A1, A2], training ids [B1, C1], and an empty entity-set intersection when A is held out; unknown or all-inclusive holdouts raise ValueError.

   **Hint:** Choose entities once, rather than selecting individual event rows.

3. **Enforce delayed-label time policy.** Implement `time_split` with aware cutoff, nonnegative gap, optional end, and strict label availability before cutoff minus gap.

   **Verify:** A label exactly at cutoff minus gap is excluded; a label one second earlier is eligible when observation is also earlier than cutoff.

   **Hint:** Write the predicate in words before combining its comparisons.

4. **Fit a transformation only on training.** Implement `fit_mean` and use it to center feature values. Train on [2, 4] and transform validation value 100 with the fitted mean.

   **Verify:** Training mean is 3, centered train values are -1 and 1, and centered validation is 97. Adding validation before fitting would change the mean and fails the test.

   **Hint:** Transforming validation uses existing state; it does not fit new state.

5. **Calculate a transparent baseline.** Implement `mae` and `evaluate_baseline` with the permitted training target mean. Use train targets [0, 0] and validation target [100].

   **Verify:** The fitted prediction is 0 and MAE is 100; empty sets, unequal metric input lengths, and nonfinite values raise ValueError.

   **Hint:** Validate both metric dimensions and numeric domain before calculating.

6. **Rehearse walk-forward windows.** Create two consecutive one-day validation windows over a tiny aware-timestamp fixture. Refit the baseline using only each fold eligible past.

   **Verify:** An observation at the shared boundary appears in the second validation window only; fold reports retain ids and counts for independent inspection.

   **Hint:** Use an explicit end on each fold so future validation rows are not scored repeatedly.

7. **Demonstrate a misleading improvement.** Intentionally fit the baseline mean on train plus validation in a scratch experiment. Compare its score with the valid [0,0] versus [100] case.

   **Verify:** The leaked mean is about 33.333 and test error about 66.667, lower than 100; your note identifies target leakage rather than model progress.

   **Hint:** A better score can be evidence of a broken experiment.

8. **Transfer to the deployment question.** Write policies for returning-customer next-day predictions and new-customer next-day predictions. Explain which group/time constraints each needs and what a final test set protects.

   **Verify:** The second policy explicitly checks both entity disjointness and future availability. Both report excluded coverage and reserve evaluation data outside policy selection.

   **Hint:** Do not reuse a tuned validation score as the final untouched estimate.

## Self-check

Without opening code, explain the three timestamps and their ordering. Give
an example where row ids are disjoint but the unseen-entity experiment is
invalid. Explain why lower error after using future targets is suspicious.
Describe one uncertainty that membership checks cannot settle, such as whether
future traffic matches the observed deployment population.

## Common pitfalls

If evaluation looks implausibly good, inspect fitted state and feature
availability before trying a more complex model. If one event is scored in two
folds, inspect the exclusive end boundary. If a fold unexpectedly empties,
report excluded ids and label delays. If the metric returns zero on no rows,
repair its preconditions. If entity sets overlap, compare that fact against
the declared question before calling it either acceptable or a defect.

## Next step

Bring these contracts into scikit-learn splitters, pipelines, and optional
forecasting work. Keep an independent membership audit next to the model code;
a library class name is useful documentation, not evidence that your inputs
and availability assumptions are correct.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for python-ml-02.
Read python/professional/companion-guides/py_ml_02_group_time_evaluation.md and python/professional/lessons/py_ml_02_group_time_evaluation.py.
Check my direct prerequisites: python-35, python-data-02.
Keep solutions/ closed unless I request comparison after an attempt.
Explain the mental model, ask me to predict one result, let me attempt it,
give one hint at a time, inspect my evidence, and ask a retrieval question.
Done when I can independently reproduce the numbered acceptance checks,
explain a failure case, and transfer the policy to a changed input.
```
