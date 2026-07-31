# Day 53 — Experiment Tracking with MLflow

**Lesson ID:** `python-53` · **Level:** advanced · **Dependencies:** `production` · **Network:** offline

Experiment tracking connects a result to its parameters, metrics, code context,
and artifacts. MLflow can run entirely on the local machine for this lesson; no
hosted service or account is required.

## Learning objectives

By the end of the lesson, you can:

- organize local MLflow experiments and runs;
- log explicit parameters, metrics, and plot artifacts;
- save a fitted scikit-learn model under a run;
- reload an artifact by run URI; and
- distinguish tracking, artifact storage, registry workflow, and reproducibility.

## Prerequisites

- Complete `python-52` (scalable computation).
- Recall model evaluation and saved pipelines.
- Install the `production` dependency group.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Experiment | Named collection of related runs |
| Run | One execution with parameters, metrics, tags, and artifacts |
| Parameter | Configuration intended to remain fixed during a run |
| Metric | Numeric measurement, optionally recorded over steps |
| Artifact | File output such as a plot, model, or report |
| Tracking store | Metadata location for experiments and runs |
| Artifact store | Location containing run files |
| Model registry | Versioned promotion and governance layer beyond basic tracking |

Tracking proves what was logged, not that the data were valid or the run can be
reproduced. Record dataset identity, code revision, environment lock, and seed
alongside model hyperparameters.

## Worked example: one explicit local run

```python
import mlflow
import mlflow.sklearn

mlflow.set_experiment("ds60-local-experiment")
with mlflow.start_run(run_name="baseline") as run:
    mlflow.log_param("model", "LogisticRegression")
    mlflow.log_param("random_state", 42)
    mlflow.log_metric("roc_auc", 0.91)
    # After fitting:
    # mlflow.sklearn.log_model(pipeline, artifact_path="model")
    print(run.info.run_id)
```

Use actual calculated metrics in the notebook; the literal metric above only
shows the logging API. Keep `mlruns/` as a learner-local ignored artifact, not a
source file to commit.

## View the local UI

macOS/Linux:

```bash
.venv/bin/mlflow ui --backend-store-uri mlruns
```

Windows PowerShell:

```powershell
.\.venv\Scripts\mlflow.exe ui --backend-store-uri mlruns
```

Open `http://127.0.0.1:5000`, and stop the process with Ctrl+C when finished.
The server binds locally and the lesson works offline.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 53 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — MLflow run identity, params, metrics, artifacts, and reproducible evidence

### The mental model

Experiment tracking records evidence about a run; it does not make the
run reproducible by itself. An experiment groups comparable runs. A run
represents one execution. Parameters describe configuration, metrics
are numeric observations (possibly by step), tags add searchable
context, and artifacts preserve files or models.

Comparability requires the same data/split/metric definitions. A model
artifact should carry an input example/signature and provenance. Local
file tracking is useful for study but is not a shared registry, access
control system, or backup.

### Worked examples and syntax anatomy

- **`with mlflow.start_run():`:** creates a bounded lifecycle so successful and failed runs receive terminal status.
- **`log_param` versus `log_metric`:** stores fixed configuration separately from numeric measurements that may evolve by step.
- **`log_artifact` / model logging:** copies output into the run's artifact store; verify reload and input contract rather than trusting existence.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — separate comparable configuration from results

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
run_record = {
    "params": {
        "model": "logistic_regression",
        "C": 1.0,
        "split_seed": 5301,
        "data_snapshot": "sha256:example",
    },
    "metrics": {
        "validation_roc_auc": 0.91,
        "test_roc_auc": 0.89,
    },
    "tags": {
        "purpose": "course-baseline",
        "metric_definition": "roc_auc",
    },
}
assert "validation_roc_auc" not in run_record["params"]
print(run_record)
```

**Expected observation:** Configuration, measured outcomes, and contextual labels are distinct, making search and comparison less ambiguous.

**Assumption to name:** The data snapshot and metric definition are stable enough that two records are actually comparable.

### Focused example B — create and inspect a fully local temporary run

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import mlflow

original_uri = mlflow.get_tracking_uri()
with TemporaryDirectory() as directory:
    mlflow.set_tracking_uri(Path(directory).as_uri())
    mlflow.set_experiment("day53-local-mechanics")
    with mlflow.start_run(run_name="bounded-example") as active:
        mlflow.log_param("alpha", 0.1)
        mlflow.log_metric("validation_score", 0.8)
        run_id = active.info.run_id
    recorded = mlflow.get_run(run_id)
    print(recorded.info.status, recorded.data.params, recorded.data.metrics)
    assert recorded.info.status == "FINISHED"
mlflow.set_tracking_uri(original_uri)
```

**Expected observation:** The context manager closes the run as FINISHED, and the parameter/metric are queryable from a local temporary tracking store.

