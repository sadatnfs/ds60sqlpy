# torch-034: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A reliability report should preserve the conditions and denominators behind a score. Group A with zero errors in one case does not provide the same evidence as zero errors in hundreds of independent cases. Duplicate records can improve an apparent rate without testing new conditions. Perturbation tests need a label policy: crossing a legitimate decision boundary may change the correct target rather than reveal a robustness failure.

Privacy and safety claims require their own mechanisms and evidence. A synthetic fixture containing no personal data does not establish differential privacy. A finite set of successful adversarial checks does not prove all future inputs are safe. This chapter uses Torch tensors for error accounting and controlled perturbations, then writes a bounded model-card record with untested conditions and failure severity.

**Subgroup denominator:** The observation count supporting a group metric.

**Robustness condition:** A specified input change under a declared label policy.

**Finite safety evidence:** Observed results on bounded cases without a universal guarantee.

**Model card:** A record of intended use, evidence and limitations.

## Reading the implementation

Compute boolean error vectors before aggregation. Groupby declared labels and retain integer error/count pairs. Compare row count with unique ID count to expose duplicates. Use None for an untested group rather than a rate of zero. Keep severity categories separate from overall pass rate, and make the decision gate explicit before inspecting results.

## Keep population, perturbation and mechanism claims separate

The original three records contain one error: groupA has \(\frac{1}{2}\) and groupB has 0/1. Overall error is \(\frac{1}{3}\). Repeating the correct record c five additional times creates eight rows but only three unique IDs. A naive row-weighted error becomes \(\frac{1}{8}\) even though no new case was tested. The apparent improvement comes entirely from changing the weight of one existing success.

This counterexample does not imply that every repeated identity should be removed. A longitudinal task may legitimately contain several observations from one person or device. The question is which unit the reported quantity is intended to average over, and whether dependence is modeled. Exact duplicate detection, source-family grouping and a weighting policy are related but different controls. A set of three IDs alone also does not prove those units are statistically independent.

Zero errors among one observation is weak evidence about an unknown error probability. Under a deliberately stated independent Bernoulli sampling model, the chance of observing zero errors in n cases is \((1-p)^n\). Solving \((1-p)^n=0.05\) gives a one-sided 95% upper bound \(1-{0.05}^{\frac{1}{n}}\):0.95 at \(n=1\) and approximately 0.0295 at \(n=100\). This arithmetic illustrates why denominators matter. The hand-selected synthetic cases do not automatically satisfy the random-sampling assumptions needed to interpret that bound as a population claim.

An empty group has no measured rate. Returning None preserves that absence; returning zero invents a successful observation. A report or chart should not replace missing rates with zero merely to fill a display. Likewise, a confidence calculation cannot create coverage for a group or condition that never appeared in the data. Keep coverage counts and the intended target population beside every aggregate.

The perturbation rule here is f(x)=1 when \(x\ge 0\). Starting at one, the shifts-0.1, -0.9, -1.1 produce 0.9, 0.1, -0.1 and therefore labels 1, 1, 0. If the target itself is defined by the observed sign, the final change is correct behavior after crossing the decision boundary. Calling it a robustness failure would assume an invariant label that the task definition does not support.

A different application might model these shifts as measurement noise while the latent class remains fixed. That is a different target policy and needs its own oracle. For this simple sign rule, perturbations with magnitude strictly below one cannot cross from the starting point to the negative side. That analytic statement is local to this scalar rule and declared perturbation set; it is not evidence that an arbitrary neural classifier is robust to all small changes.

Severity is another independent axis. Nine minor passes and one severe failure yield a90% overall pass rate. If the predeclared release rule blocks on any severe failure, the correct decision remains no-go. Choosing a favorable aggregate after observing the severe failure changes the decision policy. Preserve case-level identity, severity and the actual failed condition so a summary cannot erase it.

Privacy is not established by removing names from an example or by obtaining a good accuracy score. Differential privacy describes a randomized mechanism's output behavior under a defined change to a dataset. Its guarantee depends on the neighboring-dataset unit, privacy parameters and the mechanism/accounting assumptions. Record-level adjacency and person-level adjacency are different promises when a person contributes multiple rows. Clipping, noise, sampling and repeated releases require a coherent analysis; this chapter implements none of them. [NIST SP 800-226](https://csrc.nist.gov/pubs/sp/800/226/final) discusses evaluation of such guarantees and implementation hazards.

