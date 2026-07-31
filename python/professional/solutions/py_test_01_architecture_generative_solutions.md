# Test architecture and generative testing solution reasoning

Attempt `python-test-01` before reading the executable
[`py_test_01_architecture_generative_solution.py`](py_test_01_architecture_generative_solution.py).

The solution separates pure logic, stateful fakes, real-local boundaries, and
one-interaction mocks. `Clock` removes real waiting; `KeyValueStore` lets the
same contract exercise an in-memory fake and a JSON file implementation.
`patch.dict` is scoped so process environment state is restored after a test.

`merge_intervals` is the property-based target because many examples can miss
reversed endpoints, adjacency, nesting, duplicates, and empty input. Hypothesis
generates those combinations and shrinks a failure toward the smallest useful
counterexample. Its test disables the example database, uses deterministic
generation, and has no deadline, so it creates no repository cache and avoids
machine-speed failures.

A fake is valuable when behavior and state matter across several calls. A mock
is useful for one narrow interaction such as “audit once.” A real temporary
file is the right level for serialization and filesystem contract behavior.
Fixture lifetime should be the narrowest scope that preserves independence;
sharing mutable session state makes failures order-dependent.

Edge cases include expiry exactly at the deadline, malformed persisted JSON,
environment values that are blank or nonnumeric, interval endpoints in reverse
order, and a backend that passes fake-only tests but violates the real contract.

---

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Reasoning before implementation

The architecture keeps policy pure and repeatable, while contract and generative tests broaden evidence without confusing fake behavior with external systems.

1. **Protocol/injected dependency:** lets production policy receive a fake clock/store without patching global implementation details.
2. **shared contract suite:** applies the same observable create/read/update/delete requirements to fake and real-local implementations.
3. **Hypothesis strategy + property:** defines an input domain and invariant, with deterministic settings and no repository cache.
4. **Prove the failure boundary:** Exercise one normal case, one boundary case, and one injected failure without relying on hidden state.

**Alternative:** Table-driven and metamorphic tests can cover broad cases when a generative library is unavailable or the domain needs highly curated examples.

**Trade-off:** Fakes make tests fast and deterministic but can omit real failure modes; mocks verify interaction but couple easily to implementation.

**Failure boundary:** Leaked mutable fixtures, flaky timing, unordered output, malformed persisted data, concurrency interleavings, and Hypothesis databases/caches need control.

**Verification:** Run normal/boundary/failure examples, share contracts across fake/real-local, inspect a shrunk failure, prove environment restoration, and keep tests offline/deterministic.

### Verification micro-example

Run this small, deterministic case before adapting the reference to a
larger system. It gives the reasoning above an executable anchor:

```python
class FixedClock:
    def __init__(self, value):
        self.value = value

    def now(self):
        return self.value


def is_fresh(created_at, ttl, clock):
    if ttl <= 0:
        raise ValueError("ttl must be positive")
    return clock.now() < created_at + ttl


clock = FixedClock(12.0)
assert is_fresh(10.0, 3.0, clock)
clock.value = 13.0
assert not is_fresh(10.0, 3.0, clock)
```

**Expected observation:** The exact expiration boundary is tested instantly and deterministically without sleeping.

The reference implementation is one defensible contract, not a license
to copy internal steps into every system. Preserve the observable
guarantees and repeat the failure tests when adapting it.

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reference

Use this map after an honest attempt. The executable implementation remains
[`py_test_01_architecture_generative_solution.py`](py_test_01_architecture_generative_solution.py); this section explains the
contract, evidence, alternatives, and edge cases behind every numbered task.

### Exercise 1 — Choose fixture lifetime

**Prompt recap:** For each resource—immutable input rows, mutable in-memory store, temporary JSON file, and database connection—choose function, class, module, or session scope. Prefer the narrowest lifetime that is fast enough and keeps tests independent.

**Reference reasoning:** Tests should target stable behavior with the narrowest useful boundary: pure examples/properties, stateful fakes, real local adapters, and sparse interaction mocks. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Over-mocking, shared mutable fixtures, real waiting, nondeterministic generation, or snapshot updates without review can make tests fast but untrustworthy.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Choose fixture lifetime — run two tests that mutate the in-memory store and assert the second starts empty; assert a temporary JSON path differs between tests, immutable rows remain equal, and a database connection is rolled back/closed at the chosen scope.

### Exercise 2 — Complete interval merging

**Prompt recap:** Implement `merge_intervals`. Add examples for empty input, reversed endpoints, adjacent intervals, duplicates, and nesting. Then express properties: - output is sorted, - output intervals no longer touch, - every original integer point remains covered, and - no new point is created.

