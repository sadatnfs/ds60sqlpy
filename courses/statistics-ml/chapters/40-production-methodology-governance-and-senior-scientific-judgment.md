# 40. Production Methodology, Governance, and Senior Scientific Judgment

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-040`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Production methodology is the discipline of preserving the meaning of a result as it moves from a notebook into repeated decisions. A model artifact alone is not a system. Data availability, feature computation, evaluation, thresholds, human review and rollback determine what happens when the model is used. Senior judgment means knowing which claim the evidence supports, which uncertainty matters to the decision and who is accountable for acting.

### Reconstruct the decision-time information set

Point-in-time correctness distinguishes when an event occurred from when its information became available. A record dated Monday but ingested Wednesday cannot be used in a Tuesday prediction unless it was genuinely known then. Historical tables often contain later corrections, backfilled outcomes and final status fields. A random train/test split cannot repair features that already contain future information.

Training-serving consistency requires the same feature semantics, not merely the same column names. Time zones, missing-value defaults, category vocabularies, aggregation windows and entity joins must agree. Preserve transformation code or a tested shared specification, then compare actual training and serving examples. A feature named average_latency can mean different windows or populations in two systems while passing a schema check.

### Version the complete evidence chain

A reproducible result connects data snapshot, code, configuration, environment, fitted model and evaluation artifacts. Content hashes detect changes in bytes, while semantic contracts explain what those bytes mean. A model version should also identify its preprocessing and calibration state. For a language assistant, include base model, tokenizer, adapter, prompt, tool policy, retrieval index and source-document versions. Updating a knowledge index can change behavior without changing model weights.

A replay should answer: which inputs were available, which transformation ran, which model and threshold produced the action, and which evidence supported the accompanying explanation? Keep sensitive data and credentials out of public artifacts, but preserve an authorized route to the necessary audit evidence. Logging everything indefinitely is not a substitute for a deliberate privacy and retention design.

### Monitor usefulness, not only distribution change

Input drift is a change in observed features. Performance drift is a change in predictive or decision quality. They are related but not equivalent: a harmless seasonal mix shift can trigger a distribution alarm, while an unchanged feature distribution can accompany a changed outcome relationship. Labels may arrive weeks later, so monitor data quality, prediction distributions and mature outcome cohorts separately. Do not compare incomplete recent labels with fully matured historical labels as if they had equal follow-up.

Calibration asks whether predicted probabilities retain their meaning. Decision thresholds convert them into actions based on cost and constraints. If false-positive cost is C_FP and false-negative cost is C_FN in a simple binary setting, acting positive minimizes expected classification cost when \(p>\frac{C_{\mathrm{FP}}}{C_{\mathrm{FP}}+C_{\mathrm{FN}}}\). That formula assumes calibrated p, the specified cost structure and no other capacity or fairness constraints. The highest-AUC model is not automatically the best deployed decision policy.

### Release with observable boundaries

Shadow deployment observes candidate behavior without using its output for live decisions. A canary exposes a limited operational scope under explicit gates. Champion-challenger comparisons need matched tasks and appropriate assignment to separate model changes from population changes. Define rollback triggers, the known-good artifact and compatibility requirements before release. A rollback that restores weights but keeps incompatible features or a changed retrieval corpus may not restore prior behavior.

Human review should be designed as part of the system. Specify what reviewers see, which decisions they can override, how uncertainty is communicated and how review quality is measured. Escalation can reduce harm when the system recognizes insufficient evidence, but it also creates workload and selection effects. If only difficult cases receive labels, later training data become policy-selected and require careful interpretation.

### Apply the same rigor to LLM-assisted data science

For extraction, retain original passages and schema-level validation alongside model output. For a subject-matter assistant, enforce document access before retrieval and attach claims to permitted versioned evidence. For code generation, run reviewed code in the approved environment and compare outputs with tests or independent calculations. A language model's explanation of a result is a draft until its numbers and assumptions match the executed evidence.

Fine-tuning and RAG introduce different change surfaces. An adapter can change response behavior across many tasks; a retrieval update can change factual context, freshness and access. Evaluate both with held-out task families and failure cases, including unsupported questions, conflicting sources and prompt injection in retrieved material. Operational acceptance should consider correct abstention, citation support, tool behavior, latency, cost and human correction burden. A preference score or fluent report is only one measurement.

### Communicate a bounded conclusion

A useful scientific handoff states the decision, estimand, data coverage, method, assumptions, results, uncertainty and next action. Separate observed facts from model estimates and hypotheses. Explain what would change the recommendation and which new evidence is worth collecting. Choosing a simpler adequate method is often a strength when it makes these boundaries clearer. Scope control is part of competence: when the data cannot identify a causal effect or support a rare subgroup claim, the correct deliverable is a narrower conclusion and a concrete evidence plan.

## Methods, mechanisms, and limits

### stat-40-01

**Point-in-time correctness**

Point-in-time correctness restricts features to information available at the prediction timestamp. Both event time and availability time matter, including delayed ingestion and later corrections. Build as-of joins or immutable snapshots rather than using final-state tables indiscriminately. Validate with explicit counterexamples where a historically dated record arrives later, because a conventional train/test split can leave this leakage untouched.

### stat-40-02

**Training–serving consistency**

Training-serving consistency aligns feature definitions, transformations, missingness and model inputs across development and operation. A shared schema alone does not establish semantic parity. Compare representative raw-to-feature examples and version the preprocessing pipeline. Monitor differences in units, category vocabularies and time windows, especially when independent teams implement the same feature name.

### stat-40-03

**Data contracts**

Data contracts define schema, units, meanings, allowed values, freshness and update behavior at an interface. They should specify what happens when a requirement fails, such as quarantine, bounded fallback or stopping publication. A contract is stronger when checked at the boundary with meaningful diagnostics. Overly permissive coercion can preserve a successful job status while changing the analytical meaning.

### stat-40-04

**Dataset versioning**

Dataset versioning preserves the exact input snapshot or a reproducible reference to it, including relevant source versions and extraction logic. A filename with a date is not sufficient if contents can be overwritten. Hashes establish byte identity but not completeness or correctness. Record inclusion criteria, event/availability cutoffs and quality checks alongside the snapshot identity.

### stat-40-05

**Model versioning**

Model versioning records fitted parameters together with code, data, preprocessing, hyperparameters and evaluation. For adapted language models, retain the compatible base and adapter identities rather than only an adapter filename. A model artifact without its feature or tokenizer contract may not be usable. Distinguish candidate, approved and deployed versions with observed deployment evidence.

### stat-40-06

**Reproducible pipelines**

Reproducible pipelines make transformations and dependencies explicit so a result can be rerun from controlled inputs. Deterministic stages simplify comparison, while stochastic stages need recorded randomness and tolerance-aware checks. Rerunning should preserve learner or operational state unless replacement is intentional. Reproducibility does not prove statistical validity, so include tests for data leakage and estimand alignment as well as execution.

### stat-40-07

**Data drift monitoring**

Data drift monitoring detects changes in feature distributions, missingness, categories or joint structure. Statistical significance can become trivial at large scale, so include effect size and operational relevance. Drift may be harmless or expected, and no drift does not guarantee stable outcome relationships. Compare against an appropriate seasonal or segment reference and route alerts to a concrete investigation.

### stat-40-08

**Performance monitoring**

Performance monitoring tracks predictive or decision usefulness using outcomes that have matured enough to evaluate. Aggregate metrics can hide subgroup deterioration and policy-driven label selection. Match the monitored horizon and population to development evaluation. When labels are delayed or selectively observed, report those limitations instead of interpreting available-label performance as representative of every decision.

### stat-40-09

**Calibration monitoring**

Calibration monitoring checks whether probability predictions correspond to observed frequencies in the relevant deployment population. Reliability plots, calibration error summaries and proper scores reveal different aspects. Binning and sample size affect interpretation, particularly in rare-event tails. Recalibration can repair probability scale without changing rank, but it still requires representative recent labels and an independent acceptance check.

### stat-40-10

**Label-delay handling**

Label-delay handling accounts for outcomes that become known after a prediction or action. Recent cohorts may be incomplete or censored, and backfilled labels can revise earlier metrics. Define maturity windows and availability timestamps. Treating unknown recent outcomes as negatives can create artificial performance changes and biased retraining data.

### stat-40-11

**Retraining policies**

Retraining policies define triggers, data windows, validation gates and deployment authority for model updates. A calendar schedule is one policy, not proof that retraining helps. Drift or performance alarms should lead to diagnosis before automatic replacement. Compare the candidate with the incumbent on appropriate held-out data and preserve rollback artifacts, because newly collected labels may reflect a changed or biased policy.

### stat-40-12

**Shadow deployment**

Shadow deployment runs a candidate on real inputs while withholding its outputs from live decisions. It reveals latency, feature availability and prediction differences without measuring the full causal effect of using the candidate. Human or downstream behavior still follows the incumbent. Log shadow failures and compare mature outcomes, but do not claim an online treatment effect from shadow operation alone.

### stat-40-13

**Canary deployment**

Canary deployment exposes a limited fraction or scope to a candidate under explicit monitoring and rollback rules. It limits exposure but can produce small or unrepresentative samples. Randomization or careful design is needed for a fair performance comparison. Define which failures trigger immediate rollback and which require more evidence, and keep feature/data compatibility in the recovery plan.

### stat-40-14

**Champion–challenger evaluation**

Champion-challenger evaluation compares the incumbent with one or more candidate systems under matched data and decision conditions. Repeatedly selecting challengers on the same holdout can overfit evaluation. Pair cases where possible and distinguish offline replay from live policy effects. Include operational cost, latency and critical regressions so a small average metric gain does not conceal a worse system.

### stat-40-15

**Rollback criteria**

Rollback criteria specify observable conditions that justify reverting a release, plus the exact known-good artifacts and state compatibility needed. Restoring model weights alone may be insufficient if features, schemas or retrieval documents changed. Rehearse recovery in an appropriate owned environment and record its actual duration. A written rollback plan is not evidence that restoration succeeds.

### stat-40-16

**Human-in-the-loop systems**

Human-in-the-loop systems assign people specific roles in review, correction, escalation or final decisions. The interface, time budget and information shown affect reviewer quality. Human approval is not automatically an independent check if reviewers simply accept confident model text. Measure disagreement, overrides and missed errors, and account for how reviewed cases become a selected training/evaluation sample.

### stat-40-17

**Feedback-loop management**

Feedback-loop management recognizes that deployed decisions change exposure, labels and future populations. A fraud filter hides outcomes for blocked transactions; a recommender changes which items receive feedback. Naively retraining on resulting data can reinforce the existing policy. Use appropriate exploration, logging or causal methods, and keep the target population separate from the conveniently observed subset.

### stat-40-18

**Model risk management**

Model risk management examines the consequences of failures and the controls that reduce their likelihood or impact. Risk depends on use, scale, reversibility and human oversight, not only model complexity. Identify critical assumptions, failure scenarios and accountable owners. A generic checklist cannot replace testing the specific pathways through which this system can produce a harmful or misleading decision.

### stat-40-19

**Model documentation**

Model documentation records purpose, intended population, data, assumptions, evaluation, limitations and operating boundaries. For an LLM workflow, document prompts, tools, retrieval sources and adaptation alongside weights. Keep measured results distinct from aspirational capabilities. Documentation should support a concrete reviewer decision, including what the model must not be assumed to establish.

### stat-40-20

**Independent validation**

Independent validation uses reviewers or procedures separate from model development to challenge design and evidence. Independence improves the chance of finding shared assumptions or selection bias, but reviewers need relevant domain and technical access. Reproduce key claims, test plausible failure cases and inspect the complete data/evaluation pipeline. Approval without substantive challenge is not validation evidence.

### stat-40-21

**Auditability**

Auditability preserves enough authorized evidence to reconstruct how a result or decision was produced. Stable identifiers, timestamps, versions and bounded logs connect inputs to outputs and actions. Protect sensitive data and avoid recording credentials. An audit trail should show observed tool results and actual actions, not only a model-generated explanation after the fact.

### stat-40-22

**Decision thresholds and escalation rules**

Decision thresholds and escalation rules translate model scores into actions with explicit costs, capacity and authority. A threshold optimized for one prevalence or cost ratio may fail after deployment changes. Escalation should name the uncertainty or contract violation that triggers review. Test boundary values and include abstention as a measured outcome rather than treating every non-action as a model failure.

### stat-40-23

**Cost of false confidence**

The cost of false confidence is the loss from acting as if uncertain evidence were decisive. It can exceed the cost of a modestly less precise but honest estimate, especially when decisions are difficult to reverse. Communicate uncertainty in terms of plausible outcomes and decision sensitivity. A narrow model interval does not cover unmodeled bias, leakage or a wrong causal identification argument.

### stat-40-24

**Scope control**

Scope control limits claims to what the design, data and validation can support. A descriptive association should not become a causal recommendation through stronger wording, and a toy model run should not become a production-readiness claim. State unresolved questions and useful next evidence. Narrowing an unsupported claim is a substantive analytical result, not a failure to provide an answer.

### stat-40-25

**Method selection**

Method selection chooses the simplest adequate approach given the estimand, data structure, assumptions, constraints and stakes. Complexity is justified when it addresses a demonstrated limitation and improves relevant validation. A transparent baseline provides a comparison and helps diagnosis. Reuse familiar methods only when their assumptions fit; convenience does not override dependence, censoring or selection mechanisms.

### stat-40-26

**Scientific communication**

Scientific communication connects the question, evidence and decision in language suited to the audience. State what was observed, estimated and assumed, with units and uncertainty. Explain material limitations near the claim they qualify. A language model can draft wording, but the analyst remains responsible for verifying numerical statements and preventing a confident narrative from exceeding the study design.

### stat-40-27

**Technical review**

Technical review challenges identification, temporal leakage, dependence, validation, numerical implementation and interpretation. Reviewers should inspect a few decisive artifacts deeply rather than only a polished summary. Ask which plausible wrong approach the tests reject and which assumptions remain untested. Record actionable findings with evidence and distinguish defects from optional improvements.

### stat-40-28

**Research prioritization**

Research prioritization allocates effort toward uncertainties that can change an important decision. More precise estimation of an irrelevant quantity has low value. Consider expected impact, feasibility, reversibility and the cost of delay. A small targeted data-quality investigation can be more valuable than a complex model if the central uncertainty is whether the labels mean what the team thinks.

### stat-40-29

**Experiment prioritization**

Experiment prioritization compares potential studies by expected information and decision value, balanced against cost, time and operational constraints. Statistical power is one consideration, but the effect size worth acting on and the available intervention matter. Avoid prioritizing only easy-to-measure outcomes. A study should be designed to resolve a specific decision uncertainty with a clear interpretation of positive, negative and inconclusive results.

### stat-40-30

**Decision ownership**

Decision ownership identifies who may act on the analysis, who accepts residual uncertainty and who responds when conditions change. Analytical recommendations do not automatically authorize external actions. For automated systems, encode the action boundary and escalation owner explicitly. A reproducible model output is evidence for a decision; responsibility for the consequences remains an organizational and operational commitment.

## Worked Python demonstrations

Complete offline program: [chapter_40.py](../examples/chapter_40.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_40.py
```

