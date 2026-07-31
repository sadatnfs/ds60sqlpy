# Advanced typing and data-model solution reasoning

Attempt `python-lang-01` before reading
[`py_lang_01_typing_data_model_solution.py`](py_lang_01_typing_data_model_solution.py).

`Reader[T_co]` is covariant because it only produces values. A mutable
repository both consumes and produces its type, so it remains invariant.
`TypedDict` describes the shape of existing dictionaries; its literal `kind`
field lets a checker narrow a union. Overloads describe the relationship
between a literal argument and return type, while one runtime implementation
must still validate input.

`Batches` implements `__iter__` and `__next__`; `Transaction` implements the
context-manager protocol and never suppresses exceptions. `NonBlankText`
demonstrates descriptor lookup through both the class and an instance.
`ApiRecord` shows cooperative `super()` following the method resolution order
(MRO), not simply “calling the parent.”

`@runtime_checkable` verifies only that an object has named protocol members; it
does not run a static type checker or validate full signatures. TypedDict and
overloads also disappear as enforcement unless runtime code validates them.

Metaclasses can customize class creation, but they complicate inheritance and
tooling. The solution uses `__init_subclass__` for a small registry, which is
usually sufficient. Metaclasses remain appropriate for framework-level class
construction when simpler hooks cannot express the invariant.

Edge cases include exhausted iterators, zero batch sizes, exceptions inside a
transaction, corrupted descriptor storage, conflicting mixin order, and a
runtime object that has a `name` attribute of the wrong semantic type.

---

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Reasoning before implementation

The solution aligns each static promise with explicit runtime behavior and implements Python hooks through their observable protocol.

1. **`Protocol` + `TypeVar`:** expresses the smallest structural interface and its variance from producer/consumer behavior.
2. **`@overload` signatures + one implementation:** gives static callers precise return types while runtime code still validates the discriminant.
3. **`__iter__` / `__next__` / `__enter__` / `__exit__`:** participates in Python-managed lifecycle and must honor exhaustion, cleanup, and exception rules.
4. **Prove the failure boundary:** Exercise one normal case, one boundary case, and one injected failure without relying on hidden state.

**Alternative:** Abstract base classes provide nominal inheritance and shared implementation; concrete types may be clearer when substitution is not needed.

**Trade-off:** Precise generics/overloads improve editor and review guarantees but increase API complexity and maintenance when runtime behavior is broad.

**Failure boundary:** `bool` as `int`, `NotImplemented` versus `False`, descriptor class access, exception suppression, MRO cooperation, and mutable variance require tests.

**Verification:** Run static positive/negative cases, validate decoded data at runtime, test iterator/context/descriptor boundaries, and trace MRO plus cleanup under exceptions.

### Verification micro-example

Run this small, deterministic case before adapting the reference to a
larger system. It gives the reasoning above an executable anchor:

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

The reference implementation is one defensible contract, not a license
to copy internal steps into every system. Preserve the observable
guarantees and repeat the failure tests when adapting it.

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reference

Use this map after an honest attempt. The executable implementation remains
[`py_lang_01_typing_data_model_solution.py`](py_lang_01_typing_data_model_solution.py); this section explains the
contract, evidence, alternatives, and edge cases behind every numbered task.

### Exercise 1 — Complete and type the overloaded parser

**Prompt recap:** Implement the three promised return behaviors. Reject boolean text other than `true` and `false`. In VS Code, inspect the inferred types of `parse_scalar("12", "int")` and `parse_scalar("true", "bool")`. A variable typed as arbitrary `str` needs a broader overload or prior narrowing; overloads do not inspect future runtime text.

**Reference reasoning:** Static types describe public contracts while Python's runtime data model still governs iteration, descriptors, context management, equality, and class creation. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Complete and type the overloaded parser — assert parse_scalar('12','int') returns int 12, parse_scalar('true','bool') returns bool True, and the float case has its declared type; invalid Boolean text raises ValueError and mypy reveals the two Literal-call result types without errors.