**Reference reasoning:** Tests should target stable behavior with the narrowest useful boundary: pure examples/properties, stateful fakes, real local adapters, and sparse interaction mocks. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Over-mocking, shared mutable fixtures, real waiting, nondeterministic generation, or snapshot updates without review can make tests fast but untrustworthy.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Complete interval merging — assert merge_intervals([]) == [], merge_intervals([(3, 1)]) == [(1, 3)], adjacency [(1, 2), (2, 4)] becomes [(1, 4)], and duplicate/nested intervals collapse; property tests must prove sorted non-touching output with exactly the same covered integer points.

### Exercise 3 — Use Hypothesis meaningfully

**Prompt recap:** Generate lists of bounded integer endpoint pairs with 100 deterministic examples, no example database, and no deadline. Introduce an adjacency bug briefly, inspect the smallest counterexample, restore the implementation, and keep a useful named regression case.

**Reference reasoning:** Tests should target stable behavior with the narrowest useful boundary: pure examples/properties, stateful fakes, real local adapters, and sparse interaction mocks. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Over-mocking, shared mutable fixtures, real waiting, nondeterministic generation, or snapshot updates without review can make tests fast but untrustworthy.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Use Hypothesis meaningfully — run the declared 100-example deterministic Hypothesis test with exit code 0; make the adjacency mutant fail, record its smallest counterexample, restore the implementation, and keep a named regression assertion for that case.

### Exercise 4 — Compare test doubles

**Prompt recap:** Complete `choose_double`. Use a fake for the stateful store, a mock only for one audit interaction, and a real temporary file for serialization behavior. Explain why mocking every store method couples tests to implementation steps.

**Reference reasoning:** Tests should target stable behavior with the narrowest useful boundary: pure examples/properties, stateful fakes, real local adapters, and sparse interaction mocks. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Over-mocking, shared mutable fixtures, real waiting, nondeterministic generation, or snapshot updates without review can make tests fast but untrustworthy.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Compare test doubles — assert the fake store preserves put/get/overwrite state, the audit mock receives exactly one expected call, and a real temporary JSON file round-trips bytes/data; include a test that would survive if every store method were merely mocked.

### Exercise 5 — Patch and restore process state

**Prompt recap:** Use `patch.dict(os.environ, ..., clear=False)` or pytest's `monkeypatch` fixture to change cache settings for one test. Assert the original environment is restored afterward. Prefer passing a mapping directly when the API permits it.

**Reference reasoning:** Tests should target stable behavior with the narrowest useful boundary: pure examples/properties, stateful fakes, real local adapters, and sparse interaction mocks. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Over-mocking, shared mutable fixtures, real waiting, nondeterministic generation, or snapshot updates without review can make tests fast but untrustworthy.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Patch and restore process state — in two tests, set and read the named cache environment variable with patch.dict or monkeypatch, then assert the original value/presence is restored after each test and after an injected exception.

### Exercise 6 — Add a contract failure

**Prompt recap:** Create a deliberately broken store that never overwrites values. Run the shared contract and locate the exact violated behavior. Contract tests complement, rather than replace, implementation-specific failure tests.

**Reference reasoning:** Tests should target stable behavior with the narrowest useful boundary: pure examples/properties, stateful fakes, real local adapters, and sparse interaction mocks. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Over-mocking, shared mutable fixtures, real waiting, nondeterministic generation, or snapshot updates without review can make tests fast but untrustworthy.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Add a contract failure — run the shared store contract against the broken no-overwrite store and record the exact failing overwrite assertion; then run the same contract against the conforming fake with exit code 0.

### Exercise 7 — model a state machine

**Prompt recap:** Create a deterministic rule-based state machine for `ExpiringCache`: put, get, delete, advance time, and overwrite. Compare every action with a simple in-memory model.

**Reasoning path:** Keep keys/values bounded, use the injected FixedClock, and assert observable state after each rule rather than inspecting implementation fields.

The model stores value plus expiry and applies the documented boundary rule
(`now < expiry`, or whichever contract is chosen). Each generated command is
run against model and system, then return values and surviving keys are
compared. Invariants include no expired value returned and overwrite replacing
both value and deadline.

Use deterministic Hypothesis settings and no example database. A failing
sequence should shrink to a short reproducible command list suitable for a
named regression test.

**Common trap:** Over-mocking, shared mutable fixtures, real waiting, nondeterministic generation, or snapshot updates without review can make tests fast but untrustworthy.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** model a state machine — execute a seeded ExpiringCache state machine containing put/get/delete/advance/overwrite actions; after every action assert cache output equals the simple model, expired keys are absent, and size never exceeds the model.

### Exercise 8 — add metamorphic tests

**Prompt recap:** Write metamorphic relations for interval merging when the exact output is inconvenient: input permutation, duplicate insertion, endpoint translation, and applying merge twice.

**Reasoning path:** A valid relation transforms input and predicts a corresponding output relationship without copying the implementation.

Merging is invariant to input order and duplicates, idempotent after one
merge, and equivariant under adding the same integer offset to every endpoint.
Generate bounded intervals, run each transformation, and compare normalized
outputs. Also retain the direct coverage/no-new-points properties.

