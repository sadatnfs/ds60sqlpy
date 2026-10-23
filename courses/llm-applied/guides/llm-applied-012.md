# llm-applied-012: Evaluating retrieval and answers with oracle controls

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-011`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A RAG evaluation should identify where the pipeline failed. The central investigation is concrete: Use relevant IDs a, c and retrieved b, c, a. The finish condition is recall1; reciprocal rank.5. duplicate ID detected. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A RAG evaluation should identify where the pipeline failed. Retrieval recall asks whether relevant evidence entered the candidate or context set. Ranking metrics ask how early it appeared. Answer correctness asks whether the response satisfies the question. Support asks whether its claims are established by supplied evidence. Appropriate abstention asks whether the system declined cases lacking evidence. These measurements can disagree, and combining them into one number too early hides actionable information.

An oracle-context control supplies the authored relevant evidence directly while leaving the question and answer rubric unchanged. If the answer improves, retrieval was a bottleneck. If it still fails, the answer stage or task definition needs attention. The local fixture uses saved deterministic answer labels, not fabricated model execution. Every result is keyed by question ID and linked to an authored relevance set. Questions with no relevant documents need a separate answerability category because recall has an empty denominator.

## Design decisions and when to use this method

Use a layered evaluation when choosing between retrievers, chunkers, rerankers or answer models. Freeze relevance labels and task rubrics before tuning. Include exact-match, paraphrase, multi-hop, unanswerable, stale and adversarial cases. Keep the context budget equal across candidates so a system does not win simply by receiving more evidence.

Do not rely exclusively on an unvalidated LLM judge. A judge can be useful for triage, but its disagreement with human or deterministic checks should be measured. Citation existence, JSON validity and fluent wording are weak proxies for support and correctness. Preserve representative failures and oracle controls in the report so a reviewer can see which engineering change is justified. Use independent question families for final assessment rather than many near-duplicate variants of the tuning examples.

## Vocabulary and concepts

**Retrieval recall:** Coverage of authored relevant evidence in retrieved results.

**Reciprocal rank:** Inverse position of the first relevant result.

**Oracle-context control:** Known relevant evidence supplied to isolate answer behavior.

**Failure taxonomy:** Separate named categories locating pipeline problems.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-012/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-012.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-012.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Recall@k is the number of relevant IDs retrieved divided by total relevant IDs. Reciprocal rank is1 divided by the first relevant rank, or0 when none appears. For unanswerable questions, returnNone for recall and score abstention separately. Keep retrieval misses, unsupported claims, incorrect answers and appropriate abstentions as distinct counters. Compare observed and oracle results by the same question ID.

## Worked example / walkthrough

### Example A: Calculate recall and reciprocal rank

Both relevant documents are retrieved, but the first appears second. Recall alone would not reveal that ordering.

```python

def retrieval_metrics(retrieved,relevant):
    if len(retrieved)!=len(set(retrieved)): raise ValueError('duplicate retrieved ID')
    recall=None if not relevant else len(set(retrieved)&relevant)/len(relevant)
    rank=next((i for i,key in enumerate(retrieved,1) if key in relevant),None)
    return recall,0. if rank is None else 1/rank
recall,rr=retrieval_metrics(['b','c','a'],{'a','c'})
assert recall==1 and rr==.5
```

**Expected:** recall1; reciprocal rank.5.

### Example B: Measure a retrieval miss

The answer stage cannot use evidence absent from its context. This is a retrieval failure even if a language model guesses the answer from prior training.

```python
assert retrieval_metrics(['b','c'],{'a'})==(0.,0.)
```

**Expected:** recall0; reciprocal rank 0.

### Example C: Handle an unanswerable question

A denominator of zero does not mean perfect recall. The correct task behavior is evaluated through an explicit answerability and abstention policy.

```python
assert retrieval_metrics(['b'],set())==(None,0.)
result={'question':'q-missing','answerable':False,'abstained':True}; assert not result['answerable'] and result['abstained']
```

**Expected:** recallNone; appropriate abstentionTrue.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: recall1; reciprocal rank.5. duplicate ID detected. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Calculate recall and reciprocal rank.** Use relevant IDs a, c and retrieved b, c, a.
   **Expected:** recall1; reciprocal rank.5.
   **Verify:** Save the assertion results for exercise 1, including recall1; reciprocal rank.5.

2. **Measure a retrieval miss.** Use relevant a and retrieved b, c.
   **Expected:** recall0; reciprocal rank 0.
   **Verify:** Save the assertion results for exercise 2, including recall0; reciprocal rank 0.

3. **Handle an unanswerable question.** Use an empty relevant set and a saved abstention result.
   **Expected:** recallNone; appropriate abstentionTrue.
   **Verify:** Save the assertion results for exercise 3, including recallNone; appropriate abstentionTrue.

4. **Separate support from correctness.** Record a correct-looking answer whose cited context does not support it.
   **Expected:** correctTrue but supportedFalse.
   **Verify:** Save the assertion results for exercise 4, including correctTrue but supportedFalse.

5. **Apply an oracle-context control.** Compare q1 observed incorrect with oracle-context correct under the same rubric.
   **Expected:** paired improvement1 for q1.
   **Verify:** Save the assertion results for exercise 5, including paired improvement1 for q1.

6. **Reject duplicate result identities.** Validate one score row per question and inject a duplicateq1.
   **Expected:** duplicate ID detected.
   **Verify:** Save the assertion results for exercise 6, including duplicate ID detected.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Retrieval recall, Reciprocal rank, Oracle-context control using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-011` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-012, Evaluating retrieval and answers with oracle controls.
Read courses/llm-applied/guides/llm-applied-012.md and courses/llm-applied/lessons/llm-applied-012.py. Direct prerequisites: `llm-applied-011`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
