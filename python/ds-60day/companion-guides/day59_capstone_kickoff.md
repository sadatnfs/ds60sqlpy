# Day 59 — Capstone Kickoff

**Lesson ID:** `python-59` · **Level:** advanced · **Dependencies:** `advanced` · **Network:** offline

Today you freeze a feasible problem, evaluation plan, and reproducible project
skeleton. A strong capstone is a defensible, runnable argument—not a large pile
of techniques.

## Learning objectives

By the end of the lesson, you can:

- write a problem statement tied to a decision and stakeholder;
- choose an offline-capable dataset with a documented license/source;
- define a baseline, primary metric, guardrails, and acceptance criteria;
- create a tested project skeleton with an initial baseline; and
- record risks involving leakage, privacy, fairness, security, and operations.

## Prerequisites

- Complete `python-58` and the full preceding Python track.
- Choose a project scope runnable on one CPU laptop.
- Use local, generated, package-bundled, or intentionally cached data. Do not
  make a live API part of the reproducible default.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Stakeholder | Person or group using, affected by, or accountable for the result |
| Decision | Action the analysis or model is intended to inform |
| Baseline | Simplest credible comparison |
| Primary metric | Declared measurement used for the main success claim |
| Guardrail | Constraint that must remain acceptable while optimizing the primary metric |
| Acceptance criterion | Threshold plus evidence protocol required for completion |
| Data contract | Schema, meaning, quality, ownership, freshness, and allowed use |
| Reproducibility manifest | Code, data identity, environment, seed, and commands needed to rebuild evidence |

## Scope template

Complete each statement before choosing a complex model:

- **Decision:** We help `<stakeholder>` decide `<action>`.
- **Prediction/analysis unit:** One row represents `<unit at time>`.
- **Target or outcome:** `<definition and availability time>`.
- **Primary metric:** `<metric>` because `<error-cost rationale>`.
- **Baseline:** `<simple rule/model>`.
- **Guardrails:** `<privacy, subgroup, latency, memory, calibration, cost>`.
- **Acceptance:** On a frozen `<split/backtest>`, the candidate must
  `<criterion>` while every guardrail `<criterion>`.
- **Out of scope:** `<uses or populations not supported>`.

Avoid inventing a target number before seeing baseline variability and decision
requirements. Criteria should be ambitious enough to matter and honest enough
to test.

## Recommended project skeleton

```text
capstone/
  data/README.md          # source, license, schema; large/private data ignored
  notebooks/              # EDA and communication, not hidden production state
  src/capstone/           # importable data/features/model/evaluation modules
  tests/                  # unit, contract, and smoke tests
  artifacts/              # ignored generated models/figures/metrics
  pyproject.toml
  uv.lock                 # or another reviewed lock for this project
  README.md
```

The learner notebook shows `requirements.txt`; a `pyproject.toml` plus reviewed
lock is the more complete project form taught by the current repository.

## Day 59 evidence gates

| Gate | Evidence due today |
|---|---|
| Scope | Problem, decision, affected stakeholders, out-of-scope uses |
| Data | Local acquisition path, license/permission, row unit, schema, target timing |
| Split | Frozen holdout/backtest/group strategy and leakage rationale |
| Baseline | Reproducible code plus recorded metric and variability |
| Quality | Missingness/duplicates/range checks and one automated contract test |
| Risk | Privacy classification, subgroup plan, threat/abuse case, limitations |
| Reproduction | Fresh-environment setup and exact baseline command |
| Plan | Remaining experiments ranked by expected learning value |

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 59 learner notebook from this guide's **Next
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

## Concept deep dive — capstone scope, decision framing, data contracts, and early stop rules

### The mental model

A capstone begins with a decision and stakeholder, not an algorithm.
The problem statement identifies who acts, what prediction or analysis
is available at that moment, and what outcome changes. A baseline,
primary metric, guardrails, and acceptance threshold make success
falsifiable.

A data contract records source/license, row grain, keys, schema,
missingness, time boundary, target construction, and prohibited fields.
A risk register covers leakage, privacy, fairness, security, operations,
and uncertainty. Stop rules prevent endless tuning when data or evidence
cannot support the proposed claim.

### Worked examples and syntax anatomy

- **decision statement:** names stakeholder, action, prediction time, and consequence before selecting a model.
- **acceptance matrix:** connects each success/guardrail threshold to data, metric, owner, and verification command.
- **milestone checkpoint:** produces a reviewable artifact and explicit continue/pivot/stop decision.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — validate a project charter as data

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
charter = {
    "stakeholder": "course reviewer",
    "decision": "prioritize which records receive manual review",
    "prediction_time": "after validation, before review",
    "baseline": "review in arrival order",
    "primary_metric": "recall at fixed review capacity",
    "guardrails": ["no prohibited identifiers", "latency under 100 ms"],
    "stop_rule": "stop if target cannot be reproduced from source evidence",
}
required = {
    "stakeholder", "decision", "prediction_time", "baseline",
    "primary_metric", "guardrails", "stop_rule",
}
missing = required - charter.keys()
print({"missing": sorted(missing), "charter": charter})
assert not missing
```

**Expected observation:** The charter is reviewable because every required decision field has a concrete value.

**Assumption to name:** The stakeholder confirms the metric and capacity actually reflect the intended action.

### Focused example B — turn a claim into predeclared acceptance checks

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
acceptance = [
    {"name": "quality", "observed": 1.0, "operator": ">=", "threshold": 1.0},
    {"name": "recall_at_capacity", "observed": 0.82, "operator": ">=", "threshold": 0.80},
    {"name": "latency_ms", "observed": 42, "operator": "<=", "threshold": 100},
]

def passes(item):
    return (
        item["observed"] >= item["threshold"]
        if item["operator"] == ">="
        else item["observed"] <= item["threshold"]
    )

results = {item["name"]: passes(item) for item in acceptance}
print(results)
assert all(results.values())
```