### Exercise 2 — Implement the iterator protocol

**Prompt recap:** Complete `Batches.__next__`. Return tuples, advance the offset, and raise `StopIteration` only after exhaustion. Test empty input and a final partial batch.

**Reference reasoning:** Static types describe public contracts while Python's runtime data model still governs iteration, descriptors, context management, equality, and class creation. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Implement the iterator protocol — assert list(Batches([],2)) == [] and list(Batches([1,2,3],2)) == [(1,2),(3,)]; after exhaustion, another next() must raise StopIteration without changing the stored offset.

### Exercise 3 — Reason about variance

**Prompt recap:** Assign `SequenceReader[str]` to `Reader[object]`; this is safe because callers only read. Explain why a mutable repository of strings cannot be treated as a repository of objects: a caller might store an integer into it.

**Reference reasoning:** Static types describe public contracts while Python's runtime data model still governs iteration, descriptors, context management, equality, and class creation. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Reason about variance — save a mypy transcript where SequenceReader[str] is accepted as Reader[object] and a mutable string repository is rejected as a mutable object repository; include the concrete unsafe integer-write counterexample.

### Exercise 4 — Model events with TypedDict

**Prompt recap:** Add a third event with a unique literal `kind`. Update `describe_event` and let the checker identify unhandled or invalid fields. Add runtime validation at the JSON boundary; TypedDict alone does not validate decoded data.

**Reference reasoning:** Static types describe public contracts while Python's runtime data model still governs iteration, descriptors, context management, equality, and class creation. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Model events with TypedDict — mypy must reject one missing/invalid field and accept all three literal-kind events after exhaustive dispatch; runtime validation returns immutable domain data for valid JSON and a named error for an unknown kind.

### Exercise 5 — Exercise context-manager failure

**Prompt recap:** Append inside `Transaction`, then raise. Verify the target remains unchanged and the exception propagates. Returning true from `__exit__` would suppress it; this implementation deliberately returns false.

**Reference reasoning:** Static types describe public contracts while Python's runtime data model still governs iteration, descriptors, context management, equality, and class creation. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Exercise context-manager failure — start with target ['before'], append inside Transaction, and raise a sentinel RuntimeError; assert the target remains ['before'] and the same exception object/message reaches the caller.

### Exercise 6 — Trace descriptor lookup

**Prompt recap:** Compare `Customer.name` with `Customer("Ada").name`. Explain why the descriptor returns itself for class access. Corrupt the private field deliberately and observe the runtime type guard.

**Reference reasoning:** Static types describe public contracts while Python's runtime data model still governs iteration, descriptors, context management, equality, and class creation. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Trace descriptor lookup — assert Customer.name returns the descriptor object, Customer('Ada').name returns 'Ada', and corrupting the private storage with a non-string makes instance access raise the declared TypeError.

### Exercise 7 — Draw the MRO

**Prompt recap:** Print `ApiRecord.__mro__`. Predict the label before calling it. Every mixin uses cooperative `super()`; directly naming a parent would skip or duplicate work.

**Reference reasoning:** Static types describe public contracts while Python's runtime data model still governs iteration, descriptors, context management, equality, and class creation. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Draw the MRO — record the predicted label and ApiRecord.__mro__ before invocation, then assert the observed label matches and every expected mixin/class appears once in MRO order.

### Exercise 8 — Bound metaclass use

**Prompt recap:** Add a second `Handler` with `__init_subclass__`. Survey how a metaclass could enforce the same rule, then state why the hook is preferable here. Use a metaclass only when class-creation behavior cannot be expressed by descriptors, decorators, or subclass hooks.

**Reference reasoning:** Static types describe public contracts while Python's runtime data model still governs iteration, descriptors, context management, equality, and class creation. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** Bound metaclass use — add a second Handler with init subclass; survey how a metaclass could enforce the same rule, then state why the hook is preferable here; use a metaclass only when class-creation behavior cannot be expressed by descriptors, decorators, or subclass hooks.

