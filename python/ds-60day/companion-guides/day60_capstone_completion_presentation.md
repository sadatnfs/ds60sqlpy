# Day 60 — Capstone Completion and Presentation

**Lesson ID:** `python-60` · **Level:** advanced · **Dependencies:** `advanced` · **Network:** offline

Completion means another person can reproduce the evidence, understand the
limits, and evaluate the claim. A polished slide deck cannot compensate for a
leaky split, missing data contract, untested command, or hidden risk.

## Learning objectives

By the end of the lesson, you can:

- run the project from a clean environment using documented commands;
- present a final model against a baseline with uncertainty and error analysis;
- package code, data instructions, tests, and generated artifacts coherently;
- document security, privacy, fairness, and operational limitations; and
- deliver a concise narrative with an executable fallback demo.

## Prerequisites

- Complete `python-59` with all kickoff gates documented.
- Freeze the final evaluation protocol before the last model comparison.
- Keep enough time to rerun from clean state and repair documentation.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Release candidate | Exact code/config/artifacts proposed as final |
| Smoke test | Small end-to-end check of a critical path |
| Evidence chain | Trace from claim to metric, data, code, environment, and run |
| Error analysis | Structured study of failures, not only aggregate score |
| Model card | Intended use, data, evaluation, limitations, ethics, and operations |
| Demo fallback | Pre-recorded/screenshot evidence available if live infrastructure fails |
| Reproducibility | Ability to rebuild result under documented conditions |
| Replicability | Independent reimplementation reaches compatible conclusions |

## Final acceptance gates

| Gate | Pass evidence |
|---|---|
| Clean setup | Supported Python version, `pyproject.toml`, reviewed lock, and OS-specific setup commands |
| Data | Reproducible local loader or documented versioned snapshot; no private data committed |
| Quality | Schema/contract checks run before training |
| Model | Baseline and final candidate trained through the same valid protocol |
| Evaluation | Frozen holdout/backtest results, uncertainty, calibration/threshold as relevant, and error slices |
| Tests | Unit tests plus one end-to-end smoke path pass |
| Reproduction | Fresh clone/environment runs training and evaluation from explicit modules |
| Security/privacy | Secret scan, data classification, retention/access notes, trusted artifacts, abuse cases |
| Operations | Model/data version, monitoring signals, owners, rollback trigger and procedure |
| Honesty | Unsupported populations/uses, failure modes, and unresolved questions are prominent |

If a gate fails, label the capstone as a prototype and list the missing evidence.
Do not weaken the gate after seeing the result.

## Reproduction commands

Adapt module names to your project and run from its root.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m capstone.data
.\.venv\Scripts\python.exe -m capstone.train
.\.venv\Scripts\python.exe -m capstone.evaluate
```

macOS/Linux:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m pytest -q
.venv/bin/python -m capstone.data
.venv/bin/python -m capstone.train
.venv/bin/python -m capstone.evaluate
```

The repository may use `uv sync --locked` for the reviewed lock. Document one
canonical path, then test it without relying on a previously populated
environment.

## Presentation contract

Use roughly this story:

1. **Decision and stakes:** stakeholder, action, and constraints.

2. **Data:** row unit, source/license, quality, target timing, and exclusions.

3. **Evaluation:** split/backtest, baseline, primary metric, and guardrails.

4. **Result:** final versus baseline with variability—not only the best number.

5. **Error analysis:** representative false positives/negatives or residual
   segments, with privacy-safe examples.

6. **Operations and risk:** latency/resources, monitoring, security, fairness,
   rollback, and out-of-scope uses.

7. **Recommendation:** what should happen next and what evidence is still needed.

### Presentation quality criteria

- Every chart has a title, units, population, time scope, and readable labels.
- Every numeric claim points to a reproducible table/artifact.
- Baseline and final model use comparable data and metrics.
- Limitations receive presentation time rather than a footnote.
- The live demo has a tested health/smoke check and a static fallback.
- Questions about data lineage, leakage, failure cases, and cost have concise
  evidence-backed answers.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 60 learner notebook from this guide's **Next
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

## Concept deep dive — release evidence, cold-start reproducibility, presentation claims, and handoff

### The mental model

Capstone completion is a release review. The release candidate is one
exact code, configuration, environment, data identity, and artifact
set. A **cold-start reproduction** follows documented commands from a
clean environment and proves the critical path without hidden notebook
state.

