# llm-applied-010: Query rewriting and bounded multi-hop retrieval

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-009`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Query rewriting can translate a user's phrasing into terms that a retriever understands. The central investigation is concrete: Rewritebuy rate usingbuy->purchase while preserving the original question. The finish condition is rewrittenpurchase rate; original unchanged. restricted document never appears. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Query rewriting can translate a user's phrasing into terms that a retriever understands. It can also distort intent, add unsupported assumptions or broaden the search beyond the authorized domain. A rewrite should be treated as a proposal with a provenance trail, not as a new trusted user instruction. Multi-hop retrieval performs another search using information found in an earlier result, useful when a question requires connecting a metric definition with an exclusion policy. Each hop should have a purpose, a bounded candidate count and a stopping rule.

This lesson uses a curated synonym map and a two-hop document graph. It does not ask a model to invent search plans. The deterministic baseline makes the failure modes visible: a rewrite can help lexical recall, but a cycle can repeatedly retrieve the same documents, and an unsupported bridge can lead to an irrelevant answer. Preserve the original question, each rewritten query, retrieved IDs and the reason for continuing. Authorization remains fixed across every hop.

## Design decisions and when to use this method

Use rewriting when relevance tests show a systematic vocabulary mismatch, and use multiple hops when the task genuinely needs linked evidence rather than one passage. Keep the original query as a retrieval branch so a bad rewrite does not erase exact identifiers. For a model-generated plan, validate each proposed query and link against the same scope and budget rules as any other input.

Do not add hops merely because the first result looks uncertain. More retrieved text can introduce contradictions and consume answer context. Evaluate whether each hop improves evidence recall or answer support on held-out question families. Record duplicate rate, total documents examined and termination reasons. A missing bridge should lead to an explicit incomplete-evidence answer, not an invented connection between unrelated documents.

## Vocabulary and concepts

**Query rewrite:** A transformed search query derived from an original question.

**Multi-hop retrieval:** A bounded sequence of searches or evidence-link traversals.

**Bridge evidence:** A source that justifies connecting one retrieval step to another.

**Stopping rule:** A condition ending retrieval before unbounded exploration.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-010/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-010.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-010.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Tokenize the query, apply only declared synonym substitutions and retain the original text in a trace. A bounded breadth-first traversal uses a queue, visited set and maximum-hop count. Follow only explicit local document links. The visited set prevents cycles from consuming the budget indefinitely. A new query or link cannot add an unauthorized document because the same admitted corpus is used throughout.

## Worked example / walkthrough

### Example A: Apply a controlled synonym rewrite

The substitution is explicitly authored. A learned rewrite would need evaluation for intent preservation and unsupported expansion.

```python
from collections import deque
def rewrite(query,synonyms): return ' '.join(synonyms.get(token,token) for token in query.lower().split())
def walk(start,graph,max_hops):
    if max_hops<0: raise ValueError('nonnegative hop budget required')
    if start not in graph: return []
    queue=deque([(start,0)]); seen={start}; result=[]
    while queue:
        node,depth=queue.popleft(); result.append(node)
        if depth==max_hops: continue
        for target in graph[node]:
            if target in graph and target not in seen: seen.add(target); queue.append((target,depth+1))
    return result
original='buy rate'; rewritten=rewrite(original,{'buy':'purchase'})
assert rewritten=='purchase rate' and original=='buy rate'
```

**Expected:** rewrittenpurchase rate; original unchanged.

### Example B: Retain a rewrite trace

A retrieval failure can originate in the rewrite rather than the ranking model. Keeping both strings makes that stage diagnosable.

```python
trace={'original':original,'rewritten':rewritten,'policy':'synonyms-v1'}
assert set(trace)=={'original','rewritten','policy'}
```

**Expected:** trace includes all three fields.

### Example C: Follow two evidence hops

The depth counts edges from the starting evidence item. The final document is included because it is exactly two links away.

```python
graph={'metric':['exclusions'],'exclusions':['test_accounts'],'test_accounts':[]}
assert walk('metric',graph,2)==['metric','exclusions','test_accounts']
```

**Expected:** visitedmetric, exclusions, test_accounts.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: rewrittenpurchase rate; original unchanged. restricted document never appears. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Apply a controlled synonym rewrite.** Rewritebuy rate usingbuy->purchase while preserving the original question.
   **Expected:** rewrittenpurchase rate; original unchanged.
   **Verify:** Save the assertion results for exercise 1, including rewrittenpurchase rate; original unchanged.

2. **Retain a rewrite trace.** Record the original, rewritten query and policy version.
   **Expected:** trace includes all three fields.
   **Verify:** Save the assertion results for exercise 2, including trace includes all three fields.

3. **Follow two evidence hops.** Use graphmetric->exclusions->test_accounts with a two-hop bound.
   **Expected:** visitedmetric, exclusions, test_accounts.
   **Verify:** Save the assertion results for exercise 3, including visitedmetric, exclusions, test_accounts.

4. **Stop at the declared depth.** Run the same graph with a one-hop bound.
   **Expected:** test_accounts is absent.
   **Verify:** Save the assertion results for exercise 4, including test_accounts is absent.

5. **Break a retrieval cycle.** Addtest_accounts->metric and traverse with a larger bound.
   **Expected:** each document appears once.
   **Verify:** Save the assertion results for exercise 5, including each document appears once.

6. **Preserve authorization across hops.** Remove a restricted target from the admitted graph and ensure links to it are not followed.
   **Expected:** restricted document never appears.
   **Verify:** Save the assertion results for exercise 6, including restricted document never appears.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Query rewrite, Multi-hop retrieval, Bridge evidence using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-009` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-010, Query rewriting and bounded multi-hop retrieval.
Read courses/llm-applied/guides/llm-applied-010.md and courses/llm-applied/lessons/llm-applied-010.py. Direct prerequisites: `llm-applied-009`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
