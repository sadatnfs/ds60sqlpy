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

## Learner exercises and progressive hints

1. Log additional parameters such as Logistic Regression `C` and compare runs.
2. Save a confusion-matrix PNG and log it as an artifact.
3. Try a different classifier, such as Random Forest, and compare ROC AUC.

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
5. **Provenance manifest:** Log a JSON provenance artifact containing data fingerprint, code revision, dependency lock hash, feature schema, split policy, and metric definitions.
   **Progressive hint:** Use portable identifiers and hashes, not developer-specific absolute paths. Validate required fields before ending the run.
6. **Reload and signature check:** Log a fitted pipeline with an input example/signature, reload it by run URI, and assert prediction parity on a fixed fixture.
   **Progressive hint:** The fixture must use the documented schema and never come from hidden notebook state. Compare probabilities within a tolerance.

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