### Reject a historical record that arrived too late

At origin three, values ten and thirty are available. The record with event time two has availability time four and must be excluded. A query using only event_time<=3 would leak value twenty. The explicit dual-time predicate makes the information boundary testable.

### Version the policy as well as the model

A canonical JSON configuration includes the model, feature names and decision threshold. Changing threshold 0.2 to 0.3 changes its SHA-256 digest even though the model name stays fixed. The hash proves byte identity of this configuration, while the surrounding contract must still explain its meaning and data provenance.

### Derive an action from costs

With false-positive cost two and false-negative cost eight, the simple optimal threshold is \(\frac{2}{2+8}=0.2\). Probabilities [0.1,0.4,0.8] imply actions [false,true,true]. The program separately computes expected positive and negative costs and verifies the same decision, making the threshold derivation inspectable.

### Separate extraction validity from analytical truth

A synthetic JSON extraction passes an exact-key and allowed-category check and retains an evidence string. That establishes only schema validity, not whether the category is correct. Separately, four failures among ten events give 0.4, so an assistant draft claiming 0.9 is rejected. Semantic extraction review and code-verified aggregation remain distinct checks.

### Complete executable example

```python
import hashlib
import json
import numpy as np


def point_in_time():
    rows = [
        {"event": 1, "available": 1, "value": 10},
        {"event": 2, "available": 4, "value": 20},
        {"event": 3, "available": 3, "value": 30},
    ]
    origin = 3
    visible = [row for row in rows if row["event"] <= origin and row["available"] <= origin]
    assert [row["value"] for row in visible] == [10, 30]
    print("Available values at origin 3:", [row["value"] for row in visible])


def version_identity():
    config = {"model": "tiny-v1", "threshold": 0.2, "features": ["age", "count"]}
    encoded = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(encoded).hexdigest()
    changed = dict(config, threshold=0.3)
    other = hashlib.sha256(
        json.dumps(changed, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert digest != other and len(digest) == 64
    print("Configuration identity changes with threshold:", digest[:12], other[:12])


def decision_costs():
    p = np.array([0.1, 0.4, 0.8])
    false_positive = 2.0
    false_negative = 8.0
    threshold = false_positive / (false_positive + false_negative)
    act = p > threshold
    positive_cost = (1 - p) * false_positive
    negative_cost = p * false_negative
    assert threshold == 0.2 and act.tolist() == [False, True, True]
    assert np.array_equal(act, positive_cost < negative_cost)
    print("Threshold and actions:", threshold, act)


def checked_extraction_and_claim():
    raw = '{"case_id":"c1","category":"delay","evidence":"shipment arrived late"}'
    record = json.loads(raw)
    assert set(record) == {"case_id", "category", "evidence"}
    assert record["category"] in {"delay", "damage", "other"} and record["evidence"]
    events = 10
    failures = 4
    computed = failures / events
    draft_claim = 0.9
    assert computed == 0.4 and not np.isclose(draft_claim, computed)
    print("Schema-valid extraction:", record, "verified failure fraction:", computed)


def main():
    point_in_time()
    version_identity()
    decision_costs()
    checked_extraction_and_claim()


if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: What is the most dangerous kind of leakage to inspect first?** Information that would not exist at decision time, including delayed labels, backfilled status and post-event aggregates. Verify availability semantics before relying on a random or chronological split, because both can preserve already-leaked features.

**Interview: When should drift trigger retraining?** After diagnosing whether it changes task performance, calibration or the meaning of inputs and labels. A shift can be harmless, while a performance problem can occur without visible feature drift. Candidate retraining still needs independent acceptance and a rollback path.

**Interview: What changes when the deployed model is a RAG assistant?** The system version includes corpus/index, access rules, retrieval/ranking, prompt, base/adapted model and tool behavior. Evaluate supported answers and actual actions across that full chain. Restoring weights alone may not restore previous behavior.

**Interview: What makes a senior analytical recommendation useful?** It ties a decision to a supported estimand, checked evidence and explicit assumptions; explains uncertainty and consequences; names what would change the conclusion; and identifies who may act. Strong wording cannot compensate for a weak identification or validation design.

## Primary sources and official APIs

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

- [Liang and colleagues, holistic language-model evaluation](https://arxiv.org/abs/2211.09110)

- [Sculley and colleagues, Hidden Technical Debt in Machine Learning Systems](https://proceedings.neurips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems)

## Apply the assistant evidence contract

The [grounded claims and abstention guide](../../llm-applied/guides/llm-applied-011.md) and [retrieval/answer evaluation guide](../../llm-applied/guides/llm-applied-012.md) make key operational boundaries concrete. Record the actual source, model, prompt and evaluation versions before accepting a changed assistant, and preserve the difference between an authorized action, a generated proposal and a completed operation.

## Reading connections

[Previous chapter](39-research-synthesis-and-specialized-statistical-methodologies.md) | [Book contents](../README.md)