Metamorphic tests complement examples; a shared wrong assumption can still
infect both relation and implementation, so review the mathematical contract.

**Common trap:** Over-mocking, shared mutable fixtures, real waiting, nondeterministic generation, or snapshot updates without review can make tests fast but untrustworthy.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** add metamorphic tests — assert interval results are unchanged by input permutation and duplicate insertion, translated by exactly k when every endpoint gains k, and idempotent under merge_intervals(merge_intervals(x)).

### Exercise 9 — evaluate mutation-test survivors

**Prompt recap:** Make three deliberate mutations: change expiry `<` to `<=`, stop merging adjacent intervals, and skip store overwrite. Predict which test should fail and add a focused test for any survivor.

**Reasoning path:** Mutation testing evaluates the tests, not code quality by itself. Use tiny manual mutations if no optional tool is installed.

The expiry mutation requires an exact-deadline example, adjacency requires
touching intervals, and overwrite requires two puts of one key followed by a
get. Restore production code after each controlled mutation and verify the
focused test passes normally and fails under mutation.

Do not chase a perfect mutation score: equivalent or unreachable mutations
need review. The useful output is a concrete missing behavioral assertion.

**Common trap:** Over-mocking, shared mutable fixtures, real waiting, nondeterministic generation, or snapshot updates without review can make tests fast but untrustworthy.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** evaluate mutation-test survivors — run each of the <= expiry, no-adjacency-merge, and no-overwrite mutants separately; name the test that fails, and add a focused assertion if any mutant survives so all three finish killed.

### Exercise 10 — test concurrency without timing races

**Prompt recap:** Design a two-worker cache/store test using barriers/events to force a specific interleaving. State whether the contract promises thread safety; if it does not, test the synchronization wrapper instead.

**Reasoning path:** Control checkpoints explicitly. Do not assert that a race happens within a tiny sleep window.

Represent the unsafe read/modify/write steps with synchronization events so
both workers read before either writes, then assert the documented lost-update
or wrapper repair. If thread safety is out of scope, make that limitation
explicit and avoid a misleading flaky stress test.

For a synchronized wrapper, assert the entire compound operation is protected
and invariants hold after both workers complete. Join with a generous timeout
only to prevent a hung test, not as the correctness condition.

**Common trap:** Over-mocking, shared mutable fixtures, real waiting, nondeterministic generation, or snapshot updates without review can make tests fast but untrustworthy.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** test concurrency without timing races — use barriers/events—not sleep—to force the declared two-worker interleaving; assert final value/call count or the synchronization wrapper's result, both workers terminate before a fixed timeout, and no exception is lost.

### Exercise 11 — triage a flaky test

**Prompt recap:** Take a test that depends on wall-clock sleep, random data, shared files, or unordered output. Classify the cause, collect repeat evidence, and replace the unstable boundary rather than adding retries.

**Reasoning path:** Control clock/randomness, isolate storage, sort only when order is not contractual, and keep the original failure seed/input.

First prove reproducibility with repeated focused runs and capture environment,
seed, worker count, and failing input. Determine whether the product behavior
is nondeterministic or merely the assertion. Inject the clock/random source,
use `tmp_path`, and remove order assumptions only when the API promises no
order.

Quarantine and retry can preserve CI temporarily but are not fixes; retain an
owner and deadline if used.

**Common trap:** Over-mocking, shared mutable fixtures, real waiting, nondeterministic generation, or snapshot updates without review can make tests fast but untrustworthy.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** triage a flaky test — repeat the original flaky test enough times to record its failure rate and classify clock/random/file/order state; replace that boundary with a fake clock, seed, tmp_path, or sorted assertion and then obtain a clean repeated-test transcript without retries.

### Exercise 12 — design a layered verification portfolio

**Prompt recap:** Map one feature across pure unit/property tests, shared store contract, real temporary-file integration, CLI/process smoke, and optional external system test. Define what each layer proves and does not prove.

**Reasoning path:** Keep the default suite offline and fast. Use the fewest expensive tests that cover serialization, process, or external boundaries.

Pure tests cover transformation and expiry policy; the shared contract covers
backend semantics; a temporary JSON adapter test proves real serialization and
atomic replacement; a subprocess smoke proves packaging/CLI boundaries.
External tests are explicit, credentialed, and never required for the portable
default.

Avoid duplicating every assertion at every layer. Assign each risk to the
cheapest boundary capable of exposing it, then retain one end-to-end path for
wiring evidence.

**Common trap:** Over-mocking, shared mutable fixtures, real waiting, nondeterministic generation, or snapshot updates without review can make tests fast but untrustworthy.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** design a layered verification portfolio — deliver a matrix with unit/property, shared contract, temporary-file integration, CLI subprocess, and optional external rows; for each name its command/test ID, input fixture, expected output/failure, runtime budget, and the claim it cannot prove.
