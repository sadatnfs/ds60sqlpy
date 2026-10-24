"""python-lang-01 learner lab: typing and the Python data model.

Professional learner deep dive (python-lang-01)
------------------------------------------------

Mental model:
Type hints describe contracts for static tools and readers; they do not automatically validate
runtime data. A Protocol is structural: a class satisfies it by providing required members,
without inheritance. Covariance is safe for values a container only produces; mutable read/write
containers are generally invariant.  Python syntax such as iteration, context management,
attribute access, and `super()` is powered by data-model protocols. Implementing these hooks
means honoring their full lifecycle: `StopIteration`, exception propagation and cleanup,
descriptor class/instance access, and cooperative method-resolution order.

API/boundary anatomy:
* `Protocol` + `TypeVar`: expresses the smallest structural interface and its variance from
  producer/consumer behavior.
* `@overload` signatures + one implementation: gives static callers precise return types while
  runtime code still validates the discriminant.
* `__iter__` / `__next__` / `__enter__` / `__exit__`: participates in Python-managed lifecycle
  and must honor exhaustion, cleanup, and exception rules.

Micro-example A — show structural compatibility without inheritance::

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

Expected: `PlainRecord` never inherits from `Named`; static structural matching uses its
          available member.

Micro-example B — honor iterator exhaustion and partial batches::

    iterator = iter([("a", "b"), ("c",)])
    assert next(iterator) == ("a", "b")
    assert next(iterator) == ("c",)
    try:
        next(iterator)
    except StopIteration:
        print("iterator exhausted exactly once input ended")

Expected: The final partial batch is a valid value; only the following call signals exhaustion.

Debugging rule: Run mypy/pyright on intended and intentionally invalid uses, then separately
                test runtime boundary validation and every data-model lifecycle edge.

The snippets demonstrate mechanics only. They do not complete the
numbered TODOs below; implement those from their stated contracts and
prove normal, boundary, and failure behavior.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from typing import Generic, Literal, TypeVar, overload

T = TypeVar("T")


@overload
def parse_scalar(text: str, kind: Literal["int"]) -> int: ...


@overload
def parse_scalar(text: str, kind: Literal["bool"]) -> bool: ...


@overload
def parse_scalar(text: str, kind: Literal["text"]) -> str: ...


def parse_scalar(
    text: str,
    kind: Literal["int", "bool", "text"],
) -> int | bool | str:
    """TODO: implement the runtime behavior promised by the overloads."""

    raise NotImplementedError("complete parse_scalar")


class Batches(Generic[T], Iterator[tuple[T, ...]]):
    """Iterator exercise that makes ``iter`` and ``next`` explicit."""

    def __init__(self, items: Sequence[T], size: int) -> None:
        if size < 1:
            raise ValueError("size must be positive")
        self._items = items
        self._size = size
        self._offset = 0

    def __iter__(self) -> Batches[T]:
        return self

    def __next__(self) -> tuple[T, ...]:
        """TODO: return the next tuple and raise StopIteration when exhausted."""

        raise NotImplementedError("complete Batches.__next__")


def self_check() -> None:
    checks: tuple[tuple[str, Callable[[], object]], ...] = (
        ("overloaded parser", lambda: parse_scalar("12", "int")),
        ("iterator protocol", lambda: list(Batches([1, 2, 3], 2))),
    )
    for label, call in checks:
        try:
            print(label, "->", call())
        except NotImplementedError:
            print("TODO:", label)


# === Numbered professional practice ===
#
# Attempt every exercise before opening solutions. Keep evidence in a copy
# under .learning/ or in tests; do not overwrite the reference solution.
# Full acceptance checks and progressive hints:
# companion-guides/py_lang_01_typing_data_model.md
#
# Exercise 1 — Complete and type the overloaded parser
# Prompt: Implement the three promised return behaviors. Reject boolean text other than
# `true` and `false`. In VS Code, inspect the inferred types of
# `parse_scalar("12", "int")` and `parse_scalar("true", "bool")`. A variable typed as
# arbitrary `str` needs a broader overload or prior narrowing.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 2 — Implement the iterator protocol
# Prompt: Complete `Batches.__next__`. Return tuples, advance the offset, and raise
# `StopIteration` only after exhaustion. Test empty input and a final partial batch.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 3 — Reason about variance
# Prompt: Assign `SequenceReader[str]` to `Reader[object]`; this is safe because callers
# only read. Explain why a mutable repository of strings cannot be treated as a repository
# of objects: a caller might store an integer into it.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 4 — Model events with TypedDict
# Prompt: Add a third event with a unique literal `kind`. Update `describe_event` and let
# the checker identify unhandled or invalid fields. Add runtime validation at the JSON
# boundary; TypedDict alone does not validate decoded data.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 5 — Exercise context-manager failure
# Prompt: Append inside `Transaction`, then raise. Verify the target remains unchanged and
# the exception propagates. Returning true from `__exit__` would suppress it; this
# implementation deliberately returns false.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 6 — Trace descriptor lookup
# Prompt: Compare `Customer.name` with `Customer("Ada").name`. Explain why the descriptor
# returns itself for class access. Corrupt the private field deliberately and observe the
# runtime type guard.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 7 — Draw the MRO
# Prompt: Print `ApiRecord.__mro__`. Predict the label before calling it. Every mixin uses
# cooperative `super()`; directly naming a parent would skip or duplicate work.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 8 — Bound metaclass use
# Prompt: Add a second `Handler` with `__init_subclass__`. Survey how a metaclass could
# enforce the same rule, then state why the hook is preferable here. Use a metaclass only
# when class-creation behavior cannot be expressed by descriptors, decorators, or subclass
# hooks.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 9 — design a structural Protocol
# Prompt: Define a minimal generic `Serializer[T]` Protocol and implement JSON and text
# serializers without inheritance. Add a consumer and let mypy reject one incompatible
# implementation.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 10 — preserve signatures with ParamSpec
# Prompt: Write a timing decorator that preserves arbitrary positional/keyword parameters
# and return type, injects a log sink/clock for tests, and re-raises the wrapped exception
# unchanged.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 11 — narrow decoded data safely
# Prompt: Implement a `TypeGuard` that validates a decoded JSON object as a specific
# TypedDict, including exact required keys, value types, and the bool-versus-int edge
# case.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 12 — choose frozen, slots, and hash semantics
# Prompt: Create a small value-object dataclass and compare mutable, frozen, slotted, and
# `unsafe_hash` choices. Use it as a dictionary key and show which combinations preserve
# hash invariants.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 13 — implement cooperative equality
# Prompt: Implement `__eq__` for a value type so unrelated types receive `NotImplemented`,
# subclasses behave deliberately, and hashing remains consistent. Contrast this with
# returning `False` immediately.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 14 — evolve a typed serialization boundary
# Prompt: Version a discriminated TypedDict union, add an optional field to one event, and
# parse old/new payloads into immutable domain objects. Define unknown-version and
# unknown-kind failures.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 15 — trace weak references and caches
# Prompt: Compare a normal dictionary cache with `WeakValueDictionary` for objects that
# support weak references. Drop strong references, force collection only as an
# observation, and state when cache disappearance is acceptable.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 16 — review typing compatibility
# Prompt: Change a public function from accepting `Sequence[str]` to `list[str]`, and
# another return from `list[str]` to `Sequence[str]`. Analyze source compatibility for
# callers and implement a deprecation-safe alternative.
# Verify: add a boundary check and explain the failure policy.
#
# === End numbered professional practice ===

if __name__ == "__main__":
    self_check()
