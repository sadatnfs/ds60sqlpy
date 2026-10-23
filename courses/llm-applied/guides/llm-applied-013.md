# llm-applied-013: Paired reliability studies and family-aware uncertainty

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-012`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Reliability comparisons require an explicit unit of independence. The central investigation is concrete: Use systemA errors q1=0, q2=0, q3=1 andB q1=1, q2=1, q3=0. The finish condition is differences[-1, -1, 1] by sortedID. test-based selection rejected. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Reliability comparisons require an explicit unit of independence. Ten paraphrases of one question are not ten independent domains. Pair candidate systems on the same question IDs, then preserve related questions within a family when estimating uncertainty. A family-weighted mean gives each authored task family equal weight; a row-weighted mean gives frequently repeated families more influence. Neither is automatically correct, but the choice must match the intended deployment population.

A bootstrap resamples observed units with replacement. It can describe variability under its assumptions, but cannot repair a biased or tiny evaluation set. A confidence interval excluding zero is not a release decision by itself: severe unsupported claims, access leaks or unacceptable coverage can still block the system. This lesson uses saved binary error differences and explicit abstention counts. It keeps statistical computation deterministic and separate from any generated narrative interpreting the result.

## Design decisions and when to use this method

Use paired and family-aware analysis when multiple systems answer the same questions and the corpus contains related variants. Choose the resampling unit from the data-generation process, not from whichever choice produces a narrower interval. If the final population weights families unequally, declare and justify those weights before evaluation. Report absolute counts, error categories and uncertainty together.

Do not let an LLM write a statistical conclusion that contradicts the computed artifact. The report generator should consume named metrics and their assumptions, and a deterministic check should verify quoted counts and rates. A bootstrap interval is not a causal claim about why one system improved. Controlled ablations and study design are needed to attribute changes to retrieval, adaptation or prompting.

## Vocabulary and concepts

**Paired evaluation:** Comparing systems on the same identified cases.

**Family unit:** A group of related questions treated together for uncertainty.

**Bootstrap estimate:** A statistic calculated on a resampled set of observed units.

**Selective accuracy:** Accuracy among answered cases, reported beside coverage.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-013/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-013.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-013.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Join system error tables by question ID and reject unequal key sets. Compute errorA-errorB for each pair, aggregate within family, then sample family indices with one seeded NumPy generator. The same sampled family applies to both systems because the difference is already paired. Report the number of independent families, not only the number of paraphrases. Calculate answered accuracy and coverage with separate denominators.

## Worked example / walkthrough

### Example A: Align paired errors

Pairing by IDs prevents dictionary order from changing which observations are subtracted. A negative difference favorsA because the metric is error.

```python
import numpy as np

a={'q1':0,'q2':0,'q3':1}; b={'q3':0,'q1':1,'q2':1}; ids=sorted(a)
assert set(a)==set(b); difference=np.array([a[i]-b[i] for i in ids],dtype=float)
np.testing.assert_array_equal(difference,[-1,-1,1])
```

**Expected:** differences[-1, -1, 1] by sortedID.

### Example B: Aggregate by family

The repeated family changes the row-weighted conclusion. This is a design choice about the evaluation population, not a numerical bug.

```python
families=np.array(['F','F','G']); family_values=np.array([difference[families==f].mean() for f in ['F','G']])
np.testing.assert_allclose(difference.mean(),-1/3,atol=1e-12,rtol=0); assert family_values.mean()==0
```

**Expected:** row mean-1/3; family mean0.

### Example C: Resample paired families

Two families produce a coarse empirical distribution. A large number of bootstrap draws does not create additional independent evidence.

```python
indices=np.random.default_rng(17).integers(0,2,size=(2000,2)); estimates=family_values[indices].mean(1)
assert set(np.unique(estimates))=={-1.,0.,1.}
np.testing.assert_array_equal(indices,np.random.default_rng(17).integers(0,2,size=(2000,2)))
```

**Expected:** all estimates are-1, 0 or1; repeatable with same seed.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: differences[-1, -1, 1] by sortedID. test-based selection rejected. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Align paired errors.** Use systemA errors q1=0, q2=0, q3=1 andB q1=1, q2=1, q3=0.
   **Expected:** differences[-1, -1, 1] by sortedID.
   **Verify:** Save the assertion results for exercise 1, including differences[-1, -1, 1] by sortedID.

2. **Aggregate by family.** Assignq1, q2 tofamilyF andq3 toG; compare row mean with family mean.
   **Expected:** row mean-1/3; family mean0.
   **Verify:** Save the assertion results for exercise 2, including row mean-1/3; family mean0.

3. **Resample paired families.** Draw2000 bootstrap samples of the two family differences withseed17.
   **Expected:** all estimates are-1, 0 or1; repeatable with same seed.
   **Verify:** Save the assertion results for exercise 3, including all estimates are-1, 0 or1; repeatable with same seed.

4. **Report coverage and answered accuracy.** For10 questions, answer6 with 5 correct and abstain on4.
   **Expected:** coverage.6; answered accuracy5/6; overall correct answers5.
   **Verify:** Save the assertion results for exercise 4, including coverage.6; answered accuracy5/6; overall correct answers5.

5. **Block a severe boundary failure.** Combine a favorable mean comparison withone access leak and apply a zero-access-leak gate.
   **Expected:** release decisionFalse.
   **Verify:** Save the assertion results for exercise 5, including release decisionFalse.

6. **Keep final tests out of selection.** Record retriever selection onvalidation and final scoring ontest; flag a test-based parameter change.
   **Expected:** test-based selection rejected.
   **Verify:** Save the assertion results for exercise 6, including test-based selection rejected.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Paired evaluation, Family unit, Bootstrap estimate using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-012` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [NumPy reference](https://numpy.org/doc/stable/reference/), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-013, Paired reliability studies and family-aware uncertainty.
Read courses/llm-applied/guides/llm-applied-013.md and courses/llm-applied/lessons/llm-applied-013.py. Direct prerequisites: `llm-applied-012`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
