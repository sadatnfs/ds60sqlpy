# Test architecture, doubles, and generative testing

**Stable ID:** `python-test-01`

**Level:** intermediate

**Estimated time:** 180–240 minutes

## Level and prerequisites

- **Catalog prerequisite:** `python-10`
- Python Days 1–10, especially functions, exceptions, files, and pytest
- Bridge Day 5 is a useful database-specific follow-on, not a prerequisite
- The `professional` dependency group for Hypothesis

The lab uses temporary files, injected clocks, in-memory fakes, and
deterministic Hypothesis settings. It opens no network connection and creates no
Hypothesis example database.

## Learning objectives

You will be able to:

1. Choose fixture scope from ownership and lifetime.
2. Patch environment state inside a restoration boundary.
3. Replace real time with a `Clock` seam.
4. Choose a fake, mock, or real-local implementation deliberately.
5. Reuse one contract suite across an I/O fake and implementation.
6. State properties before generating examples.
7. Interpret a shrunk counterexample and turn it into a regression test.

## Vocabulary and concepts

- **Fixture:** setup data or resources with a defined lifetime.
- **Test seam:** a dependency boundary that can be replaced or injected.
- **Fake:** a working, simplified implementation with state and behavior.
- **Mock:** an interaction recorder used to assert a narrow call contract.
- **Stub:** a fixed response provider.
- **Monkeypatch:** a temporary replacement of process or module state.
- **Contract test:** the same behavior requirements applied to implementations
  of one boundary.
- **Property:** an invariant that should hold for a broad input domain.
- **Generator/strategy:** a description of values Hypothesis may create.
- **Shrinking:** reducing a failure to a smaller counterexample.
- **Example database:** Hypothesis's optional persisted failure history; this
  lesson disables it to keep the repository clean.

## Worked example / walkthrough

The learner file injects `FixedClock(12.0)` into a TTL decision. The test does
not sleep and cannot become slow under load.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_test_01_architecture_generative.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_test_01_architecture_generative.py
```

The reference solution builds:

```text
ExpiringCache -> KeyValueStore Protocol -> MemoryStore fake
                                      \-> JsonFileStore real-local boundary
              -> Clock Protocol       -> FixedClock
SessionService -> AuditSink Protocol  -> one narrow mock in the test
```

Both stores receive the same create/read/update/delete contract. Temporary-file
tests prove JSON and replacement behavior that the fake cannot prove.

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

Work from the repository root. First run the answer-free learner
module named in this guide's original walkthrough. Read each TODO as a
contract: record the input, returned value, raised exception, and side
effect before implementing it. Then run the focused test command in
**Self-check**. Keep exploratory changes in a copy or a new test; the
checked-in solution remains a comparison artifact.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_test_01_architecture_generative.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_test_01_architecture_generative.py
```

The focused test command is shown in **Self-check** below. The learner
module is intentionally answer-free, so `TODO` output is the expected
starting state rather than a setup failure.

## Mechanism lab — two small examples before the full system

### Boundary and mental model

A test seam makes time, storage, randomness, environment, or transport
replaceable. A fake is a working simplified implementation; a mock
records a narrow interaction; a real-local implementation proves
serialization or filesystem behavior. Shared contract tests prevent a
convenient fake from drifting away from the real boundary.

Property-based testing starts with an invariant and generates many
inputs, then shrinks a failure to a small counterexample. It complements
named examples and boundary tests; it does not infer the property or
replace external integration evidence.

- **Protocol/injected dependency:** lets production policy receive a fake clock/store without patching global implementation details.
- **shared contract suite:** applies the same observable create/read/update/delete requirements to fake and real-local implementations.
- **Hypothesis strategy + property:** defines an input domain and invariant, with deterministic settings and no repository cache.

### Micro-example A — replace wall-clock sleep with an injected clock

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

**Why it matters:** The clock represents monotonic elapsed time rather than an adjustable wall clock.

### Micro-example B — state an idempotence property

```python
def normalize_tags(tags):
    return tuple(sorted({tag.strip().lower() for tag in tags if tag.strip()}))

original = [" Python ", "sql", "PYTHON", ""]
once = normalize_tags(original)
twice = normalize_tags(once)
print(once)
assert once == twice  # applying normalization twice changes nothing
```

**Expected observation:** The named example demonstrates idempotence, a reusable property over a much broader input domain.

**Why it matters:** Case folding, whitespace removal, uniqueness, and sorted output are the intended public contract.

### Debugging and transfer

**Common mistake:** Mocking every internal call or generating arbitrary values without stating an invariant and valid domain.

**Diagnostic:** Name the observable behavior, choose the smallest seam/double, run the same contract on a real-local implementation, and retain the shrunk counterexample.

**Transfer question:** Which parts of a database client can a fake prove, and which require a disposable real PostgreSQL integration?

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercises

### 1. Choose fixture lifetime

For each resource—immutable input rows, mutable in-memory store, temporary JSON
file, and database connection—choose function, class, module, or session scope.
Prefer the narrowest lifetime that is fast enough and keeps tests independent.

**Verify:** For task `Choose fixture lifetime`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior.







### 2. Complete interval merging

Implement `merge_intervals`. Add examples for empty input, reversed endpoints,
adjacent intervals, duplicates, and nesting.

Then express properties:

- output is sorted,
- output intervals no longer touch,
- every original integer point remains covered, and
- no new point is created.

**Verify:** For task `Complete interval merging`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then run the named missing/unknown/empty boundary and assert its explicit fallback or exception instead of accepting an accidental default.







### 3. Use Hypothesis meaningfully

