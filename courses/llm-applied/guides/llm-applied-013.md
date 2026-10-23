# llm-applied-013: Paired reliability studies and family-aware uncertainty

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-012`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A reliability study must define what varies and what population the comparison represents. This chapter connects paired question results, family dependence, stochastic model behavior and selective answering to an interpretable decision about an assistant.

## Purpose and mental model

Reliability comparisons require an explicit unit of independence. Ten paraphrases of one question are not ten independent domains. Pair candidate systems on the same question IDs, then preserve related questions within a family when estimating uncertainty. A family-weighted mean gives each authored task family equal weight; a row-weighted mean gives frequently repeated families more influence. Neither is automatically correct, but the choice must match the intended deployment population.

A bootstrap resamples observed units with replacement. It can describe variability under its assumptions, but cannot repair a biased or tiny evaluation set. A confidence interval excluding zero is not a release decision by itself: severe unsupported claims, access leaks or unacceptable coverage can still block the system. This lesson uses saved binary error differences and explicit abstention counts. It keeps statistical computation deterministic and separate from any generated narrative interpreting the result.

## Decide which improvement the study is meant to estimate

The Methods Desk team has two candidate configurations and a fixed question set. Candidate A may answer exact definitions well while candidate B handles ambiguous analytical requests better. A single average can conceal that pattern, especially if the benchmark contains many paraphrases of the easy definition questions and only a few examples of the harder task.

The estimand is the quantity the study is trying to learn about. It might be the difference in error across all incoming requests, the average difference across equally weighted subject families, or the change in supported-answer coverage under a fixed abstention policy. Those targets imply different weights. Choosing the weighting rule after seeing which candidate wins turns the reported result into another selection decision.

The small fixture below makes this visible without a complex model. Repeating a favorable family changes the row-weighted mean but not the equally weighted family mean. Both calculations are mathematically valid. Their scientific usefulness depends on whether the weighting matches the population the assistant is intended to serve.

## Pair the cases before estimating variability

A difficult question tends to affect both candidates. Comparing their results on the same identified case preserves that shared difficulty. The difference for question i can be defined as error_A_i minus error_B_i, with a negative value favoring A. The study then analyzes those paired differences rather than pretending the two error tables are unrelated samples.

Pairing requires more than equal row counts. The question, source snapshot, policy, rubric and relevant evaluation conditions must correspond. If one candidate sees an updated policy or a different context budget, the comparison may still be useful as a system comparison, but it no longer isolates the same component change. Preserve those conditions alongside the question ID.

The variance identity for a paired difference explains the role of correlation. Var(A-B)=Var(A)+Var(B)-2Cov(A,B). If the candidates tend to succeed and fail on the same questions, that covariance can materially affect uncertainty. Independently resampling A and B destroys the correspondence that the study deliberately created.

## Preserve the dependence among related questions

Paraphrases, document revisions and questions derived from the same source can share errors. Treating every variant as an independent observation may make uncertainty look smaller than the evidence warrants. A family-level analysis first summarizes the paired results within each family and then treats families as the resampling units under its stated assumptions.

That choice does not magically make families independent. The family definition should reflect the dependence relevant to the study. Several families may still share a template, authoring process or narrow knowledge source. With very few independent groups, a bootstrap can describe the empirical sample's coarse variability but cannot create broad domain coverage.

The exact two-family distribution later in the chapter is useful for this reason. Its outcomes remain-1,0 and 1 regardless of how many bootstrap draws are generated. Increasing the number of resamples approximates that distribution more precisely; it does not add new study families. A reported interval should therefore be accompanied by the number and nature of the underlying units.

## Separate question variation from model variation

A language-model system can vary because of which questions are sampled, which training seed produced the model, or which stochastic decoding draws were used. These are different sources of variation. Repeating generation many times for one question estimates behavior conditional on that question and model; it does not create many independent questions.

Similarly, evaluating one trained checkpoint on many cases does not quantify how much the training procedure varies across independently trained checkpoints. If that variation matters to the decision, the experiment needs a design that includes it. A single bootstrap over question rows cannot recover an unobserved distribution of training outcomes.

A practical report can state what is held fixed and what is varied. For example: the model checkpoint and decoding policy are fixed, while question families are resampled. Or: several independently initialized adapters are trained under the same protocol, each evaluated on the same families. The analysis should follow that design rather than applying one uncertainty calculation to every situation.

## Measure refusal and severe failures beside average quality

An assistant can reduce its error among answered questions by refusing more requests. Coverage shows the consequence. Appropriate refusals on unanswerable or unauthorized questions are valuable, while refusals on well-supported routine questions can reduce utility. Keep those categories separate so a candidate cannot appear universally reliable by avoiding difficult work.

Some failures also have decision rules that are not interchangeable with average quality. A required access boundary can be violated once even while a mean task score improves. The acceptance policy may treat that violation as a blocking condition. That is a declared engineering constraint, not a contradiction of the average's arithmetic.

Statistical uncertainty does not automatically cover measurement error. If a rubric systematically rewards confident unsupported explanations, a narrow confidence interval can precisely describe performance on the wrong target. Review disagreement cases, source-support labels and task coverage before interpreting precision as trustworthiness.

## Keep the final assessment outside development

Trying many prompt, retrieval and adapter configurations gives the team more opportunities to fit the development set. The best observed validation score can partly reflect selection noise. A final assessment that also guides later changes has joined the development process. The appropriate response is to record that use and obtain new independent evidence for a fresh final claim, rather than preserve the old test label while continuing to tune against it.

The output of the study should be a reproducible analytical artifact: paired case IDs, family definitions, weights, metrics, uncertainty method, failure categories and configuration identities. A generated narrative can explain that artifact, but it should not invent significance, change denominators or convert a system comparison into a causal claim about one component. This discipline becomes especially important when the next chapters begin updating model parameters.

## Design decisions and when to use this method

Use paired and family-aware analysis when multiple systems answer the same questions and the corpus contains related variants. Choose the resampling unit from the data-generation process, not from whichever choice produces a narrower interval. If the final population weights families unequally, declare and justify those weights before evaluation. Report absolute counts, error categories and uncertainty together.

Do not let an LLM write a statistical conclusion that contradicts the computed artifact. The report generator should consume named metrics and their assumptions, and a deterministic check should verify quoted counts and rates. A bootstrap interval is not a causal claim about why one system improved. Controlled ablations and study design are needed to attribute changes to retrieval, adaptation or prompting.

Choose the unit of independence from how cases were created. Related paraphrases, document revisions or questions from one account can share errors. Preserve that grouping before computing uncertainty, and state whether the deployment objective weights rows, families or a declared mix.

Separate a statistical comparison from acceptance gates. A favorable average loss difference can coexist with a prohibited access disclosure or an unacceptable unsupported-answer rate. Declare those constraints and the weighting policy before inspecting candidate results.

## Vocabulary and concepts

**Paired evaluation:** Comparing systems on the same identified cases.

**Family unit:** A group of related questions treated together for uncertainty.

**Bootstrap estimate:** A statistic calculated on a resampled set of observed units.

**Selective accuracy:** Accuracy among answered cases, reported beside coverage.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-013/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `python-core` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-013.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Join system error tables by question ID and reject unequal key sets. Compute errorA-errorB for each pair, aggregate within family, then sample family indices with one seeded NumPy generator. The same sampled family applies to both systems because the difference is already paired. Report the number of independent families, not only the number of paraphrases. Calculate answered accuracy and coverage with separate denominators.

## Derive the paired and family-level comparison

System A has errors[0, 0, 1] on q1, q2, q3; system B has[1, 1, 0] on the same IDs. Subtracting A minus B gives[-1, -1, 1], where negative favors A because smaller error is better. Sorting dictionary keys aligns identities. Pairing by insertion order would compare different questions and produce a statistic with no intended case-level meaning.

The row-weighted mean is(-1-1+1)/3=-1/3. If q1 and q2 are related variants of family F and q3 is family G, the family means are[-1, +1], whose equally weighted average is zero. This is not a disagreement between arithmetic implementations. The row estimand gives family F twice the weight, while the family estimand gives F and G equal weight.

The bootstrap draws two family indices with replacement. There are four equally likely ordered samples from the empirical family distribution:

| Resampled families | Mean difference | Probability |
| --- | --- | --- |
| F, F | -1 | 1/4 |
| F, G | 0 | 1/4 |
| G, F | 0 | 1/4 |
| G, G | +1 | 1/4 |

The exact bootstrap mean is zero and variance is 1/2. Its standard deviation is sqrt(1/2), about 0.7071. The 2000 seeded draws approximate this very coarse distribution; increasing the draw count only reduces Monte Carlo noise in that approximation. It does not create more than the two observed independent families or establish that those families represent the deployment population.

Pairing preserves the relationship between candidate errors. The variance identity Var(A-B)=Var(A)+Var(B)-2Cov(A, B) explains why independently resampling each candidate can change uncertainty. Family resampling must likewise keep all within-family candidate observations together. If question families have unequal intended population weights, specify the weighted estimator and a resampling design that matches it rather than selecting the narrowest interval after the fact.

Selective answering introduces more denominators. With ten questions, six answers and five correct answers, coverage is 6/10=0.6 and accuracy among answers is 5/6. Correct answers per all requests is 5/10. A system that answers only the easiest one correctly has conditional accuracy one but coverage 0.1. It may or may not be useful under the task's costs. Always retain how many refusals were appropriate and how many answerable cases were declined.

The saved errors here are teaching data. Their bootstrap computation is real arithmetic, but the arrays are not receipts from running a named model. A real comparison should preserve question IDs, predictions, rubric decisions, candidate configuration and family labels. Review label disagreements, because uncertainty over sampled questions does not automatically account for systematic rubric error.

### Interview reasoning with explanatory answers

**Why can more paraphrases make an interval look falsely precise?** Treating correlated variants as independent rows can overstate the effective evidence. Resampling at the relevant family level preserves that dependence under the chosen empirical design.

**Does a confidence interval establish why one candidate improved?** No. It describes variability of a statistic under assumptions. Attributing improvement to a changed component needs a controlled comparison or suitable causal design.

**Can a severe failure be averaged away?** Arithmetic can dilute it, but the acceptance contract need not permit that. A zero-access-leak requirement is a separate gate whose observed violation blocks release even if an average metric improves.

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

**Expected:** row mean-1/3; family mean 0.

### Example C: Resample paired families

Two families produce a coarse empirical distribution. A large number of bootstrap draws does not create additional independent evidence.

```python
indices=np.random.default_rng(17).integers(0,2,size=(2000,2)); estimates=family_values[indices].mean(1)
assert set(np.unique(estimates))=={-1.,0.,1.}
np.testing.assert_array_equal(indices,np.random.default_rng(17).integers(0,2,size=(2000,2)))
```

**Expected:** all estimates are-1, 0 or 1; repeatable with same seed.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: differences[-1, -1, 1] by sortedID. test-based selection rejected. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Align paired errors.** Use systemA errors q1=0, q2=0, q3=1 andB q1=1, q2=1, q3=0.
   **Expected:** differences[-1, -1, 1] by sortedID.
   **Verify:** Save the assertion results for exercise 1, including differences[-1, -1, 1] by sortedID.

2. **Aggregate by family.** Assignq 1, q2 tofamilyF andq 3 toG; compare row mean with family mean.
   **Expected:** row mean-1/3; family mean 0.
   **Verify:** Save the assertion results for exercise 2, including row mean-1/3; family mean 0.

3. **Resample paired families.** Draw 2000 bootstrap samples of the two family differences withseed 17.
   **Expected:** all estimates are-1, 0 or 1; repeatable with same seed.
   **Verify:** Save the assertion results for exercise 3, including all estimates are-1, 0 or 1; repeatable with same seed.

4. **Report coverage and answered accuracy.** For 10 questions, answer 6 with 5 correct and abstain on 4.
   **Expected:** coverage.6; answered accuracy 5/6; overall correct answers 5.
   **Verify:** Save the assertion results for exercise 4, including coverage.6; answered accuracy 5/6; overall correct answers 5.

5. **Block a severe boundary failure.** Combine a favorable mean comparison withone access leak and apply a zero-access-leak gate.
   **Expected:** release decision False.
   **Verify:** Save the assertion results for exercise 5, including release decision False.

6. **Keep final tests out of selection.** Record retriever selection onvalidation and final scoring ontest; flag a test-based parameter change.
   **Expected:** test-based selection rejected.
   **Verify:** Save the assertion results for exercise 6, including test-based selection rejected.

## Common pitfalls and diagnosis

If a comparison changes when dictionary order changes, repair identity alignment first. If repeating one family changes a supposedly family-weighted result, inspect aggregation and sampling units. If a bootstrap interval becomes narrow only after treating paraphrases as independent, revisit the dependence model.

If answered accuracy improves while users receive fewer useful responses, inspect coverage and refusal categories. If a report treats 2000 bootstrap draws as 2000 independent cases, correct the sample-size claim. If test cases influenced hyperparameter choices, record that selection and obtain untouched evidence for a new final claim.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Paired evaluation, Family unit, Bootstrap estimate using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

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
