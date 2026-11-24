# llm-039: explanatory solutions

Read these robustness, fairness and finite safety evidence answers after attempting *Compare uneven denominators* through *Write a finite claim*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Analyze a counterfactual pair* points to one step. `llm-039_solution.py` holds the assertions; this page explains how they test counterfactual pair. Then try *Write a finite claim* on a fresh input you chose before looking.

## Mechanism review

Finite robustness and safety evaluations describe observed behavior on specified cases. They cannot prove that every possible future input is safe. Group labels, prompt families, severity and sample counts matter because an aggregate rate can conceal rare but consequential failures. Counterfactual pairs change one relevant attribute while keeping the rest of a case fixed, helping identify inconsistent treatment. A pair is useful only if the expected behavior is justified for the task. This worksheet uses fictional authored cases and collects no personal data. Its purpose is to make claims proportional to evidence and to preserve failures for review, rather than to award an unsupported safety certificate.

**Counterfactual pair:** Two cases differing in a controlled attribute.

**Severity:** The consequence category of a failure, separate from frequency.

**Finite evidence:** Observations from a bounded set of tested cases.

## Reading the implementation

Read the supplied rows as family, group, count, failures, severity. Calculate rates only with nonzero counts. Keep severe failures visible even when overall success is high. For a counterfactual pair, list the changed attribute and the behavior that should remain stable. An untested group receives an unknown result, not a zero failure rate. State the scope and the next evidence needed in the conclusion.

## Exercise 1: Compare uneven denominators

The question is: Group D has 1 failure in 50 cases; group E has 0 failures in 5. Compare the observed rates and what each establishes.

A lower observed rate on a much smaller denominator is weak evidence. Report both counts so a reader can see how little E was tested.

```text
D: failures 1, count 50, observed rate 1/50 = 0.02
E: failures 0, count 5, observed rate 0/5
A zero count in 5 cases does not establish that E is safer than D.
```

**Expected:** D observed 1/50 = 0.02; E observed 0/5; five cases do not show that E is safer than D.

**Verify:** Check that 1/50 is written as 0.02 (2 percent), that both denominators 50 and 5 are reported, and that the answer does not rank E above D.

## Exercise 2: Recompute a gate with two severe failures

The question is: Eighteen minor cases pass and two severe cases fail. Calculate the pass rate and the gate result.

The pass rate matches the earlier case, yet the decision depends on the severe-failure count, which is now two. An aggregate rate cannot replace the gate.

```text
Pass rate = 18/20 = 90 percent
Severe failures = 2
Required severe-failure gate = fail
```

**Expected:** 18/20 = 90 percent passes; 2 severe failures; the gate fails.

**Verify:** Check that the pass rate is 18/20 = 0.9 and that the gate decision is taken from the severe-failure count 2, not from the 90 percent pass rate.

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

**Verify:** Check that the record holds qualifications identical, names the single changed field and contrasts the expected equal eligibility with the observed opposite outcomes.

## Exercise 4: Handle an untested group

The question is: Group C has count 0. Decide what rate and claim to report.

Reporting zero would turn absence of observations into apparent success. A missing group should remain a visible gap in the evidence.

```text
Group C: count 0, failures not observed
Rate: undefined
Claim: no evaluation evidence for this group
```

**Expected:** rate unknown; group untested.

**Verify:** Check that group C reports count 0 with an undefined rate, not 0 percent or a pass, and that the claim says no evaluation evidence exists for the group.

## Exercise 5: Separate families from paraphrases

The question is: Twenty prompts are paraphrases of one attack family. State the independent coverage count under family-based evaluation.

Repeated variants can reveal local sensitivity, but they do not expand conceptual coverage as much as new families. The evaluation unit must match the conclusion.

```text
Prompt variants: 20
Independent authored families: 1
Report both; do not claim 20 independent threat classes.
```

**Expected:** one tested family, twenty variants.

**Verify:** Check that the report carries both counts, 20 variants and 1 independent family, and never presents the variants as 20 threat classes.

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

**Verify:** Check that the conclusion mentions the one severe failure, the untested group C and the no-go decision, and that it limits the claim to this finite suite.

## Review after comparison

Change one input to *Handle an untested group* and predict the result first; keep *Write a finite claim* failing beside the repair. Log a missing the Python standard library separately from a wrong counterfactual pair value in `llm-039`.
