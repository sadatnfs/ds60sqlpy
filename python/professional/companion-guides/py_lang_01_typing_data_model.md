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

### 2. Implement the iterator protocol

Complete `Batches.__next__`. Return tuples, advance the offset, and raise
`StopIteration` only after exhaustion. Test empty input and a final partial
batch.

### 3. Reason about variance

Assign `SequenceReader[str]` to `Reader[object]`; this is safe because callers
only read. Explain why a mutable repository of strings cannot be treated as a
repository of objects: a caller might store an integer into it.

### 4. Model events with TypedDict

Add a third event with a unique literal `kind`. Update `describe_event` and let
the checker identify unhandled or invalid fields. Add runtime validation at the
JSON boundary; TypedDict alone does not validate decoded data.

### 5. Exercise context-manager failure

Append inside `Transaction`, then raise. Verify the target remains unchanged
and the exception propagates. Returning true from `__exit__` would suppress it;
this implementation deliberately returns false.

### 6. Trace descriptor lookup

Compare `Customer.name` with `Customer("Ada").name`. Explain why the descriptor
returns itself for class access. Corrupt the private field deliberately and
observe the runtime type guard.

### 7. Draw the MRO

Print `ApiRecord.__mro__`. Predict the label before calling it. Every mixin uses
cooperative `super()`; directly naming a parent would skip or duplicate work.

### 8. Bound metaclass use

Add a second `Handler` with `__init_subclass__`. Survey how a metaclass could
enforce the same rule, then state why the hook is preferable here. Use a
metaclass only when class-creation behavior cannot be expressed by descriptors,
decorators, or subclass hooks.

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
