# llm-applied-023: Domain assistant boundaries: freshness, injection, budgets and traces

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-022`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A production-oriented domain assistant needs controls around the model as well as a good prompt. The central investigation is concrete: Use fixedUTCnow2026-10-22 and a document published one day earlier under a two-day limit. The finish condition is freshTrue. answer admissionFalse; reasonstale evidence. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A production-oriented domain assistant needs controls around the model as well as a good prompt. Evidence can become stale, access can change, caches can outlive their source version, and tool proposals can exceed work budgets. Observability should explain which stage failed without logging secrets or unrestricted source text. A trace can record request ID, policy fingerprint, corpus/index/model versions, admitted document IDs, tool counts and named failure categories. It should not become a second unprotected corpus.

This lesson implements deterministic freshness and budget checks using an injected clock. No server, deployment or live identity integration is started. A timestamp comparison establishes whether a document meets the declared freshness window; it does not prove the source is correct. A call counter enforces a bounded operation budget; it does not substitute for actual process timeouts in a serving system. Hostile text remains data under the same access and tool policies established earlier. The goal is to make each boundary and its evidence explicit before scaling the assistant.

## Design decisions and when to use this method

Use explicit boundary tests before exposing an assistant to real users or sensitive sources. Test access revocation, corpus updates, stale indexes, cache partitioning, malformed tool output, timeout and partial failure. An application should return a named failure or abstention rather than quietly substituting old evidence. Define what logs retain, who can read them and how long they remain available.

Do not call these local checks a production acceptance test. This fixture does not exercise a real authentication provider, network timeout, distributed cache or incident response. Those need separate integration and operational evidence. The useful contribution here is a concrete contract and deterministic failure cases that a real service can preserve. Measure latency, token use, tool calls and quality together, with privacy-aware traces that explain which boundary stopped the request.

## Vocabulary and concepts

**Freshness policy:** A declared maximum age for evidence under a task contract.

**Injected clock:** A supplied time value making temporal behavior deterministic in tests.

**Work budget:** A maximum number of admitted operations before refusal.

**Safe trace:** Diagnostic metadata selected without copying sensitive content.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-023/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-023.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-023.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use timezone-aware UTC datetimes and reject naive timestamps. Compareage=now-published with a nonnegative maximum age, also rejecting future publication times. A Budget object increments only for admitted operations and raises before exceeding its limit. Cache identity includes policy and corpus versions. Trace construction uses an allowlist of metadata fields and excludes source text, credentials and raw private queries.

## Worked example / walkthrough

### Example A: Check evidence freshness

The clock is supplied rather than read globally, so the test is reproducible. The result concerns the declared age policy, not the truth of the content.

```python
from datetime import datetime,timedelta,timezone
def fresh(published,now,maximum_age):
    if published.tzinfo is None or now.tzinfo is None or published.utcoffset() is None or now.utcoffset() is None: raise ValueError('aware timestamps required')
    if maximum_age<timedelta(0): raise ValueError('nonnegative age limit')
    age=now-published
    return timedelta(0)<=age<=maximum_age
class Budget:
    def __init__(self,limit):
        if type(limit) is not int or limit<0: raise ValueError('nonnegative integer limit')
        self.limit=limit; self.used=0
    def consume(self):
        if self.used>=self.limit: raise RuntimeError('operation budget exhausted')
        self.used+=1
def trace_record(value):
    return {key:value[key] for key in ['request_id','corpus_version','policy','result']}
now=datetime(2026,10,22,tzinfo=timezone.utc); published=now-timedelta(days=1)
assert fresh(published,now,timedelta(days=2))
```

**Expected:** freshTrue.

### Example B: Reject stale and future evidence

Future timestamps can indicate clock or metadata errors. Accepting them as indefinitely fresh would conceal that data-quality problem.

```python
assert not fresh(now-timedelta(days=3),now,timedelta(days=2))
assert not fresh(now+timedelta(hours=1),now,timedelta(days=2))
```

**Expected:** both fail freshness admission.

### Example C: Enforce a three-call budget

The failing request does not perform work first and report the overrun afterward. Real execution also needs bounded duration and cancellation, which this counter does not implement.

```python
budget=Budget(3)
for _ in range(3): budget.consume()
try: budget.consume()
except RuntimeError: pass
else: raise AssertionError('budget exceeded')
assert budget.used==3
```

**Expected:** used3; fourth raisesRuntimeError before increment.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: freshTrue. answer admissionFalse; reasonstale evidence. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Check evidence freshness.** Use fixedUTCnow2026-10-22 and a document published one day earlier under a two-day limit.
   **Expected:** freshTrue.
   **Verify:** Save the assertion results for exercise 1, including freshTrue.

2. **Reject stale and future evidence.** Test a three-day-old document and a document dated one hour in the future.
   **Expected:** both fail freshness admission.
   **Verify:** Save the assertion results for exercise 2, including both fail freshness admission.

3. **Enforce a three-call budget.** Consume exactly3 operations, then attempt a fourth.
   **Expected:** used3; fourth raisesRuntimeError before increment.
   **Verify:** Save the assertion results for exercise 3, including used3; fourth raisesRuntimeError before increment.

4. **Reject naive timestamp assumptions.** Pass a datetime without timezone information.
   **Expected:** ValueError.
   **Verify:** Save the assertion results for exercise 4, including ValueError.

5. **Build an allowlisted trace.** Create a trace from metadata plussecret/source_text fields and inspect the output.
   **Expected:** only request_id, corpus_version, policy, result fields retained.
   **Verify:** Save the assertion results for exercise 5, including only request_id, corpus_version, policy, result fields retained.

6. **Make stale evidence produce abstention.** Combine authorizedTrue withfreshFalse and require both before answering.
   **Expected:** answer admissionFalse; reasonstale evidence.
   **Verify:** Save the assertion results for exercise 6, including answer admissionFalse; reasonstale evidence.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Freshness policy, Injected clock, Work budget using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-022` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Python datetime documentation](https://docs.python.org/3.12/library/datetime.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-023, Domain assistant boundaries: freshness, injection, budgets and traces.
Read courses/llm-applied/guides/llm-applied-023.md and courses/llm-applied/lessons/llm-applied-023.py. Direct prerequisites: `llm-applied-022`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
