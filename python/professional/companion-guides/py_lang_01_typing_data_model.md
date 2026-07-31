# Advanced typing and the Python data model

**Stable ID:** `python-lang-01`

**Level:** advanced

**Estimated time:** 210–270 minutes

## Level and prerequisites

- **Catalog prerequisite:** `python-12`
- Python Days 1–12, including iterators, classes, dataclasses, and type hints
- Bridge Day 2 is helpful introductory Protocol and context-manager practice,
  not a prerequisite
- Python 3.11 or 3.12

Examples use 3.11-compatible `TypeVar`/`Generic` syntax. Python 3.12's bracketed
type-parameter syntax is intentionally not required.

## Learning objectives

You will be able to:

1. Build a generic read-only Protocol and explain practical covariance.
2. Use invariant types when values are both consumed and produced.
3. Model dictionary unions with TypedDict and literal discriminants.
4. Align overload declarations with runtime behavior.
5. Implement iterator and context-manager protocols.
6. Explain descriptor lookup and validate assignment.
7. Trace cooperative `super()` through method resolution order (MRO).
8. Separate static promises from runtime enforcement.
9. Recognize when `__init_subclass__` is simpler than a metaclass.

## Vocabulary and concepts

- **Generic:** code parameterized by another type.
- **Covariance:** `Container[Specific]` can be used as
  `Container[General]`, safe for producers/readers.
- **Invariance:** parameterized types are unrelated, needed when a value is
  consumed and produced.
- **Protocol:** structural interface checked from available members.
- **TypedDict:** static shape for a dictionary.
- **Literal:** a type restricted to exact values.
- **Overload:** multiple static call signatures for one implementation.
- **Data model:** Python protocols behind iteration, context management,
  descriptors, operators, and class creation.
- **Descriptor:** object whose `__get__`, `__set__`, or `__delete__` controls
  attribute access.
- **MRO:** ordered classes Python searches and `super()` follows.
- **Metaclass:** class of a class, able to customize class creation.

## Worked example / walkthrough

Run the learner parser and iterator scaffold.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_lang_01_typing_data_model.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_lang_01_typing_data_model.py
```

The solution then composes several contracts:

```text
Reader[T_co]      -> read-only covariance
MutableRepository -> invariant read/write boundary
DomainEvent       -> TypedDict union narrowed by "kind"
Batches[T]        -> __iter__ + __next__
Transaction       -> __enter__ + __exit__
NonBlankText      -> descriptor class/instance access
ApiRecord         -> cooperative super() through its MRO
Handler           -> __init_subclass__ registry
```

Static checking catches impossible uses before execution. Runtime code still
validates text, schemas, transaction state, and descriptor assignments.

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
.\.venv\Scripts\python.exe python\professional\lessons\py_lang_01_typing_data_model.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_lang_01_typing_data_model.py
```

The focused test command is shown in **Self-check** below. The learner
module is intentionally answer-free, so `TODO` output is the expected
starting state rather than a setup failure.

## Mechanism lab — two small examples before the full system

### Boundary and mental model

Type hints describe contracts for static tools and readers; they do not
automatically validate runtime data. A Protocol is structural: a class
satisfies it by providing required members, without inheritance.
Covariance is safe for values a container only produces; mutable
read/write containers are generally invariant.

Python syntax such as iteration, context management, attribute access,
and `super()` is powered by data-model protocols. Implementing these
hooks means honoring their full lifecycle: `StopIteration`, exception
propagation and cleanup, descriptor class/instance access, and
cooperative method-resolution order.

- **`Protocol` + `TypeVar`:** expresses the smallest structural interface and its variance from producer/consumer behavior.
- **`@overload` signatures + one implementation:** gives static callers precise return types while runtime code still validates the discriminant.
- **`__iter__` / `__next__` / `__enter__` / `__exit__`:** participates in Python-managed lifecycle and must honor exhaustion, cleanup, and exception rules.

### Micro-example A — show structural compatibility without inheritance

```python
from typing import Protocol

class Named(Protocol):
    @property
    def name(self) -> str: ...

class PlainRecord:
    def __init__(self, name):
        self.name = name

def label(value: Named) -> str:
    return value.name.upper()

print(label(PlainRecord("ada")))
assert label(PlainRecord("ada")) == "ADA"
```

**Expected observation:** `PlainRecord` never inherits from `Named`; static structural matching uses its available member.

**Why it matters:** At runtime, the provided `name` is actually a string; the Protocol alone does not validate decoded input.