### Exercise 9 — design a structural Protocol

**Prompt recap:** Define a minimal generic `Serializer[T]` Protocol and implement JSON and text serializers without inheritance. Add a consumer and let mypy reject one incompatible implementation.

**Reasoning path:** Protocol methods express only what the consumer needs. Use a 3.11-compatible TypeVar and abstract collection input types.

Declare `dumps(value: T) -> str` (and `loads` only if the consumer needs it).
Concrete serializers satisfy the protocol structurally. Type the consumer
against `Serializer[Record]`, not a concrete class, and include one deliberately
mis-typed example under a checker-only fixture.

Avoid `runtime_checkable` unless runtime `isinstance` is truly required; it
checks attribute presence, not full generic signatures or semantic behavior.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** design a structural Protocol — run mypy positive cases for JSON/text Serializer implementations and one negative implementation with the wrong return type; the consumer must work without inheritance and the negative fixture must fail at the protocol boundary.

### Exercise 10 — preserve signatures with ParamSpec

**Prompt recap:** Write a timing decorator that preserves arbitrary positional/keyword parameters and return type, injects a log sink/clock for tests, and re-raises the wrapped exception unchanged.

**Reasoning path:** Use `ParamSpec`, a return `TypeVar`, `Callable[P, R]`, and `functools.wraps`.

The wrapper accepts `*args: P.args` and `**kwargs: P.kwargs`, returns `R`, and
records elapsed time in `finally` so failures are observable without being
translated. The sink receives function name and finite nonnegative duration;
it never receives arguments that may contain secrets.

Use an injected monotonic clock for deterministic tests. Mypy should reveal the
same signature and return type at decorated call sites.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** preserve signatures with ParamSpec — mypy must preserve the wrapped positional/keyword signature and return type; injected fake clock/sink tests assert one duration record, functools.wraps metadata, return-value parity, and unchanged exception propagation.

### Exercise 11 — narrow decoded data safely

**Prompt recap:** Implement a `TypeGuard` that validates a decoded JSON object as a specific TypedDict, including exact required keys, value types, and the bool-versus-int edge case.

**Reasoning path:** `isinstance(True, int)` is true. Test bool explicitly before accepting integer fields, and reject unknown keys if the boundary is strict.

Accept `object`, require `dict`, compare key sets, then validate each field
without coercion. Return `TypeGuard[Payload]` only after all runtime checks.
Downstream code then narrows statically while the boundary remains honest.

For richer errors, a parser returning a validated dataclass or raising a typed
exception is often better than a Boolean guard. TypedDict alone performs no
runtime validation.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** narrow decoded data safely — assert the TypeGuard accepts exactly the required-key/type fixture and rejects missing, extra, wrong-type, and bool-in-an-int-field fixtures; inside the accepted branch mypy must narrow to the TypedDict.

### Exercise 12 — choose frozen, slots, and hash semantics

**Prompt recap:** Create a small value-object dataclass and compare mutable, frozen, slotted, and `unsafe_hash` choices. Use it as a dictionary key and show which combinations preserve hash invariants.

**Reasoning path:** Hashable keys must not change equality-relevant fields while stored. `unsafe_hash` does not make mutation safe.

For an immutable value object, `@dataclass(frozen=True, slots=True)` provides
generated equality and a compatible hash while avoiding an instance `__dict__`.
Attempted field assignment fails. A mutable equality-bearing dataclass should
normally remain unhashable.

Do not use frozen as a security boundary: contained mutable objects can still
change. Validate fields in `__post_init__` with `object.__setattr__` only for
carefully documented normalization.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** choose frozen, slots, and hash semantics — print equality/hash behavior for mutable, frozen, slotted, and unsafe_hash variants; assert only a value whose equality fields cannot mutate remains a retrievable dictionary key after attempted mutation.

