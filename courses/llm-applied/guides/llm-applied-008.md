# llm-applied-008: Hybrid retrieval, reciprocal-rank fusion and reranking

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-007`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Hybrid retrieval combines complementary candidate generators. The central investigation is concrete: Fuse lexical[a, b, c] and dense[b, d, a] with constant60. The finish condition is b ranks first, a second. ValueError for nonpositive constant; TypeError for non-string ID. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Hybrid retrieval combines complementary candidate generators. Lexical ranking can preserve exact terms, while embedding ranking can recover paraphrases. Their raw scores are usually on different scales, so adding them without calibration can let one dominate for arbitrary numerical reasons. Reciprocal-rank fusion uses rank positions instead: each list contributes1/(constant+rank) to a candidate. A document appearing near the top of both lists accumulates evidence from both methods. This is a ranking heuristic, not a probability model.

Reranking evaluates a smaller candidate set with a more expensive scoring function, often a cross-encoder that jointly reads query and document. This lesson uses a transparent deterministic relevance feature as a reranker so the candidate-stage limitation is visible. If a relevant document never enters the candidate set, no reranker can recover it. Measure candidate recall before judging reranker quality, and keep the query, candidate IDs, scores and final order in the evaluation trace.

## Design decisions and when to use this method

Use fusion when error analysis shows complementary retrieval strengths, and test whether the additional complexity improves held-out evidence coverage. A reranker is useful when the first-stage candidate set has good recall but poor ordering. Its compute cost grows with candidate count and input length, so measure quality against a fixed latency or work budget.

Do not compare a hybrid system withk100 against a lexical baseline withk5 and attribute all improvement to the model. Hold candidate and context budgets explicit. Raw-score normalization is another possible design, but it needs calibration evidence. RRF avoids raw-scale assumptions at the cost of discarding score gaps: a narrow first-place lead and an overwhelming lead receive the same rank contribution. Record that tradeoff rather than calling fusion universally optimal.

## Vocabulary and concepts

**Hybrid retrieval:** Combining candidate rankings from different retrieval mechanisms.

**RRF:** Reciprocal-rank fusion, combining inverse rank contributions.

**Reranker:** A second-stage scorer applied to a bounded candidate set.

**Candidate recall:** Relevant evidence coverage before reranking.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-008/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-008.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-008.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use one-based ranks and a positive fusion constant. Deduplicate each input ranking before assigning contributions so repeated IDs do not gain extra votes. Sum contributions by document ID and sort with an explicit ID tie-breaker. The reranker receives only admitted candidates and returns a new ordering; it must not expand access scope or silently fetch new documents.

## Worked example / walkthrough

### Example A: Fuse two rankings

Documentb receives ranks2 and1, whilea receives1 and3. The difference comes from rank evidence rather than incompatible raw score scales.

```python
from collections import defaultdict
def rrf(rankings,constant=60):
    if constant<=0: raise ValueError('positive fusion constant required')
    scores=defaultdict(float)
    for ranking in rankings:
        unique=[]; seen=set()
        for key in ranking:
            if not isinstance(key,str): raise TypeError('string document ID required')
            if key not in seen: unique.append(key); seen.add(key)
        for position,key in enumerate(unique,1): scores[key]+=1/(constant+position)
    return sorted(scores.items(),key=lambda row:(-row[1],row[0]))
ranked=rrf([['a','b','c'],['b','d','a']],60)
assert [key for key,score in ranked][:2]==['b','a']
```

**Expected:** b ranks first, a second.

### Example B: Inspect one exact contribution

Writing the formula independently makes off-by-one rank errors visible. Zero-based rank would change every denominator.

```python
scores=dict(ranked)
assert abs(scores['b']-(1/62+1/61))<1e-12
```

**Expected:** computed b score equals that sum within1e-12.

### Example C: Prevent duplicate votes

One retrieval list should contribute one rank per document. Otherwise a buggy candidate generator can inflate a result by emitting duplicates.

```python
assert rrf([['a','b','b','c']],60)==rrf([['a','b','c']],60)
```

**Expected:** fusion result unchanged.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: b ranks first, a second. ValueError for nonpositive constant; TypeError for non-string ID. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Fuse two rankings.** Fuse lexical[a, b, c] and dense[b, d, a] with constant60.
   **Expected:** b ranks first, a second.
   **Verify:** Save the assertion results for exercise 1, including b ranks first, a second.

2. **Inspect one exact contribution.** Calculate the fused score ofb as1/62+1/61.
   **Expected:** computed b score equals that sum within1e-12.
   **Verify:** Save the assertion results for exercise 2, including computed b score equals that sum within1e-12.

3. **Prevent duplicate votes.** Repeatb inside one ranking and compare with its deduplicated form.
   **Expected:** fusion result unchanged.
   **Verify:** Save the assertion results for exercise 3, including fusion result unchanged.

4. **Rerank a bounded candidate set.** Use candidatesa, b, c with authored relevance features0, 2, 1 and sort descending feature then ID.
   **Expected:** orderb, c, a.
   **Verify:** Save the assertion results for exercise 4, including orderb, c, a.

5. **Expose a candidate-recall ceiling.** Declare relevant documentd but supply only candidatesa, b, c.
   **Expected:** candidate recall0 and reranker cannot return d.
   **Verify:** Save the assertion results for exercise 5, including candidate recall0 and reranker cannot return d.

6. **Reject invalid fusion policy.** Use constant0 or a repeated non-string identifier and apply the declared validation.
   **Expected:** ValueError for nonpositive constant; TypeError for non-string ID.
   **Verify:** Save the assertion results for exercise 6, including ValueError for nonpositive constant; TypeError for non-string ID.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Hybrid retrieval, RRF, Reranker using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-007` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-008, Hybrid retrieval, reciprocal-rank fusion and reranking.
Read courses/llm-applied/guides/llm-applied-008.md and courses/llm-applied/lessons/llm-applied-008.py. Direct prerequisites: `llm-applied-007`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
