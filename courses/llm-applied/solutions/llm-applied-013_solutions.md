# llm-applied-013: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Reliability comparisons require an explicit unit of independence. Ten paraphrases of one question are not ten independent domains. Pair candidate systems on the same question IDs, then preserve related questions within a family when estimating uncertainty. A family-weighted mean gives each authored task family equal weight; a row-weighted mean gives frequently repeated families more influence. Neither is automatically correct, but the choice must match the intended deployment population.

A bootstrap resamples observed units with replacement. It can describe variability under its assumptions, but cannot repair a biased or tiny evaluation set. A confidence interval excluding zero is not a release decision by itself: severe unsupported claims, access leaks or unacceptable coverage can still block the system. This lesson uses saved binary error differences and explicit abstention counts. It keeps statistical computation deterministic and separate from any generated narrative interpreting the result.

**Paired evaluation:** Comparing systems on the same identified cases.

**Family unit:** A group of related questions treated together for uncertainty.

**Bootstrap estimate:** A statistic calculated on a resampled set of observed units.

**Selective accuracy:** Accuracy among answered cases, reported beside coverage.

## Reading the implementation

Join system error tables by question ID and reject unequal key sets. Compute errorA-errorB for each pair, aggregate within family, then sample family indices with one seeded NumPy generator. The same sampled family applies to both systems because the difference is already paired. Report the number of independent families, not only the number of paraphrases. Calculate answered accuracy and coverage with separate denominators.

## Derive the paired and family-level comparison

System A has errors[0, 0, 1] on q1, q2, q3; system B has[1, 1, 0] on the same IDs. Subtracting A minus B gives[-1, -1, 1], where negative favors A because smaller error is better. Sorting dictionary keys aligns identities. Pairing by insertion order would compare different questions and produce a statistic with no intended case-level meaning.

The row-weighted mean is(-1-1+1)/3=-1/3. If q1 and q2 are related variants of family F and q3 is family G, the family means are[-1, +1], whose equally weighted average is zero. This is not a disagreement between arithmetic implementations. The row estimand gives family F twice the weight, while the family estimand gives F and G equal weight.

The bootstrap draws two family indices with replacement. There are four equally likely ordered samples from the empirical family distribution:

| Resampled families | Mean difference | Probability |
| --- | --- | --- |
| F, F | -1 | \(\frac{1}{4}\) |
| F, G | 0 | \(\frac{1}{4}\) |
| G, F | 0 | \(\frac{1}{4}\) |
| G, G | +1 | \(\frac{1}{4}\) |

The exact bootstrap mean is zero and variance is1/2. Its standard deviation is \(\sqrt{\frac{1}{2}}\), about0.7071. The2000 seeded draws approximate this very coarse distribution; increasing the draw count only reduces Monte Carlo noise in that approximation. It does not create more than the two observed independent families or establish that those families represent the deployment population.

Pairing preserves the relationship between candidate errors. The variance identity \(\operatorname{Var}(A-B)=\operatorname{Var}(A)+\operatorname{Var}(B)-2\operatorname{Cov}(A,B)\) explains why independently resampling each candidate can change uncertainty. Family resampling must likewise keep all within-family candidate observations together. If question families have unequal intended population weights, specify the weighted estimator and a resampling design that matches it rather than selecting the narrowest interval after the fact.

Selective answering introduces more denominators. With ten questions, six answers and five correct answers, coverage is6/10=0.6 and accuracy among answers is5/6. Correct answers per all requests is5/10. A system that answers only the easiest one correctly has conditional accuracy one but coverage0.1. It may or may not be useful under the task's costs. Always retain how many refusals were appropriate and how many answerable cases were declined.

The saved errors here are teaching data. Their bootstrap computation is real arithmetic, but the arrays are not receipts from running a named model. A real comparison should preserve question IDs, predictions, rubric decisions, candidate configuration and family labels. Review label disagreements, because uncertainty over sampled questions does not automatically account for systematic rubric error.

### Interview reasoning with explanatory answers

**Why can more paraphrases make an interval look falsely precise?** Treating correlated variants as independent rows can overstate the effective evidence. Resampling at the relevant family level preserves that dependence under the chosen empirical design.

