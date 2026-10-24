# 34. Generative AI and Language-Model Evaluation

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-034`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Evaluating a language-model system means measuring whether a specified workflow produces useful, supported results under the conditions where it will be used. The unit is often a task, document family or user interaction rather than an isolated sentence. A benchmark score is meaningful only with the sampled population, information available to the system, rubric, evaluator and uncertainty attached.

### Build a task contract before choosing a metric

For structured extraction, define fields, allowed values, missingness, evidence spans and the cost of each error. For classification, define label boundaries and ambiguous cases rather than assuming a model-generated category is ground truth. For a subject-matter assistant, distinguish answerability, factual correctness, support from permitted documents, citation quality, appropriate abstention and usefulness. For statistical assistance, require executed code and a defensible analysis design behind numerical or causal claims.

A useful evaluation case contains a stable ID, the user task, the permitted evidence snapshot, expected constraints and a scoring rationale. Some tasks admit exact answers or executable tests. Others need an expert rubric or multiple valid references. Include negative cases with missing evidence, contradictory sources, irrelevant retrieval and plausible but unsupported claims. A system that answers every case fluently should fail when abstention is the correct behavior.

### Separate component diagnosis from end-to-end acceptance

A RAG pipeline can fail because the required passage was absent from the corpus, retrieval missed it, reranking discarded it, context construction truncated it or generation misused it. Evaluate retrieval recall and ranking separately from answer support. An oracle-context experiment gives the generator the right evidence to isolate its capability; a retrieved-context experiment tests the real pipeline. Passing with oracle evidence does not establish operational retrieval quality.

Likewise, a fine-tuned model may improve schema validity while degrading factuality or increasing unsupported confidence. Compare the base and adapted system on the same held-out case families, including prior capabilities and known refusal/abstention boundaries. Record tokenizer, base-model identity, adapter identity, prompt template, retrieval index version and decoding configuration. Otherwise an apparent improvement may be caused by an unrecorded change elsewhere in the workflow.

### Human judgment is an experiment

Write a rubric with observable criteria and examples of borderline cases. Sample tasks from the intended population, blind system identity, randomize response order and allow ties when the distinction is not meaningful. Use raters with relevant expertise for domain correctness. Collect independent first judgments before adjudication so disagreement can be measured rather than erased. A consensus label after discussion is useful, but it is not the same data as the original agreement rate.

Pairwise comparisons can reduce scale-use differences between raters, but presentation effects remain. Longer answers may appear more thorough even when they add unsupported claims. Reverse the order of the same pair and test whether preferences change. An automated judge is another model whose reliability must be validated on representative human-scored cases, especially failure cases where fluent wrong answers are tempting. A judge's explanation is evidence about its scoring behavior, not proof of its correctness.

### Use the right uncertainty unit

Repeated generations of one prompt reveal run-to-run variability, while many prompts from one document may still share the same underlying difficulty. Treating every token or paraphrase as an independent trial can make intervals implausibly narrow. Preserve case families and use paired comparisons or clustered resampling at the appropriate unit. Report uncertainty for rare but serious failures, and avoid concluding that a zero observed failure count proves zero risk.

For independent Bernoulli cases, a success fraction estimates a population success probability under the sample design. A Wilson interval offers a finite-sample alternative to the naive normal interval, particularly near zero or one. When cases are dependent, the binomial calculation is an illustrative lower-level model rather than a justified final interval. The scripts below show the arithmetic and explicitly state its assumptions.

### Evaluate utility, cost and failure handling together

Task success should be linked to a useful action: correctly populated analytical fields, a cited answer that resolves a question, or checked code that reproduces a requested result. Measure latency distributions, token or compute use, retrieval cost, human-review time and escalation frequency. A model can reduce generation cost while increasing expert correction effort. Compare Pareto-efficient alternatives rather than collapsing all tradeoffs into an unexplained weighted score.

The final acceptance packet should make a result reconstructable: case version, evidence snapshot, system configuration, raw output, scores, evaluator version and adjudication notes. Keep development cases separate from final acceptance, and rerun meaningful regression cases after changing prompts, retrieval or weights. The dedicated applied LLM route provides complete local examples of these boundaries; this chapter explains why their measurements support only the claims they actually test.

## Methods, mechanisms, and limits

### stat-34-01

**Task-specific evaluation**

Task-specific evaluation measures the actual success contract, such as exact extracted fields, executable code behavior or correctly supported answers. Decompose success into observable criteria without losing the end-to-end outcome. A summary can be fluent yet omit a required exception, and valid JSON can contain wrong values. Weight errors according to the decision only after reporting the underlying counts so a composite score cannot hide a critical failure.

### stat-34-02

**Reference-based evaluation**

Reference-based evaluation compares output with accepted answers, evidence spans or executable expected behavior. Multiple valid phrasings and incomplete references make exact text match too restrictive for many tasks. Semantic similarity can help but may reward a contradiction sharing the same vocabulary. Use field-level or claim-level checks when possible, and preserve expert rationale for references rather than treating one generated answer as unquestionable truth.

### stat-34-03

**Reference-free evaluation**

Reference-free evaluation assesses properties such as consistency, support from supplied evidence or rubric adherence without a fixed target answer. It is useful when many answers are acceptable or labels are expensive. The absence of a reference does not remove the need to validate the evaluator. A model judge may systematically accept plausible unsupported text, so compare its scores with independent human or executable checks on representative failures.

### stat-34-04

**Human evaluation design**

Human evaluation design specifies the task sample, rater population, rubric, blinding, assignment and analysis unit. Domain experts may be needed for technical correctness, while intended users can judge usefulness. Randomize order and balance workload to reduce fatigue and learning effects. Preserve individual ratings before adjudication and report uncertainty across tasks and raters instead of presenting one average as universally representative.

### stat-34-05

**Pairwise preference testing**

Pairwise preference testing asks which of two outputs better satisfies a rubric, often allowing ties. It reduces some problems with absolute rating scales but introduces order and comparison-context effects. Use the same tasks for both systems and randomize which response is shown first. Preference is an outcome about the rubric and rater population, not necessarily factual correctness unless the comparison explicitly checks it.

### stat-34-06

**Bradley–Terry models**

The Bradley-Terry model assigns a latent strength s_i to each system and models \(\Pr(i\text{ beats }j)=\operatorname{logistic}(s_i-s_j)\). One reference level or sum constraint is needed for identifiability. The comparison graph should connect systems adequately, and repeated tasks/raters create dependence beyond a simple independent model. Ties and nontransitive preferences need explicit extensions or diagnostics rather than forced binary labels.

### stat-34-07

**Interrater agreement analysis**

Interrater agreement measures consistency of judgments, using raw agreement and chance-adjusted measures such as kappa or suitable ordinal alternatives. Agreement depends on prevalence and category use, so high raw agreement can coexist with low kappa. Disagreement may reveal an unclear rubric, genuine ambiguity or insufficient expertise. Inspect cases, not only the summary coefficient, before deciding whether adjudication or rubric revision is needed.

### stat-34-08

**Judge-model validation**

Judge-model validation compares automated scores with trusted human or executable judgments on representative held-out cases. Include incorrect but polished answers, concise correct answers and domain-specific edge cases. Measure error types and calibration across score levels. A judge evaluated only on easy cases can look reliable while failing the exact boundary used for release decisions, and self-evaluation can share errors with the generating model.

### stat-34-09

**Position and verbosity bias**

Position bias favors a response because it appears first or second, while verbosity bias favors length independent of useful content. Reverse pair order and compare equally informative short/long variants to detect these effects. Blinding model identity does not remove them. A scoring rubric should reward supported completeness and penalize unsupported additions, so extra text cannot earn quality merely by occupying more space.

### stat-34-10

**Factuality evaluation**

Factuality evaluation checks whether claims are true against an appropriate external reference or validated computation. Break a long answer into atomic claims so one correct sentence cannot mask several false ones. Time, jurisdiction, scope and source reliability matter. A statement can be factually true but irrelevant or unsupported by the provided context, so factuality should remain distinct from groundedness and task success.

### stat-34-11

**Groundedness evaluation**

Groundedness evaluates whether an answer's claims are supported by the evidence actually supplied or permitted. A correct fact recalled from weights may be ungrounded under a source-restricted task. Support requires the cited passage to entail the claim at the stated scope, including qualifiers and dates. Evaluate unsupported additions and contradictions separately, and permit an explicit unknown when the evidence does not answer the question.

### stat-34-12

**Retrieval evaluation**

Retrieval evaluation measures whether relevant, authorized and current evidence reaches the generator. Recall at k assesses coverage of needed evidence, while ranking measures consider placement and relevance. Some questions require multiple passages, so one relevant hit may be insufficient. Evaluate on the actual corpus snapshot and candidate filters. Oracle-context performance isolates generation but must not be reported as real retrieval success.

### stat-34-13

**Citation quality evaluation**

Citation quality includes source validity, passage location, claim support and coverage of claims needing evidence. A syntactically valid link or matching document title is insufficient. Check that the cited version contains the relevant passage and supports the precise conclusion. Citation precision asks whether supplied citations support their claims; citation coverage asks whether claims that need support received it. These are different denominators.

### stat-34-14

**Benchmark contamination analysis**

Benchmark contamination occurs when evaluation material or close relatives influence pretraining, fine-tuning, prompt development or retrieval curation in a way that invalidates the intended holdout. Exact deduplication catches only some overlap; templates, paraphrases and shared source documents can also leak. Track provenance and split related families together. A contaminated score may still describe memorized performance, but it cannot establish generalization to unseen tasks.

### stat-34-15

**Prompt sensitivity analysis**

Prompt sensitivity analysis evaluates reasonable alternative formulations of the same task while preserving its semantics. Large changes in correctness or abstention indicate fragility. Separate legitimate instruction changes from harmless wording changes, and keep paraphrase families together when estimating uncertainty. Tuning a prompt on every test case converts the benchmark into development data and obscures expected real-user variability.

### stat-34-16

**Robustness and adversarial evaluation**

Robustness and adversarial evaluation tests difficult inputs such as irrelevant context, conflicting evidence, malformed records or instructions embedded in retrieved data. The threat or perturbation model must match the application. Passing a small attack list does not prove comprehensive robustness. Record the exact failure boundary and ensure the system treats external text as evidence rather than authority to change permissions or task requirements.

### stat-34-17

**Agent trajectory evaluation**

Agent trajectory evaluation inspects tool choices, arguments, intermediate observations and final actions. A correct final answer reached through an unauthorized write or unsupported assumption is not a successful workflow. Conversely, a failed tool can be handled correctly through bounded recovery. Define allowed actions, required evidence and stop/escalation conditions, and score the actual recorded trajectory rather than a model's retrospective narrative about it.

### stat-34-18

**Repeated-trial reliability**

Repeated-trial reliability estimates how often a system succeeds across repeated stochastic runs or varied cases. Distinguish repeatability on one prompt from generalization across independent task families. Report the number of trials, seeds or decoding conditions and confidence intervals under the correct dependence model. A single impressive run is weak evidence for a workflow expected to work consistently.

### stat-34-19

**Cost–latency–quality analysis**

Cost-latency-quality analysis compares task performance with compute, token use, elapsed time and human correction effort. Tail latency matters when users or downstream jobs wait for the slowest responses. Pareto analysis identifies alternatives not dominated on all objectives. A cheap model that requires frequent expert repair may be more expensive end to end, so define the accounting boundary and expected task mix.

### stat-34-20

**End-to-end system evaluation**

End-to-end evaluation measures the complete path from request and permitted data to an accepted operational result. Retrieval, parsing, tool execution, generation, validation and human escalation interact. Component improvements can fail to improve the final task if another stage is the bottleneck. Preserve raw artifacts and failure categories so a final score supports diagnosis and reproducibility rather than only a leaderboard.

## Worked Python demonstrations

Complete offline program: [chapter_34.py](../examples/chapter_34.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_34.py
```

