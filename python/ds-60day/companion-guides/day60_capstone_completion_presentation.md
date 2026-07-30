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

## Learner exercises and progressive hints

The notebook's final checklist is the exercise:

1. Finalize the data and training/evaluation pipeline.
2. Produce a results notebook and README with exact reproduction steps.
3. Save artifacts under an ignored `artifacts/` path and retain dependency
   metadata/lock.
4. Prepare presentation-ready visuals and the short story above.
5. Write three takeaways and one open question.

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
7. **Claim-to-evidence matrix:** Create a table mapping every headline claim to metric/visual, dataset and split, sample size, uncertainty, reproduction command, limitation, and owner.
   **Progressive hint:** Remove or soften claims with no direct evidence. Distinguish predictive association, operational estimate, and causal conclusion.
8. **Failure-tolerant demo:** Prepare and rehearse a five-minute demo with a preflight check, time budget, local fixtures, screenshots/static fallback, and recovery from one intentionally broken dependency or service.
   **Progressive hint:** The core result must not depend on live internet. Demonstrate the reproducible workflow, not a fragile sequence of manual notebook cells.
9. **Operational handoff:** Write an ownership and maintenance section covering artifact/data refresh, dependency updates, monitoring, incident contact, rollback, known limitations, and end-of-life criteria.
   **Progressive hint:** Name roles and cadences, not personal credentials. Connect each maintenance action to a test or acceptance gate.
10. **Retrospective and next experiment:** Write a retrospective with what changed your belief, strongest and weakest evidence, one discarded path, remaining risk, and one bounded next experiment with a predeclared decision rule.
   **Progressive hint:** The next experiment should resolve the highest-value uncertainty, not simply try a more complex model.

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