### Micro-example B — honor iterator exhaustion and partial batches

```python
iterator = iter([("a", "b"), ("c",)])
assert next(iterator) == ("a", "b")
assert next(iterator) == ("c",)
try:
    next(iterator)
except StopIteration:
    print("iterator exhausted exactly once input ended")
```

**Expected observation:** The final partial batch is a valid value; only the following call signals exhaustion.

**Why it matters:** Empty and partial batches are part of the iterator's documented contract.

### Debugging and transfer

**Common mistake:** Assuming `isinstance` with a runtime Protocol validates generic arguments or decoded field types.

**Diagnostic:** Run mypy/pyright on intended and intentionally invalid uses, then separately test runtime boundary validation and every data-model lifecycle edge.

**Transfer question:** How would a read-only covariant repository change if it gained a `save(value)` method?

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercises

### 1. Complete and type the overloaded parser

Implement the three promised return behaviors. Reject boolean text other than
`true` and `false`. In VS Code, inspect the inferred type of:

```python
number = parse_scalar("12", "int")
flag = parse_scalar("true", "bool")
```

Passing a variable typed as arbitrary `str` needs a broader overload or prior
narrowing; overloads do not inspect future runtime text.

**Verify:** For task `Complete and type the overloaded parser`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### 2. Implement the iterator protocol

Complete `Batches.__next__`. Return tuples, advance the offset, and raise
`StopIteration` only after exhaustion. Test empty input and a final partial
batch.

**Verify:** For task `Implement the iterator protocol`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then run the named missing/unknown/empty boundary and assert its explicit fallback or exception instead of accepting an accidental default.







### 3. Reason about variance

Assign `SequenceReader[str]` to `Reader[object]`; this is safe because callers
only read. Explain why a mutable repository of strings cannot be treated as a
repository of objects: a caller might store an integer into it.

**Verify:** For task `Reason about variance`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### 4. Model events with TypedDict

Add a third event with a unique literal `kind`. Update `describe_event` and let
the checker identify unhandled or invalid fields. Add runtime validation at the
JSON boundary; TypedDict alone does not validate decoded data.

**Verify:** For task `Model events with TypedDict`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### 5. Exercise context-manager failure

Append inside `Transaction`, then raise. Verify the target remains unchanged
and the exception propagates. Returning true from `__exit__` would suppress it;
this implementation deliberately returns false.

**Verify:** For task `Exercise context-manager failure`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### 6. Trace descriptor lookup

Compare `Customer.name` with `Customer("Ada").name`. Explain why the descriptor
returns itself for class access. Corrupt the private field deliberately and
observe the runtime type guard.

**Verify:** For task `Trace descriptor lookup`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### 7. Draw the MRO

Print `ApiRecord.__mro__`. Predict the label before calling it. Every mixin uses
cooperative `super()`; directly naming a parent would skip or duplicate work.

**Verify:** For task `Draw the MRO`, demonstrate the concrete requirement “7. Draw the MRO Print ApiRecord. mro . Predict the label before calling it. Every mixin uses cooperative super ; directly naming a parent would skip or duplicate work” with explicit inputs, observable output, and one counterexample.







### 8. Bound metaclass use

Add a second `Handler` with `__init_subclass__`. Survey how a metaclass could
enforce the same rule, then state why the hook is preferable here. Use a
metaclass only when class-creation behavior cannot be expressed by descriptors,
decorators, or subclass hooks.

**Verify:** For task `Bound metaclass use`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 9 — design a structural Protocol

Define a minimal generic `Serializer[T]` Protocol and implement JSON and text serializers without inheritance. Add a consumer and let mypy reject one incompatible implementation.

**Progressive hint:** Protocol methods express only what the consumer needs. Use a 3.11-compatible TypeVar and abstract collection input types.

**Verify:** For task `design a structural Protocol`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### Exercise 10 — preserve signatures with ParamSpec

Write a timing decorator that preserves arbitrary positional/keyword parameters and return type, injects a log sink/clock for tests, and re-raises the wrapped exception unchanged.

**Progressive hint:** Use `ParamSpec`, a return `TypeVar`, `Callable[P, R]`, and `functools.wraps`.

**Verify:** For task `preserve signatures with ParamSpec`, demonstrate the concrete requirement “Exercise 10 — preserve signatures with ParamSpec Write a timing decorator that preserves arbitrary positional/keyword parameters and return type, injects a log sink/clock for tests” with explicit inputs, observable output, and one counterexample.