### Put uncertainty around eight successes

Eight of ten independent illustrative cases succeed. The empirical rate is 0.8, but the Wilson interval is broad, roughly 0.49 to 0.94. Ten paraphrases from one document would not justify this independent-case interpretation. The calculation demonstrates why a small acceptance set cannot support a precise reliability claim.

### Separate citation presence from support

The retriever finds only one of two required source IDs, giving evidence recall one-half. All three answer claims have citations, but a human support annotation marks only two as supported. Citation presence is therefore 100 percent while supported-citation precision is two-thirds. The example explicitly consumes annotations; it does not pretend a Boolean lookup is a general factuality evaluator.

### Preserve paired outcomes and rater disagreement

Two raters agree on four of six binary cases. Their marginal positive rates imply chance agreement one-half, so kappa is one-third. A separate paired system example shows one B-only success and no A-only successes. Those counts retain the paired design; a reliable improvement claim would need more representative cases and uncertainty analysis.

### Compare alternatives without hiding the tradeoff

System C is worse than A in quality, cost and latency, so it is dominated. A and B remain on the Pareto frontier: B has higher quality but costs more and takes longer. Choosing between them requires the application's utility and constraints, not an unexplained average of incompatible units.

### Complete executable example

```python
import numpy as np


def wilson_interval(successes, total, z=1.96):
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return center - half, center + half


def repeated_reliability():
    outcomes = np.array([1, 1, 1, 0, 1, 1, 0, 1, 1, 1])
    low, high = wilson_interval(int(outcomes.sum()), len(outcomes))
    assert outcomes.mean() == 0.8 and low < 0.8 < high and low > 0.45 and high < 0.96
    print("Independent-case success rate and Wilson interval:", outcomes.mean(), low, high)


def retrieval_and_claim_support():
    needed = {"policy-v2", "runtime-17"}
    retrieved = ["policy-v2", "glossary-v1"]
    recall = len(needed & set(retrieved)) / len(needed)
    # Human-supplied support labels for three atomic claims, not an automatic entailment model.
    claim_support = np.array([True, True, False])
    has_citation = np.array([True, True, True])
    supported_citations = np.sum(claim_support & has_citation) / np.sum(has_citation)
    assert recall == 0.5 and np.isclose(supported_citations, 2 / 3)
    assert has_citation.mean() == 1 and supported_citations < 1
    print(
        "Evidence recall:",
        recall,
        "citations present:",
        has_citation.mean(),
        "supported:",
        supported_citations,
    )


def paired_and_agreement():
    first = np.array([1, 1, 0, 0, 1, 0])
    second = np.array([1, 0, 0, 0, 1, 1])
    agreement = np.mean(first == second)
    expected = first.mean() * second.mean() + (1 - first.mean()) * (1 - second.mean())
    kappa = (agreement - expected) / (1 - expected)
    assert np.isclose(agreement, 2 / 3) and np.isclose(kappa, 1 / 3)
    a = np.array([1, 1, 0, 0, 1])
    b = np.array([1, 1, 1, 0, 1])
    assert np.sum((b == 1) & (a == 0)) == 1 and np.sum((a == 1) & (b == 0)) == 0
    print("Raw agreement, kappa:", agreement, kappa, "paired B-only success:", 1)


def pareto_tradeoff():
    # Higher quality, lower cost and latency are preferred.
    systems = [("A", 0.80, 1.0, 2.0), ("B", 0.85, 2.0, 3.0), ("C", 0.78, 2.0, 4.0)]
    efficient = []
    for name, q, c, l in systems:
        dominated = any(
            q2 >= q and c2 <= c and l2 <= l and (q2 > q or c2 < c or l2 < l)
            for name2, q2, c2, l2 in systems
            if name2 != name
        )
        if not dominated:
            efficient.append(name)
    assert efficient == ["A", "B"]
    print("Pareto-efficient alternatives:", efficient)


def main():
    repeated_reliability()
    retrieval_and_claim_support()
    paired_and_agreement()
    pareto_tradeoff()


if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Can an LLM judge replace domain experts?** It can reduce review effort if validated for the specific rubric and case distribution. Keep expert audits, executable checks where possible, and failure-case analysis. Agreement on general preference data does not establish correctness on specialized statistical, scientific or policy questions.

**Interview: How do you diagnose a RAG failure?** Check corpus presence and access first, then retrieval, ranking, context assembly and generation. Compare oracle-context with real-context runs. A generator that fails with the correct passage needs a different repair from a retriever that never supplied it.

**Interview: What is a fair base-versus-fine-tuned comparison?** Freeze held-out case families and run both systems with matched evidence and decoding conditions, recording model/adaptor versions. Score task success, support, abstention, format and regressions, with paired uncertainty and cost. Training examples or near-duplicates must not become the final test set.

**Interview: Does zero observed hallucination establish a zero hallucination rate?** No. It is a finite sample outcome conditional on the tested distribution and evaluator sensitivity. Report the sample size, interval or bound under stated assumptions, and what kinds of unsupported claims the test could actually detect.

**Interview: How should model-written statistical conclusions be graded?** Require the executed analysis artifact, data contract and estimator assumptions. Check numerical values against code output and causal language against the study design. A persuasive explanation or citation to a statistics page cannot validate an unexecuted calculation.

## Primary sources and official APIs

- [Liang and colleagues, Holistic Evaluation of Language Models](https://arxiv.org/abs/2211.09110)

- [Zheng and colleagues, Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685)

- [Es and colleagues, evaluation of retrieval-augmented generation](https://arxiv.org/abs/2309.15217)

## Continue into applied evaluation

The [retrieval and answer evaluation guide](../../llm-applied/guides/llm-applied-012.md) separates oracle-context controls from the real retrieved-context pipeline. The [grounded claims guide](../../llm-applied/guides/llm-applied-011.md) supplies explicit support and abstention boundaries. A component test should remain labeled by the component it actually observes.

## Reading connections

[Previous chapter](33-deep-learning-language-and-generative-modeling.md) | [Book contents](../README.md) | [Next chapter](35-bandits-reinforcement-learning-and-adaptive-decisions.md)
