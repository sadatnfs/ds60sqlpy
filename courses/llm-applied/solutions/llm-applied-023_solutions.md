# llm-applied-023: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A production-oriented domain assistant needs controls around the model as well as a good prompt. Evidence can become stale, access can change, caches can outlive their source version, and tool proposals can exceed work budgets. Observability should explain which stage failed without logging secrets or unrestricted source text. A trace can record request ID, policy fingerprint, corpus/index/model versions, admitted document IDs, tool counts and named failure categories. It should not become a second unprotected corpus.

This lesson implements deterministic freshness and budget checks using an injected clock. No server, deployment or live identity integration is started. A timestamp comparison establishes whether a document meets the declared freshness window; it does not prove the source is correct. A call counter enforces a bounded operation budget; it does not substitute for actual process timeouts in a serving system. Hostile text remains data under the same access and tool policies established earlier. The goal is to make each boundary and its evidence explicit before scaling the assistant.

**Freshness policy:** A declared maximum age for evidence under a task contract.

**Injected clock:** A supplied time value making temporal behavior deterministic in tests.

**Work budget:** A maximum number of admitted operations before refusal.

**Safe trace:** Diagnostic metadata selected without copying sensitive content.

## Reading the implementation

Use timezone-aware UTC datetimes and reject naive timestamps. Compareage=now-published with a nonnegative maximum age, also rejecting future publication times. A Budget object increments only for admitted operations and raises before exceeding its limit. Cache identity includes policy and corpus versions. Trace construction uses an allowlist of metadata fields and excludes source text, credentials and raw private queries.

## Trace temporal admission, work consumption and diagnosis

The freshness helper computes age=now-published and accepts0<=age<=maximum_age. Both boundaries are inclusive. At a two-day limit, a source exactly two days old is admitted; a source two days plus one microsecond old is not. A future publication has negative age and fails rather than remaining perpetually fresh. These comparisons implement a chosen policy, not a test that the document is factually correct.

The supplied fixtures use timezone-aware UTC datetimes. Rejection of naive timestamps prevents one obvious ambiguity, but a complete real-time interface also needs normalization and a policy for source clocks. Civil-time transitions and ambiguous local timestamps deserve separate tests if non-UTC input is supported. An aware timestamp alone should not be described as a complete clock-quality guarantee.

Different temporal fields should remain distinguishable. A policy may be published yesterday but effective next month, or discovered today after applying for weeks. A current answer might require both applicability and a recent verification event. A historical answer might intentionally use an old source that was effective at the event time. The simple published-age gate cannot decide those cases without additional metadata.

The Budget object starts with used=0. Three consume calls move it to one, two, three. The fourth checks used>=limit before incrementing and raises, leaving used at three. A zero limit permits no calls. The limit is a nonnegative integer, so a Boolean or fractional configuration is rejected instead of becoming an accidental count policy.

The counter measures admitted attempts when consume is called before an operation. If an admitted tool later fails, the budget has still been consumed. Refunding it automatically could permit an unbounded retry loop; never refunding it may reduce task completion. Choose and document the retry policy rather than letting it emerge from exception placement. A counter also cannot stop one admitted operation from running forever. The execution layer needs a real deadline, cancellation propagation and resource boundaries.

The trace helper retains request_id, corpus_version, policy, result and excludes fields named secret or source_text. That is a useful key-level allowlist, but it does not inspect the contents of the allowed values. If a raw private question is placed inside request_id, the allowlist will retain it. A production trace schema therefore needs typed identifiers, value-length limits, permitted categories and an access/retention policy, not merely approved field names.

Authorization and freshness are independent gates. The final example combines an authorized source with stale=False admission, resulting in unknown. An error response should explain the failure category without revealing restricted source identities or copying content into logs. The exact user-visible reason may need to distinguish absence, staleness and forbidden access internally while preserving the outward disclosure policy.

### Interview reasoning with explanatory answers

**Why inject time instead of reading the wall clock inside the test?** It makes boundary cases repeatable and allows exact checks at the permitted age limit. It does not remove the need to handle real clock quality in deployment.

**Does a three-call budget bound latency?** No. One call can take arbitrarily long unless the execution layer enforces a deadline and cancellation. Count and duration are different resource dimensions.

**Does an allowlisted trace guarantee no sensitive data leaks?** It restricts keys. Allowed values, downstream access, retention and correlation can still disclose information, so their contracts need separate validation.

## Exercise 1: Check evidence freshness

The question is: Use fixed UTC now 2026-10-22 and a document published one day earlier under a two-day limit.

The clock is supplied rather than read globally, so the test is reproducible. The result concerns the declared age policy, not the truth of the content.

```python
now=datetime(2026,10,22,tzinfo=timezone.utc); published=now-timedelta(days=1)
assert fresh(published,now,timedelta(days=2))
```

**Expected:** fresh True.

**Verify:** Compare the computed values or written argument with fresh True.

## Exercise 2: Reject stale and future evidence

The question is: Test a three-day-old document and a document dated one hour in the future.

Future timestamps can indicate clock or metadata errors. Accepting them as indefinitely fresh would conceal that data-quality problem.

```python
assert not fresh(now-timedelta(days=3),now,timedelta(days=2))
assert not fresh(now+timedelta(hours=1),now,timedelta(days=2))
```

**Expected:** both fail freshness admission.

**Verify:** Compare the computed values or written argument with both fail freshness admission.

## Exercise 3: Enforce a three-call budget

The question is: Consume exactly3 operations, then attempt a fourth.

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

**Verify:** Compare the computed values or written argument with used3; fourth raisesRuntimeError before increment.

## Exercise 4: Reject naive timestamp assumptions

The question is: Pass a datetime without timezone information.

A local wall-clock value cannot be safely compared with a UTC instant without an explicit zone policy. Silent assumptions can shift freshness boundaries.

```python
try: fresh(datetime(2026,10,21),now,timedelta(days=2))
except ValueError: pass
else: raise AssertionError('naive timestamp accepted')
```

**Expected:** ValueError.

**Verify:** Compare the computed values or written argument with ValueError.

## Exercise 5: Build an allowlisted trace

The question is: Create a trace from metadata plussecret/source_text fields and inspect the output.

Observability can leak information if it copies raw inputs indiscriminately. An explicit metadata schema makes the diagnostic surface reviewable.

```python
raw={'request_id':'r1','corpus_version':'v2','policy':'public','result':'abstained_stale','secret':'hidden','source_text':'restricted body'}
trace=trace_record(raw)
assert set(trace)=={'request_id','corpus_version','policy','result'} and 'secret' not in trace and 'source_text' not in trace
```

**Expected:** only request_id, corpus_version, policy, result fields retained.

**Verify:** Compare the computed values or written argument with only request_id, corpus_version, policy, result fields retained.

## Exercise 6: Make stale evidence produce abstention

The question is: Combine authorizedTrue withfreshFalse and require both before answering.

Authorization and freshness are independent gates. A permitted but stale source should not be treated as current merely because it is accessible.

```python
authorized=True; current=fresh(now-timedelta(days=3),now,timedelta(days=2)); answer_allowed=authorized and current
assert not answer_allowed
result={'status':'unknown','reason':'stale evidence'}; assert result['reason']=='stale evidence'
```

**Expected:** answer admission False; reason stale evidence.

**Verify:** Compare the computed values or written argument with answer admission False; reason stale evidence.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
