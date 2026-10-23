# llm-039: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Finite robustness and safety evaluations describe observed behavior on specified cases. They cannot prove that every possible future input is safe. Group labels, prompt families, severity and sample counts matter because an aggregate rate can conceal rare but consequential failures. Counterfactual pairs change one relevant attribute while keeping the rest of a case fixed, helping identify inconsistent treatment. A pair is useful only if the expected behavior is justified for the task. This worksheet uses fictional authored cases and collects no personal data. Its purpose is to make claims proportional to evidence and to preserve failures for review, rather than to award an unsupported safety certificate.

**Counterfactual pair:** Two cases differing in a controlled attribute.

**Severity:** The consequence category of a failure, separate from frequency.

**Finite evidence:** Observations from a bounded set of tested cases.

## Reading the implementation

Read the supplied rows as family,group,count,failures,severity. Calculate rates only with nonzero counts. Keep severe failures visible even when overall success is high. For a counterfactual pair, list the changed attribute and the behavior that should remain stable. An untested group receives an unknown result, not a zero failure rate. State the scope and the next evidence needed in the conclusion.

## Exercise 1: Read group denominators

The question is: GroupA has0 failures in10 cases;groupB has0 in1. Compare what is established.

Equal observed rates do not imply equal uncertainty. The denominator is a central part of the result and should remain visible in a report.

```text
A: failures0,count10,observed rate0/10
B: failures0,count1,observed rate0/1
Neither establishes a zero population failure probability.
```

**Expected:** both observed zero;B has much less evidence.

**Verify:** Compare the computed values or written argument with both observed zero;B has much less evidence.

## Exercise 2: Expose a severe failure

The question is: Nine minor cases pass and one severe case fails. Calculate total pass rate and state the release implication under a no-severe-failure gate.

Averages cannot override an explicitly required critical condition. The decision rule should be established before seeing which case failed.

```text
Pass rate = 9/10 = 90percent
Severe failures = 1
Required severe-failure gate = fail
```

**Expected:** 90percent passes;gate fails.

**Verify:** Compare the computed values or written argument with 90percent passes;gate fails.

## Exercise 3: Analyze a counterfactual pair

The question is: Two fictional applicants have identical task-relevant qualifications; only a neutral name token differs, and the system gives opposite eligibility outcomes.

The pair controls the relevant input information for the stated task. It does not by itself characterize all fairness properties or all real populations.

```text
Pair C1/C2:
Qualifications: identical
Changed field: fictional name token
Expected eligibility: equal
Observed eligibility: opposite
```

**Expected:** inconsistency requires investigation under this fixture rubric.

**Verify:** Compare the computed values or written argument with inconsistency requires investigation under this fixture rubric.

## Exercise 4: Handle an untested group

The question is: GroupC hascount0. Decide what rate and claim to report.

Reporting zero would turn absence of observations into apparent success. A missing group should remain a visible gap in the evidence.

```text
Group C: count0,failuresnot observed
Rate: undefined
Claim: no evaluation evidence for this group
```

**Expected:** rate unknown;group untested.

**Verify:** Compare the computed values or written argument with rate unknown;group untested.

## Exercise 5: Separate families from paraphrases

The question is: Twenty prompts are paraphrases of one attack family. State the independent coverage count under family-based evaluation.

Repeated variants can reveal local sensitivity, but they do not expand conceptual coverage as much as new families. The evaluation unit must match the conclusion.

```text
Prompt variants:20
Independent authored families:1
Report both; do not claim20 independent threat classes.
```

**Expected:** one tested family,twenty variants.

**Verify:** Compare the computed values or written argument with one tested family,twenty variants.

## Exercise 6: Write a finite claim

The question is: Draft a conclusion for the cases above including the severe failure and untested group.

A negative decision can be the most useful outcome. Preserving the failed family and its exact conditions supports repair and a meaningful future retest.

```text
Observed: one severe failure in the authored set; group C untested.
Decision: no-go under the stated severe-failure gate.
Limit: this finite suite cannot establish universal safety.
Next evidence: investigate the failure and evaluate additional independent families.
```

**Expected:** conclusion rejects a universal safety guarantee.

**Verify:** Compare the computed values or written argument with conclusion rejects a universal safety guarantee.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