An empirical privacy attack test and a mathematical privacy guarantee answer different questions. Failing to observe leakage in a few attempts does not prove a bound over all neighboring datasets and outputs. Conversely, a claimed formal bound does not remove the need to inspect the actual implementation, access controls and intended release. The lesson's model card therefore records synthetic teaching use and no privacy guarantee rather than promoting absence of personal data into a property of the training algorithm.

A useful card joins intended use, data/version identity, evaluation units, group counts, perturbation policy, severity results and untested conditions. It can summarize existing evidence but does not create it. The paired TensorFlow route uses the same reasoning fixtures, so framework choice does not change the denominator, independence or privacy interpretation.

## Exercise 1: Count group errors

The question is: Use groups A, A, B with truth 1, 1, 0 and prediction 1, 0, 0.

Counts keep the evidence visible. Equal rates with different denominators do not imply equal uncertainty.

```python
truth=torch.tensor([1,1,0]); prediction=torch.tensor([1,0,0]); groups=['A','A','B']; errors=prediction!=truth
report={group:(int(errors[torch.tensor([g==group for g in groups])].sum()),groups.count(group)) for group in ['A','B']}
assert report=={'A':(1,2),'B':(0,1)}
```

**Expected:** A1/2errors; B0/1.

**Verify:** Compare the computed values or written argument with A1/2errors; B0/1.

## Exercise 2: Expose repeated identities

The question is: Repeatcorrectrecordc five times and compare row count with unique IDs.

Repeated rows can bias a metric without adding independent cases. Identity validation belongs before aggregation.

```python
ids=['a','b','c']+['c']*5
assert len(ids)==8 and len(set(ids))==3
```

**Expected:** 8rows but 3 unique IDs.

**Verify:** Compare the computed values or written argument with 8rows but 3 unique IDs.

## Exercise 3: Trace a controlled perturbation

The question is: Classify \(x\ge 0\) at base 1 after shifts-.1, -.9, -1.1.

The last shift crosses the defined boundary. Whether that counts as a robustness failure depends on the intended label semantics.

```python
base=torch.tensor(1.); shifts=torch.tensor([-.1,-.9,-1.1]); changed=(base+shifts>=0).long()
assert changed.tolist()==[1,1,0]
```

**Expected:** labels 1, 1, 0.

**Verify:** Compare the computed values or written argument with labels 1, 1, 0.

## Exercise 4: Keep severe failures visible

The question is: Use 9 minor passes and 1 severe failure.

A high aggregate cannot override a predeclared critical-failure gate. Report both frequency and consequence.

```python
passed=torch.tensor([True]*9+[False]); severe=torch.tensor([False]*9+[True])
np.testing.assert_allclose(passed.float().mean().item(),.9,atol=1e-6,rtol=0)
assert int((~passed&severe).sum())==1
```

**Expected:** overall pass rate.9; severe failure count 1.

**Verify:** Compare the computed values or written argument with overall pass rate.9; severe failure count 1.

## Exercise 5: Represent an untested group

The question is: Define a rate helper with count 0.

Absence of observations is not a perfect score. Keeping None visible prevents an untested group from looking validated.

```python
def rate(errors,count): return None if count==0 else errors/count
assert rate(0,0) is None and rate(0,1)==0
```

**Expected:** None for untested; 0for zero errors in one case.

**Verify:** Compare the computed values or written argument with None for untested; 0for zero errors in one case.

## Exercise 6: Write a bounded card

The question is: Record 3 unique units, synthetic teaching use and untested future conditions.

The card organizes evidence and limits; it does not create evidence merely by being complete. A production decision needs representative tests and appropriate privacy analysis.

```python
card={'unique_units':3,'use':'synthetic teaching','untested':['future population','private-data behavior'],'differential_privacy_established':False}
assert card['unique_units']==3 and not card['differential_privacy_established']
```

**Expected:** card explicitly has no privacy guarantee.

**Verify:** Compare the computed values or written argument with card explicitly has no privacy guarantee.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