A presentation is a chain of claims and evidence: decision, data,
baseline, evaluation design, result with uncertainty, error analysis,
limitations, and next action. A demo fallback keeps the evidence
available if live infrastructure fails. Operational handoff names
owners, monitoring, rollback, retention, and known gaps.

### Worked examples and syntax anatomy

- **release manifest:** pins code/data/environment/artifact identities and the commands used to verify them.
- **claim-to-evidence matrix:** maps each slide or conclusion to a metric, artifact, test, and limitation.
- **handoff/runbook:** defines normal operation, monitoring, failure response, rollback, ownership, and retention.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — reject unsupported presentation claims

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
claims = [
    {"claim": "candidate beats baseline", "evidence": "metrics.json", "limitation": "single local dataset"},
    {"claim": "service reloads artifact", "evidence": "smoke-test.txt", "limitation": "no load test"},
    {"claim": "works for every population", "evidence": None, "limitation": None},
]
unsupported = [
    item["claim"] for item in claims
    if not item["evidence"] or not item["limitation"]
]
print({"unsupported": unsupported})
assert unsupported == ["works for every population"]
```

**Expected observation:** A broad claim without both evidence and a scoped limitation is blocked from the final narrative.

**Assumption to name:** Evidence files are versioned, reproducible, and actually support the wording of their claims.

### Focused example B — turn release readiness into a failing checklist

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
release = {
    "clean_environment_run": True,
    "tests_passed": True,
    "data_identity_recorded": True,
    "artifact_hash_verified": True,
    "baseline_comparison_present": True,
    "limitations_present": True,
    "rollback_rehearsed": True,
    "owner_named": True,
}
missing = [name for name, passed in release.items() if not passed]
print({"ready": not missing, "missing": missing})
assert not missing
```

**Expected observation:** Readiness is the conjunction of reproducibility, quality, evidence, safety, and ownership—not slide completion.

**Assumption to name:** Every Boolean is backed by a dated command/output or reviewed artifact, not self-attestation.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define release evidence, cold-start reproducibility, presentation claims, and handoff in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Running from a warm notebook, showing only the best metric, or making live-demo success the only proof.

**Debug it deliberately:** Start from the documented first command in a clean environment; follow every generated file and claim back to its source, test, hash, and owner.

**Stop condition:** Do not call the capstone complete while a required gate is unknown, the release cannot be reproduced, or risk/rollback ownership is absent.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

The notebook's final checklist is the exercise:

1. Finalize the data and training/evaluation pipeline.

**Verify:** Practice 1 — release evidence, cold-start reproducibility, presentation claims, and handoff — from a clean checkout/environment, run the documented train and test commands with exit code 0; record dataset/split hashes, baseline and candidate metric files, passing tests, and the frozen selection rule before opening final-test labels.

2. Produce a results notebook and README with exact reproduction steps.

**Verify:** Practice 2 — release evidence, cold-start reproducibility, presentation claims, and handoff — have another person or clean shell execute every README command in order; require exit code 0 and compare produced metric/artifact hashes with the results notebook, documenting any intentionally nondeterministic field.

3. Save artifacts under an ignored `artifacts/` path and retain dependency
   metadata/lock.

**Verify:** Practice 3 — release evidence, cold-start reproducibility, presentation claims, and handoff — write artifacts only under ignored artifacts/, list relative path, SHA-256, size, model/data/split/code identity, Python and dependency-lock hash, then reload the primary artifact in a fresh process and match a fixed prediction.

4. Prepare presentation-ready visuals and the short story above.

**Verify:** Practice 4 — release evidence, cold-start reproducibility, presentation claims, and handoff — export every presentation visual with title, axes/units, population/window, support, and source metric; reconcile each plotted value with the results table and remove any claim not supported by the frozen evaluation.

5. Write three takeaways and one open question.

**Verify:** Practice 5 — release evidence, cold-start reproducibility, presentation claims, and handoff — write three takeaways that each cite a metric, comparison, and limitation, plus one open question with the data/experiment needed to answer it; rehearse the story in the declared time and keep a tested fallback demo.

### Progressive hints

1. Stop adding model families; rerun the frozen candidate from clean state.
2. Generate metrics/plots from the same evaluation module used by tests.
3. Ask a peer or Codex tutor to follow only the README; record every ambiguity.
4. Practice a five-minute version, then prepare deeper appendix evidence.

The reference solution adds a direct smoke-test and automation template. Use
portable direct Python commands as the canonical Windows path; Make is optional.

### Additional mastery practice

Finish with cold-start reproduction, evidence-backed claims, failure-tolerant demonstration, ownership, and honest limits. Completion means another person can rerun and assess the work.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

