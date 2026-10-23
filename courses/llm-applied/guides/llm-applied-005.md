# llm-applied-005: Chunking, overlap, offsets and context budgets

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Beginner; approximately 180 minutes. Direct prerequisites: `llm-applied-004`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Chunking divides documents into retrieval units. The central investigation is concrete: Chunk one two three four five six seven with size 3 and overlap 1. The finish condition is chunks one two three, three four five and five six seven. empty list for empty text; one short chunk for the two-token source. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Chunking divides documents into retrieval units. Small chunks can isolate relevant facts but lose context; large chunks preserve context but consume more budget and may dilute lexical or embedding signals. Overlap repeats boundary text so a fact crossing a split is less likely to disappear, but it also creates duplicate evidence and additional storage. Preserve source offsets so a retrieved chunk can cite the exact original span. Chunk identity should include document version and chunk boundaries, not just its ordinal position in a list.

The default splitter uses whitespace tokens only as a transparent fixture. Actual language-model tokenization may split a word into several tokens and add chat-template markers, so its counts must be measured with the intended tokenizer. A chunker should reject impossible overlap settings and handle an empty document deliberately. Evaluation should include facts at boundaries, repeated headings and documents whose key definition depends on an earlier section. No single chunk size is universally optimal; choose it through task-specific retrieval and answer evaluation.

## Design decisions and when to use this method

Use sentence, paragraph or structure-aware chunks when the task depends on complete definitions, tables or procedure steps. Preserve headings and document metadata as separate context rather than blindly repeating them into every embedding. For tables, a row alone may lose column meanings; a chunk needs enough schema context to interpret its values. For code or formulas, splitting at arbitrary whitespace can destroy syntax or assumptions.

Evaluate chunk policies on authored boundary questions. Measure retrieval recall, citation fidelity, duplicate rate, answer support and context consumption together. A policy that increases recall by returning many near-duplicate chunks may leave less room for other necessary evidence. Do not tune chunk size on the final test set. Record splitter version and tokenization policy so rebuilding an index does not silently change the experiment.

## Vocabulary and concepts

**Chunk:** A bounded source span used as a retrieval unit.

**Overlap:** Repeated boundary material shared by adjacent chunks.

**Source offset:** A character boundary in the original document.

**Context budget:** The allowed amount of material supplied to an answerer.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-005/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-005.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-005.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

re.finditer over non-whitespace spans records exact start/end offsets in the original text. A window ofsize tokens advances bysize-overlap. The chunk text is sliced from the first token start to the last token end, preserving internal whitespace. Each output recordsdocument_id, version, start, end, text. Validate0<=overlap<size before looping so a zero or negative step cannot hang the process.

## Worked example / walkthrough

### Example A: Split a fixed document

The step is two tokens, so each adjacent pair shares one token. The final full window reaches the document end without creating a duplicate tail chunk.

```python
import re
def chunk(text,document_id,version,size,overlap):
    if type(size) is not int or type(overlap) is not int or size<=0 or not 0<=overlap<size: raise ValueError('0<=overlap<size required')
    spans=list(re.finditer(r'\S+',text)); result=[]; step=size-overlap
    for begin in range(0,len(spans),step):
        end=min(begin+size,len(spans)); start_char=spans[begin].start(); end_char=spans[end-1].end()
        result.append({'document_id':document_id,'version':version,'start':start_char,'end':end_char,'text':text[start_char:end_char]})
        if end==len(spans): break
    return result
text='one two three four five six seven'; chunks=chunk(text,'d',1,3,1)
assert [c['text'] for c in chunks]==['one two three','three four five','five six seven']
```

**Expected:** chunks one two three, three four five and five six seven.

### Example B: Verify citation offsets

Offsets remain meaningful only relative to the exact source version. Reconstructing chunk text with join could normalize whitespace and break this equality.

```python
assert all(text[c['start']:c['end']]==c['text'] for c in chunks)
assert chunks[1]['start']==text.index('three')
```

**Expected:** every source slice equals the stored chunk text.

### Example C: Preserve unusual whitespace

The splitter counts token spans but retains original characters inside the chunk. Citation fidelity and tokenization are separate concerns.

```python
odd='alpha  beta\ngamma'; pieces=chunk(odd,'odd',2,2,0)
assert pieces[0]['text']=='alpha  beta' and pieces[1]['text']=='gamma'
```

**Expected:** first chunk retains the double space; second chunk is gamma.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: chunks one two three, three four five and five six seven. empty list for empty text; one short chunk for the two-token source. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Split a fixed document.** Chunk one two three four five six seven with size 3 and overlap 1.
   **Expected:** chunks one two three, three four five and five six seven.
   **Verify:** Save the assertion results for exercise 1, including chunks one two three, three four five and five six seven.

2. **Verify citation offsets.** For every chunk, slice the original text using its start and end offsets.
   **Expected:** every source slice equals the stored chunk text.
   **Verify:** Save the assertion results for exercise 2, including every source slice equals the stored chunk text.

3. **Preserve unusual whitespace.** Chunk alpha, two spaces, beta, a newline and gamma with size 2 and overlap 0.
   **Expected:** first chunk retains the double space; second chunk is gamma.
   **Verify:** Save the assertion results for exercise 3, including first chunk retains the double space; second chunk is gamma.

4. **Measure overlap duplication.** Count total stored chunk token occurrences versus original source token positions in the first fixture.
   **Expected:** 9 stored token occurrences versus7 source positions.
   **Verify:** Save the assertion results for exercise 4, including 9 stored token occurrences versus7 source positions.

5. **Reject invalid policies.** Try overlap equal to window size, negative overlap and size 0.
   **Expected:** all policies raise ValueError before iteration.
   **Verify:** Save the assertion results for exercise 5, including all policies raise ValueError before iteration.

6. **Handle empty and short sources.** Chunk empty text and a two-token string with size 5.
   **Expected:** empty list for empty text; one short chunk for the two-token source.
   **Verify:** Save the assertion results for exercise 6, including empty list for empty text; one short chunk for the two-token source.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Chunk, Overlap, Source offset using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-004` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-005, Chunking, overlap, offsets and context budgets.
Read courses/llm-applied/guides/llm-applied-005.md and courses/llm-applied/lessons/llm-applied-005.py. Direct prerequisites: `llm-applied-004`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
