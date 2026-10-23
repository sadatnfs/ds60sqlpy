# llm-applied-007: Embedding retrieval, similarity and representation limits

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-006`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Embedding retrieval maps queries and documents to vectors and compares their geometry. The central investigation is concrete: Use query[1, 0, 0] and documents purchase[1, .1, 0], geometry[0, 1, 0], mixed[.5, .5, 0]. The finish condition is purchase ranks first, mixed second, geometry last. top-ranked IDwrong is outside the authored relevant set. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Embedding retrieval maps queries and documents to vectors and compares their geometry. A learned embedding model can place related wording near each other, but that behavior depends on its training objective and domain coverage. A vector is not an explanation or a probability that a document answers a question. Cosine similarity compares direction after dividing by vector norms; a dot product also depends on magnitude. The choice affects rankings unless all vectors are normalized consistently.

This lesson uses a literal three-dimensional table whose axes are explicitly described as topic features. It demonstrates retrieval arithmetic and its limits without pretending that the fixed table is a pretrained semantic model. The synonym relation between purchase and buy is encoded by hand so you can see exactly where that knowledge enters. A real embedding system needs a pinned model revision, a consistent query/document encoding policy, domain relevance labels and evaluation against lexical retrieval. Zero vectors and incompatible dimensions should fail clearly rather than silently produce NaNs.

## Design decisions and when to use this method

Use embedding retrieval when paraphrases and semantic relationships matter, but retain lexical baselines for rare terms, identifiers and exact phrases. Evaluate query and document encoding conventions separately: some models require different prefixes or instructions for each role. Normalize only when the model documentation and chosen similarity metric call for it. Store encoder revision, tokenizer revision, pooling strategy and vector dimension with the index.

Do not interpret a cosine score as calibrated relevance probability. Scores can cluster tightly or shift across domains, and a threshold chosen on one corpus may not transfer. Domain adaptation can improve useful relationships while degrading others, so evaluate held-out query families and exact-identifier cases after fine-tuning. The actual embedding and reranker training lesson later in this track updates a small model and measures its held-out behavior; this chapter establishes the geometry and failure vocabulary first.

## Vocabulary and concepts

**Embedding:** A vector representation produced by a specified mapping.

**Cosine similarity:** The dot product of unit-normalized vectors.

**Embedding space:** The coordinate system defined by one model and preprocessing policy.

**Semantic retrieval:** Retrieval intended to match meaning rather than exact shared terms.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-007/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-007.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-007.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Convert vectors to a float64 matrix with documents on rows and features on columns. Divide each row by its norm, rejecting zero or nonfinite norms. Normalize the query with the same convention, then matrix-multiply document rows by the query. Sort by descending score and stable document ID. Keep model identity and preprocessing policy with the index, because equal vector dimensions do not make two embedding spaces compatible.

## Worked example / walkthrough

### Example A: Rank fixed topic vectors

The ranking follows the declared topic geometry. The fixture does not demonstrate that a learned model will assign these vectors to arbitrary language.

```python
import numpy as np
def unit(value):
    value=np.asarray(value,dtype=np.float64)
    if value.ndim!=1 or not len(value) or not np.isfinite(value).all(): raise ValueError('finite vector required')
    norm=np.linalg.norm(value)
    if norm==0 or not np.isfinite(norm): raise ValueError('nonzero finite norm required')
    return value/norm
def cosine_rank(query,documents):
    q=unit(query); scores=[]
    for key,value in documents.items():
        v=unit(value)
        if v.shape!=q.shape: raise ValueError('embedding dimensions differ')
        scores.append((key,float(q@v)))
    return sorted(scores,key=lambda row:(-row[1],row[0]))
table={'purchase':np.array([1.,.1,0.]),'geometry':np.array([0.,1.,0.]),'mixed':np.array([.5,.5,0.])}
ranked=cosine_rank(np.array([1.,0.,0.]),table)
assert [key for key,score in ranked]==['purchase','mixed','geometry']
```

**Expected:** purchase ranks first, mixed second, geometry last.

### Example B: Separate cosine from magnitude

Normalization removes positive magnitude scaling from the score. A model trained for unnormalized dot products may use magnitude meaningfully, so the scoring convention must match the model contract.

```python
query=np.array([1.,0.,0.]); original=table['purchase']; scaled=10*original
np.testing.assert_allclose(unit(original)@unit(query),unit(scaled)@unit(query),atol=1e-12,rtol=0)
assert scaled@query==10*(original@query)
```

**Expected:** cosine unchanged within1e-12; raw dot product multiplies by 10.

### Example C: Expose hand-authored synonym knowledge

The semantic relation was supplied by the fixture author. A pretrained encoder would need to learn or represent it, and a domain-specific synonym may still be missed.

```python
word_vectors={'buy':np.array([1.,0.,0.]),'purchase':np.array([1.,0.,0.])}
assert set('buy'.split())&set('purchase'.split())==set()
np.testing.assert_array_equal(word_vectors['buy'],word_vectors['purchase'])
```

**Expected:** vector scores match; literal word overlap is empty.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: purchase ranks first, mixed second, geometry last. top-ranked IDwrong is outside the authored relevant set. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Rank fixed topic vectors.** Use query[1, 0, 0] and documents purchase[1, .1, 0], geometry[0, 1, 0], mixed[.5, .5, 0].
   **Expected:** purchase ranks first, mixed second, geometry last.
   **Verify:** Save the assertion results for exercise 1, including purchase ranks first, mixed second, geometry last.

2. **Separate cosine from magnitude.** Scale the purchase vector by 10 and compare its cosine score with the original.
   **Expected:** cosine unchanged within1e-12; raw dot product multiplies by 10.
   **Verify:** Save the assertion results for exercise 2, including cosine unchanged within1e-12; raw dot product multiplies by 10.

3. **Expose hand-authored synonym knowledge.** Assign buy the same literal vector as purchase and compare retrieval with an exact-token overlap baseline.
   **Expected:** vector scores match; literal word overlap is empty.
   **Verify:** Save the assertion results for exercise 3, including vector scores match; literal word overlap is empty.

4. **Reject zero and nonfinite vectors.** Normalize[0, 0] and[1, NaN] through the checked helper.
   **Expected:** both raise ValueError.
   **Verify:** Save the assertion results for exercise 4, including both raise ValueError.

5. **Reject incompatible spaces.** Compare query metadata modelA with an index encoded by modelB, even when both have width3.
   **Expected:** space identity mismatch blocks retrieval.
   **Verify:** Save the assertion results for exercise 5, including space identity mismatch blocks retrieval.

6. **Measure a domain failure.** Give an irrelevant document a high-scoring vector and record that geometric rank does not establish relevance.
   **Expected:** top-ranked IDwrong is outside the authored relevant set.
   **Verify:** Save the assertion results for exercise 6, including top-ranked IDwrong is outside the authored relevant set.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Embedding, Cosine similarity, Embedding space using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-006` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Sentence-BERT](https://arxiv.org/abs/1908.10084), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-007, Embedding retrieval, similarity and representation limits.
Read courses/llm-applied/guides/llm-applied-007.md and courses/llm-applied/lessons/llm-applied-007.py. Direct prerequisites: `llm-applied-006`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