**Does a confidence interval establish why one candidate improved?** No. It describes variability of a statistic under assumptions. Attributing improvement to a changed component needs a controlled comparison or suitable causal design.

**Can a severe failure be averaged away?** Arithmetic can dilute it, but the acceptance contract need not permit that. A zero-access-leak requirement is a separate gate whose observed violation blocks release even if an average metric improves.

## Exercise 1: Align paired errors

The question is: Use system A errors \(q_{1}=0\), \(q_{2}=0\), \(q_{3}=1\) and B \(q_{1}=1\), \(q_{2}=1\), \(q_{3}=0\).

Pairing by IDs prevents dictionary order from changing which observations are subtracted. A negative difference favorsA because the metric is error.

```python
a={'q1':0,'q2':0,'q3':1}; b={'q3':0,'q1':1,'q2':1}; ids=sorted(a)
assert set(a)==set(b); difference=np.array([a[i]-b[i] for i in ids],dtype=float)
np.testing.assert_array_equal(difference,[-1,-1,1])
```

**Expected:** differences[-1, -1, 1] by sortedID.

**Verify:** Compare the computed values or written argument with differences[-1, -1, 1] by sortedID.

## Exercise 2: Aggregate by family

The question is: Assignq1, q2 tofamilyF andq3 toG; compare row mean with family mean.

The repeated family changes the row-weighted conclusion. This is a design choice about the evaluation population, not a numerical bug.

```python
families=np.array(['F','F','G']); family_values=np.array([difference[families==f].mean() for f in ['F','G']])
np.testing.assert_allclose(difference.mean(),-1/3,atol=1e-12,rtol=0); assert family_values.mean()==0
```

**Expected:** row mean-1/3; family mean0.

**Verify:** Compare the computed values or written argument with row mean-1/3; family mean0.

## Exercise 3: Resample paired families

The question is: Draw2000 bootstrap samples of the two family differences withseed17.

Two families produce a coarse empirical distribution. A large number of bootstrap draws does not create additional independent evidence.

```python
indices=np.random.default_rng(17).integers(0,2,size=(2000,2)); estimates=family_values[indices].mean(1)
assert set(np.unique(estimates))=={-1.,0.,1.}
np.testing.assert_array_equal(indices,np.random.default_rng(17).integers(0,2,size=(2000,2)))
```

**Expected:** all estimates are-1, 0 or1; repeatable with same seed.

**Verify:** Compare the computed values or written argument with all estimates are-1, 0 or1; repeatable with same seed.

## Exercise 4: Report coverage and answered accuracy

The question is: For10 questions, answer6 with 5 correct and abstain on4.

A system can improve answered accuracy by refusing difficult cases. Coverage exposes that tradeoff instead of presenting a selective score as overall success.

```python
total,answered,correct=10,6,5
assert answered/total==.6 and correct/answered==5/6 and total-answered==4
```

**Expected:** coverage.6; answered accuracy5/6; overall correct answers5.

**Verify:** Compare the computed values or written argument with coverage.6; answered accuracy5/6; overall correct answers5.

## Exercise 5: Block a severe boundary failure

The question is: Combine a favorable mean comparison with one access leak and apply a zero-access-leak gate.

An average quality improvement does not compensate for a required authorization failure. The gate should be declared before inspecting results.

```python
mean_gain=.1; access_leaks=1
release=mean_gain>0 and access_leaks==0
assert not release
```

**Expected:** release decisionFalse.

**Verify:** Compare the computed values or written argument with release decisionFalse.

## Exercise 6: Keep final tests out of selection

The question is: Record retriever selection on validation and final scoring on test; flag a test-based parameter change.

Once the test influences a configuration choice, it is part of selection. A new untouched assessment is needed for a fresh final claim.

```python
ledger=[('choose_k','validation'),('score_final','test')]
assert all(part=='validation' for action,part in ledger if action=='choose_k')
assert ('choose_k','test')[1]!='validation'
```

**Expected:** test-based selection rejected.

**Verify:** Compare the computed values or written argument with test-based selection rejected.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
