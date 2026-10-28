"""Executable references for python-lang-02, with behavioral assertions."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any


def _integer(value: object) -> int:
    if type(value) is not int:
        raise ValueError("Expected an exact integer")
    return value


# Exercise 1: Bind independent offsets.
def bind_offsets(offsets: tuple[int, ...]) -> tuple[Callable[[int], int], ...]:
    for offset in offsets:
        _integer(offset)

    def bind(offset: int) -> Callable[[int], int]:
        def add(value: int) -> int:
            return _integer(value) + offset

        return add

    return tuple(bind(offset) for offset in offsets)


# Exercise 2: Keep private accumulated state.
def make_running_total(start: int = 0) -> Callable[[int], int]:
    total = _integer(start)

    def increment(value: int) -> int:
        nonlocal total
        checked = _integer(value)
        total += checked
        return total

    return increment


# Exercise 3: Read a live configuration binding.
def make_live_lookup(config: dict[str, int], key: str) -> Callable[[], int]:
    if (
        not isinstance(config, dict)
        or not isinstance(key, str)
        or not key
        or any(not isinstance(name, str) or not name for name in config)
    ):
        raise ValueError("Expected a dictionary with nonempty string keys")
    for value in config.values():
        _integer(value)
    _integer(config[key])

    def lookup() -> int:
        return _integer(config[key])

    return lookup


# Exercise 4: Trace a call without changing its result.
def trace_calls(events: list[str]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(function: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            events.append(f"call:{function.__name__}")
            try:
                result = function(*args, **kwargs)
            except Exception as error:
                events.append(f"raise:{function.__name__}:{type(error).__name__}")
                raise
            events.append(f"return:{function.__name__}")
            return result

        return wrapper

    return decorate


# Exercise 5: Make decorator order observable.
def require_nonnegative(function: Callable[[int], int]) -> Callable[[int], int]:
    @wraps(function)
    def wrapper(value: int) -> int:
        checked = _integer(value)
        if checked < 0:
            raise ValueError("Expected a nonnegative integer")
        return function(checked)

    return wrapper


# Exercise 6: Snapshot and compose a pipeline.
def compose_stages(stages: Sequence[Callable[[int], int]]) -> Callable[[int], int]:
    frozen = tuple(stages)
    if not all(callable(stage) for stage in frozen):
        raise ValueError("Each stage must be callable")

    def pipeline(value: int) -> int:
        for stage in frozen:
            value = stage(value)
        return value

    return pipeline


def _raises(kind: type[Exception], action: Callable[[], Any]) -> Exception:
    try:
        action()
    except kind as error:
        return error
    raise AssertionError(f"Expected {kind.__name__}")


def verify_examples() -> None:
    adders = bind_offsets((2, -1, 0))
    assert tuple(add(10) for add in adders) == (12, 9, 10)
    assert tuple(add(10) for add in adders[::-1]) == (10, 9, 12)
    assert bind_offsets(()) == ()
    _raises(ValueError, lambda: bind_offsets((True,)))
    _raises(ValueError, lambda: adders[0](True))
    running = make_running_total(5)
    separate = make_running_total(5)
    assert (running(2), running(-3)) == (7, 4)
    _raises(ValueError, lambda: running(True))
    assert running(0) == 4 and separate(0) == 5
    _raises(ValueError, lambda: make_running_total("5"))  # type: ignore[arg-type]  # Deliberately invalid input.
    config = {"limit": 3}
    before = config.copy()
    lookup = make_live_lookup(config, "limit")
    assert config == before and lookup() == 3
    config["limit"] = 8
    assert lookup() == 8
    old_config = config
    config = {"limit": 99}
    assert lookup() == 8 and old_config == {"limit": 8}
    del old_config["limit"]
    _raises(KeyError, lookup)
    old_config["limit"] = "invalid"  # type: ignore[assignment]  # Probe runtime validation.
    _raises(ValueError, lookup)
    _raises(ValueError, lambda: make_live_lookup({"": 1}, ""))
    events: list[str] = []
    failure = RuntimeError("original")

    def divide(value: int, *, divisor: int = 1) -> float:
        """Divide a value by a supplied divisor."""
        if divisor == -1:
            raise failure
        return value / divisor

    wrapped = trace_calls(events)(divide)
    assert wrapped(8, divisor=2) == 4
    assert events == ["call:divide", "return:divide"]
    assert _raises(RuntimeError, lambda: wrapped(8, divisor=-1)) is failure
    assert events[-2:] == ["call:divide", "raise:divide:RuntimeError"]
    assert wrapped.__name__ == divide.__name__ and wrapped.__doc__ == divide.__doc__
    # Callable describes calls; wraps also attaches this runtime metadata.
    assert wrapped.__wrapped__ is divide  # type: ignore[attr-defined]
    assert inspect.signature(wrapped) == inspect.signature(divide)
    body: list[int] = []

    def square(value: int) -> int:
        body.append(value)
        return value * value

    outer_trace: list[str] = []
    inner_trace: list[str] = []
    traced_validator = trace_calls(outer_trace)(require_nonnegative(square))
    validated_trace = require_nonnegative(trace_calls(inner_trace)(square))
    _raises(ValueError, lambda: traced_validator(-1))
    _raises(ValueError, lambda: validated_trace(-1))
    assert body == [] and inner_trace == []
    assert outer_trace == ["call:square", "raise:square:ValueError"]
    assert traced_validator(0) == 0 and validated_trace(0) == 0
    assert body == [0, 0]
    stages = [lambda value: value + 2, lambda value: value * 3]
    pipeline = compose_stages(stages)
    assert pipeline(4) == 18 and compose_stages(stages[::-1])(4) == 14
    stages.clear()
    assert pipeline(4) == 18 and compose_stages([])(4) == 4
    _raises(ValueError, lambda: compose_stages([None]))  # type: ignore[list-item]  # Deliberately invalid stage.
    later: list[int] = []

    def broken(value: int) -> int:
        raise failure

    def observe(value: int) -> int:
        later.append(value)
        return value

    assert _raises(RuntimeError, lambda: compose_stages([broken, observe])(1)) is failure
    assert later == []
    print("All six scope, closure, and decorator contracts passed.")


if __name__ == "__main__":
    verify_examples()
