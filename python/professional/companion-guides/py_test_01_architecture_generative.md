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

## Exercises

### 1. Choose fixture lifetime

For each resource—immutable input rows, mutable in-memory store, temporary JSON
file, and database connection—choose function, class, module, or session scope.
Prefer the narrowest lifetime that is fast enough and keeps tests independent.

### 2. Complete interval merging

Implement `merge_intervals`. Add examples for empty input, reversed endpoints,
adjacent intervals, duplicates, and nesting.

Then express properties:

- output is sorted,
- output intervals no longer touch,
- every original integer point remains covered, and
- no new point is created.

### 3. Use Hypothesis meaningfully

Generate lists of bounded integer endpoint pairs. Use:

```python
settings(max_examples=100, derandomize=True, database=None, deadline=None)
```

Temporarily introduce a bug such as failing to merge adjacency. Read the
smallest failing example. Restore the implementation and keep that example as a
named regression test if it communicates an important rule.

### 4. Compare test doubles

Complete `choose_double`. Use a fake for the stateful store, a mock only for one
audit interaction, and a real temporary file for serialization behavior.
Explain why mocking every store method couples tests to implementation steps.

### 5. Patch and restore process state

Use `patch.dict(os.environ, ..., clear=False)` or pytest's `monkeypatch` fixture
to change cache settings for one test. Assert the original environment is
restored afterward. Prefer passing a mapping directly when the API permits it.

### 6. Add a contract failure

Create a deliberately broken store that never overwrites values. Run the shared
contract and locate the exact violated behavior. Contract tests complement,
rather than replace, implementation-specific failure tests.

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
