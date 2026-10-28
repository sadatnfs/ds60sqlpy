"""python-lang-02: Scope, Closures, and Observable Decorator Contracts.

Run two offline worked examples, then implement the six separate task functions.
Each classroom Run starts a fresh process; saved source and notes persist.
The opening examples do not call the unimplemented exercises.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any


# Exercise 1: Bind independent offsets.
# Inputs: A tuple of exact integers such as (2, -1, 0); bool is not an integer for these
# | contracts.
# Expected: Return one function per offset in input order. Each function adds its own offset to
# | an exact integer argument. Empty input returns (). Reject invalid offsets before
# | returning functions, and invalid call arguments, with ValueError.
# Verify: Calling all three functions with 10 returns (12, 9, 10). Call them again in reverse
# | order to expose accidental shared late binding.
def bind_offsets(offsets: tuple[int, ...]) -> tuple[Callable[[int], int], ...]:
    """Bind independent offsets.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement bind_offsets")


# Exercise 2: Keep private accumulated state.
# Inputs: An exact integer start and later exact integer increments, including negative
# | increments.
# Expected: Return a closure with private running state. Calls add the increment and return the
# | new total. Separate factory calls never share state. Reject a malformed start or
# | increment with ValueError; a rejected increment must not change the stored total.
# Verify: A total starting at 5 returns 7 then 4 for increments 2 and -3. After rejecting
# | True, increment 0 still returns 4; a second factory starting at 5 still returns 5.
def make_running_total(start: int = 0) -> Callable[[int], int]:
    """Keep private accumulated state.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement make_running_total")


# Exercise 3: Read a live configuration binding.
# Inputs: A caller-owned dictionary whose keys are nonempty strings and values exact integers,
# | plus an existing nonempty key.
# Expected: Validate the initial dictionary without copying or modifying it. Return a closure
# | that reads the current value of the selected key on each call. A missing key raises
# | KeyError, including after later deletion; a malformed current value raises
# | ValueError. Replacing a separate caller variable with a new dictionary does not
# | replace the captured dictionary.
# Verify: A captured limit initially 3 becomes 8 after config["limit"] = 8. Deleting limit
# | raises KeyError; reinserting a string raises ValueError. Record the caller
# | dictionary before and after construction to prove no mutation.
def make_live_lookup(config: dict[str, int], key: str) -> Callable[[], int]:
    """Read a live configuration binding.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement make_live_lookup")


# Exercise 4: Trace a call without changing its result.
# Inputs: A list for observation and an ordinary synchronous callable to decorate. Calls may
# | use positional and keyword arguments or raise an Exception.
# Expected: Return a decorator that preserves metadata with functools.wraps. Append call:NAME
# | before invocation, then return:NAME on success or raise:NAME:TYPE on an Exception.
# | Return the original result and re-raise the same exception object. Do not catch
# | BaseException control signals.
# Verify: For a function named divide, division by zero yields ["call:divide",
# | "raise:divide:ZeroDivisionError"]. Inspect __name__, __doc__, __wrapped__, and
# | inspect.signature; assert an injected exception is the identical object.
def trace_calls(events: list[str]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Trace a call without changing its result.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement trace_calls")


# Exercise 5: Make decorator order observable.
# Inputs: An ordinary one-integer function. The wrapper accepts one exact integer that must be
# | at least zero.
# Expected: Preserve function metadata. Reject negative integers, bool, and nonintegers with
# | ValueError before calling the wrapped function. Otherwise return its result
# | unchanged. Compare tracing outside validation with validation outside tracing;
# | neither order may call the body for invalid input.
# Verify: A traced outer wrapper records call and raise for -1. An outer validator records no
# | trace for -1. On 0 both call the body once and return its actual result.
def require_nonnegative(function: Callable[[int], int]) -> Callable[[int], int]:
    """Make decorator order observable.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement require_nonnegative")


# Exercise 6: Snapshot and compose a pipeline.
# Inputs: A finite caller-owned sequence of callables. Each stage accepts and returns an
# | integer. Input stage storage may be changed after construction.
# Expected: Snapshot the stage sequence and reject a noncallable stage with ValueError at
# | construction. Return a function applying stages from left to right. Empty stages
# | return their input unchanged. Forward a stage exception immediately without calling
# | later stages; never mutate the supplied sequence.
# Verify: For add-two then multiply-three, input 4 gives 18, while reversed stages give 14.
# | Clearing the original list afterward does not change the first pipeline; record that
# | a later stage was not called after a deliberate error.
def compose_stages(stages: Sequence[Callable[[int], int]]) -> Callable[[int], int]:
    """Snapshot and compose a pipeline.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement compose_stages")


def worked_examples() -> None:
    def worked_binding() -> None:
        late = []
        early = []
        for label in ("red", "blue"):
            late.append(lambda: label)  # noqa: B023 - deliberate late-binding contrast
            early.append(lambda saved=label: saved)
        assert [read() for read in late] == ["blue", "blue"]
        assert [read() for read in early] == ["red", "blue"]
        print("Late binding:", [read() for read in late])
        print("Definition defaults:", [read() for read in early])

    worked_binding()

    from functools import wraps

    events = []

    def announce(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            events.append("before")
            try:
                return function(*args, **kwargs)
            finally:
                events.append("after")

        return wrapper

    @announce
    def reciprocal(value):
        """Return one divided by value."""
        return 1 / value

    assert reciprocal(2) == 0.5
    try:
        reciprocal(0)
    except ZeroDivisionError:
        pass
    else:
        raise AssertionError("The wrapper hid the failure")
    assert events == ["before", "after", "before", "after"]
    assert reciprocal.__name__ == "reciprocal"
    print("Decorator events:", events)


if __name__ == "__main__":
    worked_examples()
    print("Examples passed. Implement and verify the six separate task functions.")
