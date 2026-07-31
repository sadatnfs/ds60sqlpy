# Day 59 — Solutions: Capstone Kickoff

We provide concrete templates and examples for scope, metrics, data access, baseline, risks, and milestones.

Contents
- Exercise 1: Problem statement and hypotheses
- Exercise 2: Data sources and access plan
- Exercise 3: Baseline metric, risks, milestones

---

Worked reference for Exercise 1 — Problem and hypotheses (template)
```markdown
# Problem Statement
We aim to predict <target> for <users/stakeholders> to achieve <business value>.

## Hypotheses
- H1: Feature A (e.g., last_login) is predictive of churn.
- H2: Text sentiment from tickets correlates with upsell.
- H3: Seasonality drives demand; including holidays improves forecast.

## Success Metrics
- Primary: AUC ≥ 0.80 on holdout within ±2% over 4 weeks
- Secondary: Calibration error ≤ 0.02, latency ≤ 50ms P95
```

Worked reference for Exercise 2 — Data sources and contracts
```markdown
## Sources
- Warehouse table analytics.users_daily (owner: data-eng)
- CRM API /tickets (owner: ops)

## Contracts
- Schema, freshness (daily by 02:00 UTC), null rate < 1%
- Access: request via JIRA SEC‑123; principle of least privilege
```

Worked reference for Exercise 3 — Baseline, risks, milestones
```markdown
## Baseline
- Heuristic: last_30d_activity>0 → non‑churner; baseline AUC ≈ 0.62

## Risks
- Data leakage from future‑derived features
- Nonstationarity; quarterly product changes
- PII handling for GDPR/CCPA

## Milestones
- Week 1: Data audit + baseline
- Week 2: Feature engineering + model v1
- Week 3: Evaluation + error analysis
- Week 4: Packaging + demo + report
```

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **decision statement:** names stakeholder, action, prediction time, and consequence before selecting a model.
2. **acceptance matrix:** connects each success/guardrail threshold to data, metric, owner, and verification command.
3. **milestone checkpoint:** produces a reviewable artifact and explicit continue/pivot/stop decision.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** A falsifiable charter and staged evidence plan reduce wasted modeling and make risk/acceptance decisions reviewable.

**Useful alternative:** A descriptive analysis, rule, data-quality fix, or no model may better serve the stakeholder than predictive ML.

**Trade-off:** Broader scope may be more impressive but weakens depth, reproducibility, and completion probability.

**Edge case to test:** License restrictions, unrepresentative samples, target leakage, tiny key slices, unavailable labels, and irreproducible external data can invalidate the plan.

**Evidence of correctness:** Get stakeholder sign-off on charter/thresholds, validate a local data sample and license, reproduce the target, run the baseline, and record continue/pivot/stop at each milestone.

When comparing your attempt with the reference, explain which of these
decisions your code made explicitly. If the reference makes a different
choice, compare the contracts and evidence before deciding that one
version is universally better.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Write the problem statement and success metric in the notebook.

**How to reason about it:** Define stakeholder decision, prediction unit/time, target, error costs, success metric, minimum practical improvement, and excluded uses before choosing model families.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1 — capstone scope, decision framing, data contracts, and early stop rules — write a decision, population, prediction/analysis unit, target, primary metric formula, baseline, success threshold, guardrail, and out-of-scope list; include an owner and stop condition for each threshold.

### Exercise 2 — Original lesson practice

**Prompt:** Create the project skeleton.

**How to reason about it:** Create the skeleton and ignored artifact/data locations before exploratory sprawl. The README and pyproject are active contracts, not end-of-project cleanup.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2 — capstone scope, decision framing, data contracts, and early stop rules — create the declared src/tests/notebooks/data-or-config layout plus README and ignored local artifact paths; print a tree and run one smoke import/test from a clean process with exit code 0.

### Exercise 3 — Original lesson practice

**Prompt:** Build a baseline and record metrics.

**How to reason about it:** Use the simplest credible frozen-split baseline, save machine-readable metrics, and explain them. Optional tracking must not make offline completion dependent on a server.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 3 — capstone scope, decision framing, data contracts, and early stop rules — save a baseline metric file containing dataset/split hash, seed, model parameters, metric value, denominator/support, and timestamp; reload it and reproduce the metric on the same frozen split.

### Exercise 4 — Scope and stop rules

**Prompt:** Write must-have, should-have, and out-of-scope lists plus kill criteria for unavailable data, inadequate support, unacceptable harm, or missed minimum baseline value.

**Reasoning before implementation:** Time-box discovery and name the evidence that triggers pivot, pause, or stop. Do not make deployment the default capstone requirement.

The contract should fit the remaining course time on a clean laptop. Kill
criteria protect against manufacturing a result when data rights, target
quality, group support, or practical value are inadequate.

Record the decision and date in a log. A well-supported “do not deploy” or
“collect better labels” conclusion is a successful analytical outcome.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Scope and stop rules — deliver must/should/out-of-scope and kill-criteria tables with owner, measurement command, threshold, review date, and observed status for data availability, support, harm, and baseline value.

### Exercise 5 — Capstone data contract

**Prompt:** Create a versioned schema and quality report for your chosen local dataset, including source/license, row unit, target, types, ranges, missingness, duplicates, split keys, and fingerprint.

**Reasoning before implementation:** Use a tiny valid fixture and deliberately invalid fixture to test the validator.

Validation should run before EDA/modeling and produce actionable failures.
Document first-run network/cache behavior if using an allowed Seaborn dataset;
otherwise prefer packaged/generated data for a fully offline path.

Preserve raw inputs and transform into ignored artifacts. Never commit a
credential, restricted dataset, or developer-specific absolute path.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Capstone data contract — validate the versioned schema against the local snapshot and print source/license, row unit/count, target, types/ranges, missing/duplicate counts, split-key overlap, and SHA-256; reject one tampered fixture.

### Exercise 6 — Decision log

**Prompt:** Record at least five project decisions with date, question, alternatives, evidence, chosen action, consequences, and revisit trigger.

**Reasoning before implementation:** Include split/metric/baseline choices, not only model hyperparameters. Link each result to a reproducible command or notebook cell.

The log prevents hindsight from turning exploration into a falsely linear
story. It also lets a reviewer distinguish a predeclared acceptance rule from
one chosen after results.

Keep rejected alternatives and why they were rejected. A revisit trigger such
as new labels, changed prevalence, or a failed slice metric makes the decision
operational rather than permanent dogma.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Decision log — record at least five uniquely dated decisions with question, alternatives, evidence link/metric, chosen action, consequence, owner, and revisit trigger; cross-link each active decision from the experiment log or README.
