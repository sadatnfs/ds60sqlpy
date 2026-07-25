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

## Learner exercises

1. Write the problem statement and success metric in the notebook.
2. Create the project skeleton.
3. Build a baseline and record metrics.

### Progressive hints

1. Start with the decision and cost of errors; select the metric afterward.
2. Add `README`, `pyproject.toml`, `src`, `tests`, and ignored `artifacts` before
   adding more notebooks.
3. Use the simplest credible model/rule and frozen split. Save metrics as a
   small machine-readable artifact and explain them in prose.

The reference solution includes example warehouse/API source text as a planning
template. Those are placeholders, not course dependencies; your default
capstone must remain reproducible offline.

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