### Exercise 13 — implement cooperative equality

**Prompt recap:** Implement `__eq__` for a value type so unrelated types receive `NotImplemented`, subclasses behave deliberately, and hashing remains consistent. Contrast this with returning `False` immediately.

**Reasoning path:** `NotImplemented` lets Python try the reflected comparison and then fall back appropriately; it is not the same object as `NotImplementedError`.

Compare only values under the declared compatible-type policy and otherwise
return `NotImplemented`. If exact type identity is required, check
`type(other) is type(self)`; if subclasses share semantics, use a documented
`isinstance` policy. Equal objects must produce equal hashes.

Test both operand orders, an unrelated object, and subclass behavior. Avoid
raising merely because comparison is unsupported.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** implement cooperative equality — assert equal values have equal hashes, unequal values compare false, direct __eq__ with an unrelated type returns NotImplemented, and one reflected-comparison fixture demonstrates why returning False immediately differs.

### Exercise 14 — evolve a typed serialization boundary

**Prompt recap:** Version a discriminated TypedDict union, add an optional field to one event, and parse old/new payloads into immutable domain objects. Define unknown-version and unknown-kind failures.

**Reasoning path:** Narrow on literal version/kind only after runtime validation. Keep wire payloads separate from trusted domain types.

The parser first validates an outer version and kind, then validates the exact
fields for that variant and constructs a dataclass. An additive optional field
gets an explicit default for old payloads. Unknown version or kind raises a
typed boundary error carrying no raw sensitive payload.

Exhaustive `assert_never` helps the checker find an unhandled trusted union
variant, but it cannot replace validation of arbitrary decoded JSON.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** evolve a typed serialization boundary — parse one old and one new payload into the expected immutable objects; assert the optional field default, round-trip version/kind, and named unknown-version and unknown-kind errors.

### Exercise 15 — trace weak references and caches

**Prompt recap:** Compare a normal dictionary cache with `WeakValueDictionary` for objects that support weak references. Drop strong references, force collection only as an observation, and state when cache disappearance is acceptable.

**Reasoning path:** Weak caches do not own values. Slotted classes need weak-reference support explicitly, and collection timing is not a business deadline.

Use weak caching only when recomputation is safe and identity is an
optimization, not required state. Keep one strong reference to prove lookup,
delete it, run `gc.collect()` in the bounded teaching test, and observe that
the entry may disappear. A normal dict retains the object.

Never base correctness on immediate garbage collection. Explicit lifecycle or
bounded LRU/TTL policy is preferable for resources and deterministic eviction.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** trace weak references and caches — after dropping the only strong reference, assert the normal cache still owns its value while WeakValueDictionary may lose it after collection; test a slotted class with and without weak-reference support.

### Exercise 16 — review typing compatibility

**Prompt recap:** Change a public function from accepting `Sequence[str]` to `list[str]`, and another return from `list[str]` to `Sequence[str]`. Analyze source compatibility for callers and implement a deprecation-safe alternative.

**Reasoning path:** Parameter types are consumer inputs; narrowing them breaks callers. Return types can often become more specific, not arbitrarily more abstract.

Requiring `list` rejects tuple and other valid sequence callers, so retain the
abstract `Sequence` unless mutation is required; if mutation is required,
introduce a new API or copy internally. Changing a promised concrete list
return to arbitrary Sequence can break callers that append.

Use checker fixtures representing downstream calls, runtime tests, and a
documented migration window. Type-checker compatibility and runtime semantics
must both be preserved.

**Common trap:** A type annotation is not runtime validation, and clever metaclass/mixin/descriptor machinery can obscure ownership, variance, or method-resolution behavior.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** review typing compatibility — save mypy caller fixtures showing the Sequence[str]-to-list[str] parameter narrowing breaks a valid tuple caller and analyze the return change separately; test the compatibility wrapper and its deprecation warning.