**Assumption to name:** The temporary store proves API mechanics only; it is intentionally deleted and not a durable team record.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define MLflow run identity, params, metrics, artifacts, and reproducible evidence in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Comparing runs with different splits/metrics or logging only the model score while omitting data and environment identity.

**Debug it deliberately:** Query the run by ID, inspect status/params/metrics/tags/artifacts, reload the model in a fresh process, and reconcile inputs and predictions.

**Stop condition:** Do not promote the top UI row without acceptance gates, comparable evidence, artifact verification, and ownership.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Log additional parameters such as Logistic Regression `C` and compare runs.

**Verify:** For task `Log additional parameters such as Logistic Regression C and compare runs`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.






2. Save a confusion-matrix PNG and log it as an artifact.

**Verify:** For task `Save a confusion-matrix PNG and log it as an artifact`, verify identity/hash and metadata, then reload or inspect the artifact outside the creating state and test one tampered mismatch.






3. Try a different classifier, such as Random Forest, and compare ROC AUC.

**Verify:** For task `Try a different classifier, such as Random Forest, and compare ROC AUC`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Progressive hints

1. Make one run per configuration and include split seed, metric name, and model
   type. Avoid changing several uncontrolled factors at once.
2. Save figures under an ignored `artifacts/` directory, close the figure, and
   pass the path to `mlflow.log_artifact`.
3. Reuse exactly the same train/test split. Compare runtime and complexity as
   well as score.

The reference solution adds scikit-learn autologging and model reload. Start
with explicit logging so you know which information is essential; use autolog
as a supplement, not as a substitute for experiment design.

### Additional mastery practice

Make experiment records reconstructable: status, parameters, data/code identity, metrics, artifacts, and model signature must describe one coherent run.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Failure-state handling:** Run an experiment that intentionally raises after logging parameters. Verify MLflow records a failed status and useful exception context without exposing raw data or secrets.
   **Progressive hint:** Use the run context manager so exception exit marks the run failed. Log safe stage/status information before re-raising.

**Verify:** For task `Failure-state handling: Run an experiment that intentionally raises after logging parameters....`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.







5. **Provenance manifest:** Log a JSON provenance artifact containing data fingerprint, code revision, dependency lock hash, feature schema, split policy, and metric definitions.
   **Progressive hint:** Use portable identifiers and hashes, not developer-specific absolute paths. Validate required fields before ending the run.

**Verify:** For task `Provenance manifest: Log a JSON provenance artifact containing data fingerprint, code revisio...`, record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state; then assert exact names, order, types/nullability or versions and prove one mismatch is rejected rather than silently coerced.







6. **Reload and signature check:** Log a fitted pipeline with an input example/signature, reload it by run URI, and assert prediction parity on a fixed fixture.
   **Progressive hint:** The fixture must use the documented schema and never come from hidden notebook state. Compare probabilities within a tolerance.

**Verify:** For task `Reload and signature check: Log a fitted pipeline with an input example/signature, reload it...`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.






Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.



## Self-check

- What uniquely identifies the logged model artifact?
- Which facts are missing if you log only ROC AUC and `C`?
- Why should the final holdout not become a leaderboard across many runs?
- What is the difference between a tracking run and an approved production
  model version?

Expected behavior: runs and artifacts appear in the local UI, and reloading a
model from `runs:/<run_id>/model` reproduces predictions on the same input.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Likely cause | Response |
|---|---|---|
| Runs appear in different stores | Working directory/tracking URI changed | Set and document the local URI |
| Nested/duplicate runs appear | Autolog and manual contexts overlap | Decide the intended run structure |
| Artifact cannot be loaded | Wrong run ID or artifact path | Inspect the run's artifact tree in UI |
| Repository becomes huge | Local `mlruns/` committed | Keep learner artifacts ignored |
| Metrics are incomparable | Split/data/metric definition changed | Log data identity and evaluation protocol |

Local file tracking is ideal for learning and one user. Team use needs durable
backends, access controls, retention, backup, and an explicit promotion process.

## Next step

- Work in the [Day 53 learner notebook](../notebooks/day53_mlops_mlflow_experiment_tracking.ipynb).
- Then consult the
  [Day 53 solution](../solutions/day53_mlops_mlflow_experiment_tracking/day53_solutions.md).
- Continue to [Day 54 — Monitoring and Governance](day54_monitoring_model_governance.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-53` — Day 53 — Experiment Tracking with MLflow.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize MLflow run identity, params, metrics, artifacts, and reproducible evidence. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day53_mlops_mlflow_experiment_tracking.md`
- learner artifact: `python/ds-60day/notebooks/day53_mlops_mlflow_experiment_tracking.ipynb`

Assume only the prerequisites declared in the guide. Do not open or
quote anything under `solutions/` unless I explicitly ask after an
honest attempt. First explain one concept in plain language and show a
tiny example. Then ask me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