### Exercise 11 — narrow decoded data safely

Implement a `TypeGuard` that validates a decoded JSON object as a specific TypedDict, including exact required keys, value types, and the bool-versus-int edge case.

**Progressive hint:** `isinstance(True, int)` is true. Test bool explicitly before accepting integer fields, and reject unknown keys if the boundary is strict.

**Verify:** For task `narrow decoded data safely`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Exercise 12 — choose frozen, slots, and hash semantics

Create a small value-object dataclass and compare mutable, frozen, slotted, and `unsafe_hash` choices. Use it as a dictionary key and show which combinations preserve hash invariants.

**Progressive hint:** Hashable keys must not change equality-relevant fields while stored. `unsafe_hash` does not make mutation safe.

**Verify:** For task `choose frozen, slots, and hash semantics`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Exercise 13 — implement cooperative equality

Implement `__eq__` for a value type so unrelated types receive `NotImplemented`, subclasses behave deliberately, and hashing remains consistent. Contrast this with returning `False` immediately.

**Progressive hint:** `NotImplemented` lets Python try the reflected comparison and then fall back appropriately; it is not the same object as `NotImplementedError`.

**Verify:** For task `implement cooperative equality`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then verify identity/hash and metadata, then reload or inspect the artifact outside the creating state and test one tampered mismatch.







### Exercise 14 — evolve a typed serialization boundary

Version a discriminated TypedDict union, add an optional field to one event, and parse old/new payloads into immutable domain objects. Define unknown-version and unknown-kind failures.

**Progressive hint:** Narrow on literal version/kind only after runtime validation. Keep wire payloads separate from trusted domain types.

**Verify:** For task `evolve a typed serialization boundary`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### Exercise 15 — trace weak references and caches

Compare a normal dictionary cache with `WeakValueDictionary` for objects that support weak references. Drop strong references, force collection only as an observation, and state when cache disappearance is acceptable.

**Progressive hint:** Weak caches do not own values. Slotted classes need weak-reference support explicitly, and collection timing is not a business deadline.

**Verify:** For task `trace weak references and caches`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.







### Exercise 16 — review typing compatibility

Change a public function from accepting `Sequence[str]` to `list[str]`, and another return from `list[str]` to `Sequence[str]`. Analyze source compatibility for callers and implement a deprecation-safe alternative.

**Progressive hint:** Parameter types are consumer inputs; narrowing them breaks callers. Return types can often become more specific, not arbitrarily more abstract.

**Verify:** For task `review typing compatibility`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







## Self-check

- All examples parse on Python 3.11.
- Literal overloads match runtime return types.
- Iterator exhaustion raises `StopIteration`.
- Failed transactions roll back and propagate exceptions.
- Descriptor class and instance access both work.
- Runtime-checkable Protocol use is described as shallow structural checking.
- Covariance is limited to the read-only producer.
- TypedDict JSON is validated separately at runtime.
- MRO output explains the mixin result.

Windows PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m unittest python.professional.tests.test_py_lang_01_typing_data_model -v
```

macOS/Linux:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest python.professional.tests.test_py_lang_01_typing_data_model -v
```

## Common pitfalls

- **A Protocol is treated as an abstract base class:** structural types do not
  require inheritance.
- **`isinstance` is assumed to prove full types:** runtime Protocol checks see
  members, not complete annotated semantics.
- **A mutable generic is made covariant:** callers could insert an incompatible
  value.
- **Overloads contain separate implementations:** overload bodies are static
  declarations; exactly one runtime implementation follows.
- **`__next__` returns a sentinel:** Python iteration ends with
  `StopIteration`.
- **A context manager hides errors:** `__exit__` accidentally returned true.
- **A mixin names its parent:** cooperative MRO composition is broken.
- **A metaclass solves ordinary validation:** a descriptor or subclass hook is
  usually simpler.

## Next step

Apply these boundaries to `python-test-01`, `python-svc-01`, and the engineering
bridge. For deeper study, add a typed async context manager and compare static
checker diagnostics with explicit runtime validation.

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-lang-01` — Advanced typing and the Python data model.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize static type contracts, structural protocols, overloads, and Python data-model hooks. Use exactly these maintained learner materials:
- guide: `python/professional/companion-guides/py_lang_01_typing_data_model.md`
- learner artifact: `python/professional/lessons/py_lang_01_typing_data_model.py`

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
