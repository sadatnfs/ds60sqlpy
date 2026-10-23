# llm-040: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A reliability argument combines a decision rule with evidence and its limits. When comparing systems, preserve question-level pairing and the dependence between paraphrases in the same family. Resampling individual rows can exaggerate the effective sample size when many variants repeat one underlying task. Aggregate or resample by family under a declared policy. Prompt and retrieval tuning belong on validation data; the final holdout is opened after the policy is frozen. Abstention changes coverage, so accuracy among answered questions must be reported beside answered count and total count. A favorable mean is not enough when severe failures violate a required gate.

**Clustered resampling:** Sampling related groups as units rather than individual rows.

**Coverage:** Fraction of questions receiving an answer.

**Reliability argument:** A decision supported by specified tests and bounded assumptions.

## Reading the implementation

Align both systems by question ID, compute per-question loss or correctness differences, then average within family if families are the resampling unit. Use one index draw for the paired family differences. Preserve a decision ledger separating validation choices from final assessment. Calculate coverage=answered/total and selective accuracy=correct_answered/answered, with an explicit empty-answer policy.

## Exercise 1: Align paired question results

The question is: Use questionsq1,q2 inA andq3 inB; system error differences[-1,-1,1].

The repeated familyA receives twice the weight under a row mean. The family mean asks a different question and prevents variants from silently dominating the comparison.

```python
families=['A','A','B']; diff=np.array([-1.,-1.,1.]); grouped=np.array([diff[np.array(families)==f].mean() for f in ['A','B']])
np.testing.assert_array_equal(grouped,[-1,1]); np.testing.assert_allclose(diff.mean(),-1/3,atol=1e-12,rtol=0)
```

**Expected:** question mean-1/3;family meansA-1,B1.

**Verify:** Compare the computed values or written argument with question mean-1/3;family meansA-1,B1.

## Exercise 2: Resample whole families

The question is: Draw1000 bootstrap samples of the two family differences with seed8.

The sample space is tiny and visibly discrete. A smooth-looking interval would not create more independent families than the two observed.

```python
indices=np.random.default_rng(8).integers(0,2,size=(1000,2)); estimates=grouped[indices].mean(1)
assert set(np.unique(estimates))<={-1.,0.,1.} and grouped.mean()==0
```

**Expected:** estimates only-1,0,1;mean of original family values0.

**Verify:** Compare the computed values or written argument with estimates only-1,0,1;mean of original family values0.

## Exercise 3: Expose row-weighting dependence

The question is: Repeatq1 ten times and compare row mean with unchanged family means.

Duplicating a variant can alter a row-weighted conclusion without adding new task families. The test demonstrates why the unit must be chosen before scoring.

```python
repeated=np.concatenate([diff,[-1.]*10]); assert repeated.mean()!=diff.mean() and grouped.mean()==0
```

**Expected:** row mean changes;family mean remains0.

**Verify:** Compare the computed values or written argument with row mean changes;family mean remains0.

## Exercise 4: Report selective accuracy

The question is: Of4 questions,answer2 correctly and abstain on2. Compute coverage and answered accuracy.

Perfect accuracy among answered questions can coexist with limited usefulness. Coverage makes the abstention tradeoff visible.

```python
total,answered,correct=4,2,2
assert answered/total==.5 and correct/answered==1 and correct==2
```

**Expected:** coverage.5;answered accuracy1;total correct answers2.

**Verify:** Compare the computed values or written argument with coverage.5;answered accuracy1;total correct answers2.

## Exercise 5: Audit decision chronology

The question is: Record prompt selection on validation followed by final-test assessment; flag a test-driven prompt change.

Information use determines the boundary. Renaming a file or calling a repeated assessment a confirmation does not restore an untouched holdout.

```python
ledger=[('select_prompt','validation'),('assess','test')]
assert all(part=='validation' for action,part in ledger if action=='select_prompt')
forbidden=('select_prompt','test'); assert forbidden[1]!='validation'
```

**Expected:** test-driven selection is invalid for a fresh final claim.

**Verify:** Compare the computed values or written argument with test-driven selection is invalid for a fresh final claim.

## Exercise 6: Combine gates with uncertainty

The question is: Require no severe failures and adequate family coverage; evaluate a report with one severe failure.

The decision reflects a predeclared constraint. A mean difference and a bootstrap summary provide evidence but do not replace a required failure-severity gate.

```python
gates={'severe_failures':1,'tested_families':2,'minimum_families':2}
go=gates['severe_failures']==0 and gates['tested_families']>=gates['minimum_families']
assert not go
```

**Expected:** decisionno-go regardless of favorable average.

**Verify:** Compare the computed values or written argument with decisionno-go regardless of favorable average.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
