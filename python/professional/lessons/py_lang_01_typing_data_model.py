"""python-lang-01 learner lab: typing and the Python data model."""

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
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 2 — Implement the iterator protocol
# Prompt: Complete `Batches.__next__`. Return tuples, advance the offset, and raise
# `StopIteration` only after exhaustion. Test empty input and a final partial batch.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 3 — Reason about variance
# Prompt: Assign `SequenceReader[str]` to `Reader[object]`; this is safe because callers
# only read. Explain why a mutable repository of strings cannot be treated as a repository
# of objects: a caller might store an integer into it.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 4 — Model events with TypedDict
# Prompt: Add a third event with a unique literal `kind`. Update `describe_event` and let
# the checker identify unhandled or invalid fields. Add runtime validation at the JSON
# boundary; TypedDict alone does not validate decoded data.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 5 — Exercise context-manager failure
# Prompt: Append inside `Transaction`, then raise. Verify the target remains unchanged and
# the exception propagates. Returning true from `__exit__` would suppress it; this
# implementation deliberately returns false.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 6 — Trace descriptor lookup
# Prompt: Compare `Customer.name` with `Customer("Ada").name`. Explain why the descriptor
# returns itself for class access. Corrupt the private field deliberately and observe the
# runtime type guard.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 7 — Draw the MRO
# Prompt: Print `ApiRecord.__mro__`. Predict the label before calling it. Every mixin uses
# cooperative `super()`; directly naming a parent would skip or duplicate work.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 8 — Bound metaclass use
# Prompt: Add a second `Handler` with `__init_subclass__`. Survey how a metaclass could
# enforce the same rule, then state why the hook is preferable here. Use a metaclass only
# when class-creation behavior cannot be expressed by descriptors, decorators, or subclass
# hooks.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 9 — design a structural Protocol
# Prompt: Define a minimal generic `Serializer[T]` Protocol and implement JSON and text
# serializers without inheritance. Add a consumer and let mypy reject one incompatible
# implementation.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 10 — preserve signatures with ParamSpec
# Prompt: Write a timing decorator that preserves arbitrary positional/keyword parameters
# and return type, injects a log sink/clock for tests, and re-raises the wrapped exception
# unchanged.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 11 — narrow decoded data safely
# Prompt: Implement a `TypeGuard` that validates a decoded JSON object as a specific
# TypedDict, including exact required keys, value types, and the bool-versus-int edge
# case.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 12 — choose frozen, slots, and hash semantics
# Prompt: Create a small value-object dataclass and compare mutable, frozen, slotted, and
# `unsafe_hash` choices. Use it as a dictionary key and show which combinations preserve
# hash invariants.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 13 — implement cooperative equality
# Prompt: Implement `__eq__` for a value type so unrelated types receive `NotImplemented`,
# subclasses behave deliberately, and hashing remains consistent. Contrast this with
# returning `False` immediately.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 14 — evolve a typed serialization boundary
# Prompt: Version a discriminated TypedDict union, add an optional field to one event, and
# parse old/new payloads into immutable domain objects. Define unknown-version and
# unknown-kind failures.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 15 — trace weak references and caches
# Prompt: Compare a normal dictionary cache with `WeakValueDictionary` for objects that
# support weak references. Drop strong references, force collection only as an
# observation, and state when cache disappearance is acceptable.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 16 — review typing compatibility
# Prompt: Change a public function from accepting `Sequence[str]` to `list[str]`, and
# another return from `list[str]` to `Sequence[str]`. Analyze source compatibility for
# callers and implement a deprecation-safe alternative.
# Evidence: add a boundary check and explain the failure policy.
#
# === End numbered professional practice ===

if __name__ == "__main__":
    self_check()