6. **Cold-start reproduction:** Clone/copy the project into a fresh temporary directory, follow only the README on Windows or POSIX, and log every ambiguity, manual step, network access, output, and elapsed stage.
   **Progressive hint:** Use a clean environment and no notebook state. Verify the documented offline path after the one connected bootstrap.

**Verify:** Cold-start reproduction — from a fresh temporary copy, execute the README on the documented Windows/POSIX path and retain command transcript, exit codes, elapsed stages, network accesses, outputs, and ambiguities; require the final tests and artifact reload to pass.

7. **Claim-to-evidence matrix:** Create a table mapping every headline claim to metric/visual, dataset and split, sample size, uncertainty, reproduction command, limitation, and owner.
   **Progressive hint:** Remove or soften claims with no direct evidence. Distinguish predictive association, operational estimate, and causal conclusion.

**Verify:** Claim-to-evidence matrix — for every headline claim, provide one row with exact metric/visual, dataset/split hash, sample size, uncertainty, reproduction command, limitation, and owner; remove claims whose command/result cannot be reconciled.

8. **Failure-tolerant demo:** Prepare and rehearse a five-minute demo with a preflight check, time budget, local fixtures, screenshots/static fallback, and recovery from one intentionally broken dependency or service.
   **Progressive hint:** The core result must not depend on live internet. Demonstrate the reproducible workflow, not a fragile sequence of manual notebook cells.

**Verify:** Failure-tolerant demo — record a timed five-minute rehearsal transcript: preflight passes, local fixture produces the expected result, one dependency is intentionally broken, the fallback is shown, recovery succeeds, and the time budget is met.

9. **Operational handoff:** Write an ownership and maintenance section covering artifact/data refresh, dependency updates, monitoring, incident contact, rollback, known limitations, and end-of-life criteria.
   **Progressive hint:** Name roles and cadences, not personal credentials. Connect each maintenance action to a test or acceptance gate.

**Verify:** Operational handoff — name role/owner, cadence, command, expected result, escalation route, and rollback/end-of-life trigger for artifact/data refresh, dependencies, monitoring, and incidents; have a second person walk one maintenance scenario.

10. **Retrospective and next experiment:** Write a retrospective with what changed your belief, strongest and weakest evidence, one discarded path, remaining risk, and one bounded next experiment with a predeclared decision rule.
   **Progressive hint:** The next experiment should resolve the highest-value uncertainty, not simply try a more complex model.

**Verify:** Retrospective and next experiment — write the strongest/weakest evidence with cited metrics, one discarded path and remaining risk; define the next experiment's population, intervention/input, metric, sample/budget, stop rule, and result that would reverse the current decision.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Can a new machine reproduce the main metric without your shell history?
- Can each slide claim be traced to a checked artifact and exact run?
- Are thresholds and feature transformations inside the validated pipeline?
- Are private data, secrets, caches, model downloads, and large artifacts handled
  according to the documented policy?
- Could an operator identify the version and roll it back?
- Can you explain one serious limitation without minimizing it?

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Response |
|---|---|---|
| “Works on my machine” | Hidden environment/data state | Test a clean supported environment |
| Last-minute model selection on holdout | Final metric is optimistic | Freeze candidate; disclose if boundary was compromised |
| Notebook is the only implementation | Hidden state/order | Put repeatable logic in importable modules |
| Huge artifact committed | Repo becomes unusable | Store ignored/generated artifacts with rebuild instructions |
| Demo needs Internet | Offline presentation can fail | Cache intentionally and prepare local fallback |
| Risks omitted for a clean story | Audience cannot assess suitability | Present limits and controls alongside result |

Shipping a prototype, an analysis, and a production service require different
evidence. State which one you built.

## Next step

- Finish in the [Day 60 learner notebook](../notebooks/day60_capstone_completion_presentation.ipynb).
- Compare your evidence with the
  [Day 60 solution](../solutions/day60_capstone_completion_presentation/day60_solutions.md).
- There is no Day 61 in this track. Continue with the
  [Python + PostgreSQL engineering bridge](../../../bridge/README.md) or revisit
  weak areas identified by the capstone review.

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-60` — Day 60 — Capstone Completion and Presentation.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize release evidence, cold-start reproducibility, presentation claims, and handoff. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day60_capstone_completion_presentation.md`
- learner artifact: `python/ds-60day/notebooks/day60_capstone_completion_presentation.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-59`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
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