**Expected observation:** Each claim has direction, threshold, and observed evidence instead of a vague 'good enough' judgment.

**Assumption to name:** Thresholds were approved before final evaluation and each observation comes from the declared evidence boundary.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define capstone scope, decision framing, data contracts, and early stop rules in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Choosing a large dataset or fashionable model before defining the decision, prediction time, baseline, and harm constraints.

**Debug it deliberately:** Ask what row exists at prediction time, who acts on the output, what simple alternative exists, and which evidence would force a stop.

**Stop condition:** Pause or pivot when target provenance, data license, leakage boundary, stakeholder decision, or feasible baseline cannot be established.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Write the problem statement and success metric in the notebook.

**Verify:** For task `Write the problem statement and success metric in the notebook`, demonstrate the concrete requirement “1. Write the problem statement and success metric in the notebook” with explicit inputs, observable output, and one counterexample.






2. Create the project skeleton.

**Verify:** For task `Create the project skeleton`, demonstrate the concrete requirement “2. Create the project skeleton” with explicit inputs, observable output, and one counterexample.






3. Build a baseline and record metrics.

**Verify:** For task `Build a baseline and record metrics`, record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.







### Progressive hints

1. Start with the decision and cost of errors; select the metric afterward.
2. Add `README`, `pyproject.toml`, `src`, `tests`, and ignored `artifacts` before
   adding more notebooks.
3. Use the simplest credible model/rule and frozen split. Save metrics as a
   small machine-readable artifact and explain them in prose.

The reference solution includes example warehouse/API source text as a planning
template. Those are placeholders, not course dependencies; your default
capstone must remain reproducible offline.

### Additional mastery practice

Start the capstone with a decision, bounded scope, data contract, baseline, and experiment log. A small reproducible question is stronger than an expansive vague project.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Scope and stop rules:** Write must-have, should-have, and out-of-scope lists plus kill criteria for unavailable data, inadequate support, unacceptable harm, or missed minimum baseline value.
   **Progressive hint:** Time-box discovery and name the evidence that triggers pivot, pause, or stop. Do not make deployment the default capstone requirement.

**Verify:** For task `Scope and stop rules: Write must-have, should-have, and out-of-scope lists plus kill criteria...`, demonstrate the concrete requirement “4. Scope and stop rules: Write must-have, should-have, and out-of-scope lists plus kill criteria for unavailable data, inadequate support, unacceptable harm, or missed minimum base” with explicit inputs, observable output, and one counterexample.







5. **Capstone data contract:** Create a versioned schema and quality report for your chosen local dataset, including source/license, row unit, target, types, ranges, missingness, duplicates, split keys, and fingerprint.
   **Progressive hint:** Use a tiny valid fixture and deliberately invalid fixture to test the validator.

**Verify:** For task `Capstone data contract: Create a versioned schema and quality report for your chosen local da...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







6. **Decision log:** Record at least five project decisions with date, question, alternatives, evidence, chosen action, consequences, and revisit trigger.
   **Progressive hint:** Include split/metric/baseline choices, not only model hyperparameters. Link each result to a reproducible command or notebook cell.

**Verify:** For task `Decision log: Record at least five project decisions with date, question, alternatives, evide...`, report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels; then show the relevant row/group/time identities and assert the training and evaluation information boundaries are disjoint.






Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.



## Self-check

- Can someone state what one prediction means and when its features are known?
- Does the baseline execute from a clean environment with one documented
  command?
- Which result would falsify the project's main claim?
- What data cannot be committed or sent to an assistant?
- Which stakeholder can challenge, appeal, or stop harmful use?

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Response |
|---|---|---|
| “Build an accurate model” as scope | No decision or finish line | Define user, action, metric, and constraints |
| Dataset chosen only for size | Laptop project stalls | Sample responsibly or choose bounded local data |
| Metric target chosen after results | Moving goalposts | Freeze criteria and protocol early |
| Baseline omitted | Complexity has no reference | Implement a simple rule/model first |
| Private data copied into repo | Security/privacy incident | Use synthetic/public data and documented ignores |
| Presentation postponed | Evidence lacks narrative | Draft one result table/visual and limitations now |

## Next step

- Build in the [Day 59 learner notebook](../notebooks/day59_capstone_kickoff.ipynb).
- Then review the
  [Day 59 solution](../solutions/day59_capstone_kickoff/day59_solutions.md).
- Continue to [Day 60 — Completion and Presentation](day60_capstone_completion_presentation.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-59` — Day 59 — Capstone Kickoff.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize capstone scope, decision framing, data contracts, and early stop rules. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day59_capstone_kickoff.md`
- learner artifact: `python/ds-60day/notebooks/day59_capstone_kickoff.ipynb`

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
