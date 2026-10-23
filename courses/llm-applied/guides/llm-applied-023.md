# llm-applied-023: Domain assistant boundaries: freshness, injection, budgets and traces

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-022`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A useful assistant must preserve its evidence contract while time, permissions and runtime conditions change. This chapter follows failures through a request lifecycle and explains how freshness, work budgets, cancellation and observability support reliable behavior beyond a successful model call.

## Purpose and mental model

A production-oriented domain assistant needs controls around the model as well as a good prompt. Evidence can become stale, access can change, caches can outlive their source version, and tool proposals can exceed work budgets. Observability should explain which stage failed without logging secrets or unrestricted source text. A trace can record request ID, policy fingerprint, corpus/index/model versions, admitted document IDs, tool counts and named failure categories. It should not become a second unprotected corpus.

This lesson implements deterministic freshness and budget checks using an injected clock. No server, deployment or live identity integration is started. A timestamp comparison establishes whether a document meets the declared freshness window; it does not prove the source is correct. A call counter enforces a bounded operation budget; it does not substitute for actual process timeouts in a serving system. Hostile text remains data under the same access and tool policies established earlier. The goal is to make each boundary and its evidence explicit before scaling the assistant.

## Follow one request through changing system state

Consider a serving design for the Methods Desk. A request is admitted under a principal's policy, retrieves an applicable handbook version, obtains a validated calculation, checks the proposed answer and returns it. Each transition should produce enough information to explain what happened. The local code below exercises only a few of those boundaries: time admission, a call counter and selected trace fields.

A failure should remain attached to its stage. Missing evidence is different from a retriever timeout. A denied source is different from an empty public corpus. A valid tool request whose computation failed is different from an unsupported operation. These distinctions help an operator repair the system and help the analyst understand what can be concluded from a partial result.

The outward explanation may be less detailed than the internal trace when disclosure policy requires it. A public response should not reveal restricted document identities simply to explain why it could not answer. The system can preserve a precise internal category without copying sensitive content into a broadly visible log or user message.

## Freshness is a policy over the relevant kind of time

The chapter's age rule compares a source publication time with an injected UTC now. It is useful because the exact boundary can be tested: at the maximum permitted age, a source is admitted; just beyond it, it is not. Future timestamps fail rather than becoming evidence that is indefinitely fresh.

A real question may need a different temporal interpretation. Publication, effective date, ingestion, last verification and data-event time describe different facts. A recently downloaded old policy is not necessarily current. A historical question may legitimately require an old source. The application should identify which time field its freshness or applicability rule uses.

Requests also take time to execute. A source can change between retrieval and response release. One policy may pin a consistent snapshot for the duration of a request; another may require revalidation before answering a current-policy question. Neither behavior is supplied automatically by a timestamp comparison. The serving contract must state how it handles such changes and keep the relevant versions in the result.

## A resource budget has several dimensions

The local Budget counter limits admitted operations. It cannot bound the time taken by one operation, the size of its result or the amount of model context it creates. A fuller design may track tool calls, retrieved documents, tokens, bytes and elapsed time separately. Those budgets should be charged at the points where resources are committed, with clear behavior for failure and retry.

For a serial pipeline, stage latencies add. Two independent retrieval branches that truly run in parallel can instead contribute approximately the larger branch latency plus coordination overhead, while still consuming the work of both branches. This distinction explains why latency and total resource cost can move differently. Actual scheduling, contention and backend behavior require measurement; the arithmetic is a planning model.

A deadline should propagate through the stages that can consume it. Starting a long model call when almost no request budget remains may guarantee a timeout after expensive work has already begun. Cancellation also needs an observed lifecycle: a request that is no longer useful should not leave unbounded background work merely because the caller stopped waiting.

The call-counter example intentionally counts an admitted attempt before the operation. If that operation fails, the attempt has consumed budget. A retry policy that refunds every failure can create an unbounded loop; a policy that never retries can reduce completion unnecessarily. Decide which failures are retryable and whether the previous attempt may have produced a side effect. A pure in-memory calculation is simpler than a remote mutating operation, so their recovery contracts should not be conflated.

## Make traces useful without turning them into another corpus

A diagnostic record can identify request, policy, corpus/index/model versions, admitted source IDs, operation counts, durations and a named result. Those fields help locate whether an incident came from stale data, a policy change, a timeout, a numerical failure or an unsupported answer. Raw private queries and unrestricted source bodies are not always needed to make that diagnosis.

A field-name allowlist is only a beginning. If the allowed request_id value contains a private query, the key is approved while the content still violates the intended trace contract. Values need their own types, length bounds and permitted categories, and the trace store needs an access and retention policy. The tiny helper demonstrates omission of certain keys, not a complete privacy-preserving logging service.

Quality monitoring also needs labels appropriate to the claim. A rising average retrieval score does not establish that answers became more correct. A lower refusal rate can indicate improved evidence coverage or more unsupported answering. A model or corpus fingerprint change can identify when behavior shifted, but it does not explain the cause without representative failure examples and evaluation.

## Repair incidents through the evidence chain

If a current-definition answer uses an old policy, compare the source snapshot, index build and cache identity. If a valid calculation is misquoted, inspect the result-to-explanation interface. If a request exceeds its budget, inspect retries and cancellation rather than only the final timeout message. If a model follows an instruction embedded in evidence, inspect both model behavior and whether the application allowed any unauthorized operation to proceed.

An incident can become a useful development case, but doing so changes the evaluation history. If its answer or failure label is used to revise a prompt or training dataset, it belongs to development from then on. Preserve independent cases for a fresh assessment. The final chapter brings these ideas together into a reviewable assistant design while keeping the course's actual executed baseline distinct from the larger system it motivates.

## Design decisions and when to use this method

Use explicit boundary tests before exposing an assistant to real users or sensitive sources. Test access revocation, corpus updates, stale indexes, cache partitioning, malformed tool output, timeout and partial failure. An application should return a named failure or abstention rather than quietly substituting old evidence. Define what logs retain, who can read them and how long they remain available.

Do not call these local checks a production acceptance test. This fixture does not exercise a real authentication provider, network timeout, distributed cache or incident response. Those need separate integration and operational evidence. The useful contribution here is a concrete contract and deterministic failure cases that a real service can preserve. Measure latency, token use, tool calls and quality together, with privacy-aware traces that explain which boundary stopped the request.

Specify operational policies as measurable contracts around the model: admissible evidence age, access identity, maximum admitted work, cancellation, failure categories and trace schema. Keep their implementation evidence separate from a successful local model call.

Use an injected UTC clock for deterministic freshness checks. Publication time, effective time, ingestion time and last verification time can answer different questions. A maximum publication age is one policy; it should not silently stand in for all of them.

## Vocabulary and concepts

**Freshness policy:** A declared maximum age for evidence under a task contract.

**Injected clock:** A supplied time value making temporal behavior deterministic in tests.

**Work budget:** A maximum number of admitted operations before refusal.

**Safe trace:** Diagnostic metadata selected without copying sensitive content.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-023/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `python-core` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-023.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use timezone-aware UTC datetimes and reject naive timestamps. Compareage=now-published with a nonnegative maximum age, also rejecting future publication times. A Budget object increments only for admitted operations and raises before exceeding its limit. Cache identity includes policy and corpus versions. Trace construction uses an allowlist of metadata fields and excludes source text, credentials and raw private queries.

## Trace temporal admission, work consumption and diagnosis

The freshness helper computes age=now-published and accepts 0<=age<=maximum_age. Both boundaries are inclusive. At a two-day limit, a source exactly two days old is admitted; a source two days plus one microsecond old is not. A future publication has negative age and fails rather than remaining perpetually fresh. These comparisons implement a chosen policy, not a test that the document is factually correct.

The supplied fixtures use timezone-aware UTC datetimes. Rejection of naive timestamps prevents one obvious ambiguity, but a complete real-time interface also needs normalization and a policy for source clocks. Civil-time transitions and ambiguous local timestamps deserve separate tests if non-UTC input is supported. An aware timestamp alone should not be described as a complete clock-quality guarantee.

Different temporal fields should remain distinguishable. A policy may be published yesterday but effective next month, or discovered today after applying for weeks. A current answer might require both applicability and a recent verification event. A historical answer might intentionally use an old source that was effective at the event time. The simple published-age gate cannot decide those cases without additional metadata.

The Budget object starts with used=0. Three consume calls move it to one, two, three. The fourth checks used>=limit before incrementing and raises, leaving used at three. A zero limit permits no calls. The limit is a nonnegative integer, so a Boolean or fractional configuration is rejected instead of becoming an accidental count policy.

The counter measures admitted attempts when consume is called before an operation. If an admitted tool later fails, the budget has still been consumed. Refunding it automatically could permit an unbounded retry loop; never refunding it may reduce task completion. Choose and document the retry policy rather than letting it emerge from exception placement. A counter also cannot stop one admitted operation from running forever. The execution layer needs a real deadline, cancellation propagation and resource boundaries.

The trace helper retains request_id, corpus_version, policy, result and excludes fields named secret or source_text. That is a useful key-level allowlist, but it does not inspect the contents of the allowed values. If a raw private question is placed inside request_id, the allowlist will retain it. A production trace schema therefore needs typed identifiers, value-length limits, permitted categories and an access/retention policy, not merely approved field names.

Authorization and freshness are independent gates. The final example combines an authorized source with fresh=False, resulting in unknown. An error response should explain the failure category without revealing restricted source identities or copying content into logs. The exact user-visible reason may need to distinguish absence, staleness and forbidden access internally while preserving the outward disclosure policy.

### Interview reasoning with explanatory answers

**Why inject time instead of reading the wall clock inside the test?** It makes boundary cases repeatable and allows exact checks at the permitted age limit. It does not remove the need to handle real clock quality in deployment.

**Does a three-call budget bound latency?** No. One call can take arbitrarily long unless the execution layer enforces a deadline and cancellation. Count and duration are different resource dimensions.

**Does an allowlisted trace guarantee no sensitive data leaks?** It restricts keys. Allowed values, downstream access, retention and correlation can still disclose information, so their contracts need separate validation.

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

**Expected:** fresh True.

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

**Expected:** used 3; fourth raisesRuntimeError before increment.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: fresh True. answer admission False; reason stale evidence. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Check evidence freshness.** Use fixedUTCnow 2026-10-22 and a document published one day earlier under a two-day limit.
   **Expected:** fresh True.
   **Verify:** Save the assertion results for exercise 1, including fresh True.

2. **Reject stale and future evidence.** Test a three-day-old document and a document dated one hour in the future.
   **Expected:** both fail freshness admission.
   **Verify:** Save the assertion results for exercise 2, including both fail freshness admission.

3. **Enforce a three-call budget.** Consume exactly 3 operations, then attempt a fourth.
   **Expected:** used 3; fourth raisesRuntimeError before increment.
   **Verify:** Save the assertion results for exercise 3, including used 3; fourth raisesRuntimeError before increment.

4. **Reject naive timestamp assumptions.** Pass a datetime without timezone information.
   **Expected:** ValueError.
   **Verify:** Save the assertion results for exercise 4, including ValueError.

5. **Build an allowlisted trace.** Create a trace from metadata plussecret/source_text fields and inspect the output.
   **Expected:** only request_id, corpus_version, policy, result fields retained.
   **Verify:** Save the assertion results for exercise 5, including only request_id, corpus_version, policy, result fields retained.

6. **Make stale evidence produce abstention.** Combine authorized True with fresh=False and require both before answering.
   **Expected:** answer admission False; reason stale evidence.
   **Verify:** Save the assertion results for exercise 6, including answer admission False; reason stale evidence.

## Common pitfalls and diagnosis

If freshness changes unexpectedly, inspect the exact timestamps, timezone normalization, inclusive boundary and the meaning of published versus effective time. If future timestamps are admitted, check the lower age bound as well as the maximum.

If retries exceed the intended work budget, trace where consume is called and whether failed attempts are refunded. If a request hangs under the call limit, inspect execution deadlines rather than increasing the counter. If a trace leaks content, inspect allowed field values and downstream access instead of only searching for a field literally named secret.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Freshness policy, Injected clock, Work budget using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-022` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Python datetime documentation](https://docs.python.org/3.12/library/datetime.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-023, Domain assistant boundaries: freshness, injection, budgets and traces.
Read courses/llm-applied/guides/llm-applied-023.md and courses/llm-applied/lessons/llm-applied-023.py. Direct prerequisites: `llm-applied-022`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