Generate lists of bounded integer endpoint pairs. Use:

```python
settings(max_examples=100, derandomize=True, database=None, deadline=None)
```

Temporarily introduce a bug such as failing to merge adjacency. Read the
smallest failing example. Restore the implementation and keep that example as a
named regression test if it communicates an important rule.

**Verify:** For task `Use Hypothesis meaningfully`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior.







### 4. Compare test doubles

Complete `choose_double`. Use a fake for the stateful store, a mock only for one
audit interaction, and a real temporary file for serialization behavior.
Explain why mocking every store method couples tests to implementation steps.

**Verify:** For task `Compare test doubles`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### 5. Patch and restore process state

Use `patch.dict(os.environ, ..., clear=False)` or pytest's `monkeypatch` fixture
to change cache settings for one test. Assert the original environment is
restored afterward. Prefer passing a mapping directly when the API permits it.

**Verify:** For task `Patch and restore process state`, measure peak active/queued work, account for every input, and prove permits/resources are released after success and injected failure.







### 6. Add a contract failure

Create a deliberately broken store that never overwrites values. Run the shared
contract and locate the exact violated behavior. Contract tests complement,
rather than replace, implementation-specific failure tests.

**Verify:** For task `Add a contract failure`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 7 — model a state machine

Create a deterministic rule-based state machine for `ExpiringCache`: put, get, delete, advance time, and overwrite. Compare every action with a simple in-memory model.

**Progressive hint:** Keep keys/values bounded, use the injected FixedClock, and assert observable state after each rule rather than inspecting implementation fields.

**Verify:** For task `model a state machine`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Exercise 8 — add metamorphic tests

Write metamorphic relations for interval merging when the exact output is inconvenient: input permutation, duplicate insertion, endpoint translation, and applying merge twice.

**Progressive hint:** A valid relation transforms input and predicts a corresponding output relationship without copying the implementation.

**Verify:** For task `add metamorphic tests`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior.







### Exercise 9 — evaluate mutation-test survivors

Make three deliberate mutations: change expiry `<` to `<=`, stop merging adjacent intervals, and skip store overwrite. Predict which test should fail and add a focused test for any survivor.

**Progressive hint:** Mutation testing evaluates the tests, not code quality by itself. Use tiny manual mutations if no optional tool is installed.

**Verify:** For task `evaluate mutation-test survivors`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Exercise 10 — test concurrency without timing races

Design a two-worker cache/store test using barriers/events to force a specific interleaving. State whether the contract promises thread safety; if it does not, test the synchronization wrapper instead.

**Progressive hint:** Control checkpoints explicitly. Do not assert that a race happens within a tiny sleep window.

**Verify:** For task `test concurrency without timing races`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then assert exact names, order, types/nullability or versions and prove one mismatch is rejected rather than silently coerced.







### Exercise 11 — triage a flaky test

Take a test that depends on wall-clock sleep, random data, shared files, or unordered output. Classify the cause, collect repeat evidence, and replace the unstable boundary rather than adding retries.

**Progressive hint:** Control clock/randomness, isolate storage, sort only when order is not contractual, and keep the original failure seed/input.

**Verify:** For task `triage a flaky test`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 12 — design a layered verification portfolio

Map one feature across pure unit/property tests, shared store contract, real temporary-file integration, CLI/process smoke, and optional external system test. Define what each layer proves and does not prove.

**Progressive hint:** Keep the default suite offline and fast. Use the fewest expensive tests that cover serialization, process, or external boundaries.

**Verify:** For task `design a layered verification portfolio`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then assert exact names, order, types/nullability or versions and prove one mismatch is rejected rather than silently coerced.







## Self-check

- No test sleeps or depends on wall-clock time.
- Mutable fixtures cannot leak between tests.
- Environment patches are restored.
- Fake and real-local stores pass the same contract.
- The mock asserts one meaningful audit interaction, not internal call order.
- Hypothesis runs at least 100 examples with `database=None`.
- Interval properties verify coverage, ordering, and disjoint output.
- A malformed JSON file fails visibly.

Windows PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m unittest python.professional.tests.test_py_test_01_architecture_generative -v
```

macOS/Linux:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest python.professional.tests.test_py_test_01_architecture_generative -v
```

## Common pitfalls

- **A suite passes alone but fails together:** shared mutable fixture state
  escaped its intended lifetime.
- **A time test takes seconds:** production code called the global clock or
  sleep rather than an injected seam.
- **A mock breaks after harmless refactoring:** the test asserted call order
  instead of observable behavior.
- **The fake passes but production fails:** the fake did not share a contract
  with a real-local boundary.
- **Property tests are random fuzzing:** no invariant was stated. Define what
  must remain true before selecting strategies.
- **Hypothesis creates `.hypothesis/`:** the example database was not disabled
  for this repository exercise.
- **A failing case is huge:** inspect Hypothesis's final shrunk example, not the
  first generated input shown during verbose debugging.

## Next step

Apply the same contract/fake pattern to Bridge Day 5. Continue to
`python-lang-01` to make test seams precise with generics, Protocols, overloads,
and runtime validation.

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-test-01` — Test architecture, doubles, and generative testing.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize test seams, fakes versus mocks, shared contracts, and generative properties. Use exactly these maintained learner materials:
- guide: `python/professional/companion-guides/py_test_01_architecture_generative.md`
- learner artifact: `python/professional/lessons/py_test_01_architecture_generative.py`

Assume only the prerequisites declared in the guide. Do not open or
quote anything under `solutions/` unless I explicitly ask after an
honest attempt. First explain one concept in plain language and show a
tiny example. Then ask me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
