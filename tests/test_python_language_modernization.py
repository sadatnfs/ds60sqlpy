"""Independent behavioral, lifetime, and cancellation oracles for language units."""

from __future__ import annotations

import asyncio
import inspect
import itertools
import re
import runpy
from collections import Counter
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from functools import lru_cache
from io import StringIO
from pathlib import Path
from typing import Any, cast

import pytest

from ds60sqlpy.catalog import Catalog, Lesson
from scripts.audit_lesson_depth import measure_lesson
from scripts.audit_practice import count_practice

ROOT = Path(__file__).resolve().parents[1]
PREREQUISITES = {
    2: ("python-lang-01", "python-11"),
    3: ("python-lang-02", "python-08"),
    4: ("python-lang-03", "python-pro-02"),
}


@lru_cache(maxsize=3)
def reference(number: int) -> dict[str, Any]:
    return runpy.run_path(
        str(ROOT / f"python/professional/solutions/py_lang_{number:02d}_solution.py")
    )


def run_async(operation: Callable[[], Awaitable[None]]) -> None:
    async def bounded() -> None:
        async with asyncio.timeout(5):
            await operation()

    asyncio.run(bounded())


@pytest.mark.parametrize("number", [2, 3, 4])
def test_complete_surfaces_have_matching_six_contracts_and_executable_examples(number: int) -> None:
    stem = f"py_lang_{number:02d}"
    lesson = Lesson.from_mapping(
        {
            "id": f"python-lang-{number:02d}",
            "track": "python",
            "day": 84 + number,
            "title": "Python language mechanics",
            "level": "advanced",
            "phase": "Python language mechanics",
            "estimated_minutes": 180,
            "prerequisites": list(PREREQUISITES[number]),
            "lesson_path": f"python/professional/lessons/{stem}.py",
            "guide_path": f"python/professional/companion-guides/{stem}.md",
            "solution_paths": [
                f"python/professional/solutions/{stem}_solutions.md",
                f"python/professional/solutions/{stem}_solution.py",
            ],
            "dependency_group": "core",
            "network": "offline",
            "runner": "python",
        }
    )
    assert not measure_lesson(Catalog(ROOT, [lesson]), lesson).issues
    for relative in (lesson.lesson_path, lesson.guide_path, *lesson.solution_paths):
        assert count_practice(ROOT / relative, solution="solutions/" in relative) == 6
        assert "\u2014" not in (ROOT / relative).read_text()
    learner = runpy.run_path(str(ROOT / lesson.lesson_path))
    learner["worked_examples"]()
    reference(number)["verify_examples"]()
    guide = (ROOT / lesson.guide_path).read_text()
    examples = re.findall(r"```python\n(.*?)\n```", guide, flags=re.S)
    assert len(examples) == 2
    for index, example in enumerate(examples, 1):
        exec(compile(example, f"{stem}:worked-{index}", "exec"), {"__name__": "__main__"})
    explained = (ROOT / lesson.solution_paths[0]).read_text()
    for example in re.findall(r"```python\n(.*?)\n```", explained, flags=re.S):
        exec(compile(example, f"{stem}:explained", "exec"), dict(reference(number)))


def test_offset_factories_and_accumulators_match_independent_integer_oracles() -> None:
    functions = reference(2)
    for offsets in itertools.product(range(-2, 3), repeat=3):
        adders = functions["bind_offsets"](offsets)
        for value in (-4, 0, 9):
            assert tuple(add(value) for add in adders) == tuple(
                value + offset for offset in offsets
            )
            assert tuple(add(value) for add in adders[::-1]) == tuple(
                value + offset for offset in offsets[::-1]
            )
    assert functions["bind_offsets"](()) == ()
    for invalid in (True, False, 1.0, "1", None):
        with pytest.raises(ValueError):
            functions["bind_offsets"]((1, invalid))
        with pytest.raises(ValueError):
            functions["bind_offsets"]((1,))[0](invalid)
        with pytest.raises(ValueError):
            functions["make_running_total"](invalid)
    increments = [2, -4, 0, 8, -1]
    first, second = functions["make_running_total"](3), functions["make_running_total"](-2)
    expected = 3
    for increment in increments:
        expected += increment
        assert first(increment) == expected
        with pytest.raises(ValueError):
            first(True)
        assert first(0) == expected
        assert second(0) == -2


def test_live_lookup_preserves_object_binding_and_exposes_mutations() -> None:
    factory = reference(2)["make_live_lookup"]
    original = {"limit": 3, "other": 4}
    before = original.copy()
    lookup = factory(original, "limit")
    assert original == before and lookup() == 3
    for value in (-5, 0, 27):
        original["limit"] = value
        assert lookup() == value
    replacement = {"limit": 99}
    assert replacement != original and lookup() == 27
    del original["limit"]
    with pytest.raises(KeyError, match="limit"):
        lookup()
    original["limit"] = True
    with pytest.raises(ValueError):
        lookup()
    for config, key in [
        ({"": 1}, ""),
        ({"limit": True}, "limit"),
        ({"limit": 1}, ""),
        ({1: 2}, "limit"),
    ]:
        with pytest.raises(ValueError):
            factory(config, key)
    with pytest.raises(KeyError):
        factory({}, "missing")


def test_decorators_preserve_identity_error_and_order_evidence() -> None:
    functions = reference(2)
    events: list[str] = []
    error = RuntimeError("same instance")

    def evaluate(value: int, *, multiplier: int = 2) -> int:
        """Documented original callable."""
        if value < 0:
            raise error
        return value * multiplier

    wrapped = functions["trace_calls"](events)(evaluate)
    assert wrapped(3, multiplier=4) == 12
    assert events == ["call:evaluate", "return:evaluate"]
    assert wrapped.__name__ == "evaluate" and wrapped.__doc__ == evaluate.__doc__
    assert wrapped.__wrapped__ is evaluate and inspect.signature(wrapped) == inspect.signature(
        evaluate
    )
    with pytest.raises(RuntimeError) as caught:
        wrapped(-1)
    assert caught.value is error
    assert events[-2:] == ["call:evaluate", "raise:evaluate:RuntimeError"]

    class ControlSignal(BaseException):
        pass

    control = ControlSignal()

    def stopped() -> int:
        raise control

    events.clear()
    with pytest.raises(ControlSignal) as caught_control:
        functions["trace_calls"](events)(stopped)()
    assert caught_control.value is control and events == ["call:stopped"]
    body: list[int] = []

    def echo(value: int) -> int:
        body.append(value)
        return value + 10

    outer_events: list[str] = []
    inner_events: list[str] = []
    first = functions["trace_calls"](outer_events)(functions["require_nonnegative"](echo))
    second = functions["require_nonnegative"](functions["trace_calls"](inner_events)(echo))
    for invalid in (-1, True, 1.0):
        with pytest.raises(ValueError):
            first(invalid)
        with pytest.raises(ValueError):
            second(invalid)
    assert body == [] and inner_events == []
    assert outer_events == ["call:echo", "raise:echo:ValueError"] * 3
    assert first(0) == second(0) == 10 and body == [0, 0]


def test_pipeline_snapshots_order_and_stops_after_failure() -> None:
    compose = reference(2)["compose_stages"]
    stages = [lambda value: value + 2, lambda value: value * 3]
    first, second = compose(stages), compose(stages[::-1])
    before = stages.copy()
    assert stages == before
    stages.clear()
    for value in range(-4, 5):
        assert first(value) == (value + 2) * 3
        assert second(value) == value * 3 + 2
        assert compose([])(value) == value
    later: list[int] = []
    error = LookupError("stop")

    def broken(value: int) -> int:
        raise error

    def observe(value: int) -> int:
        later.append(value)
        return value

    with pytest.raises(LookupError) as caught:
        compose([broken, observe])(7)
    assert caught.value is error and later == []
    with pytest.raises(ValueError):
        compose([None])


class TrackedIterator:
    def __init__(self, values: list[Any]):
        self.values = iter(values)
        self.pulls = 0
        self.iterations = 0
        self.closed = False

    def __iter__(self) -> TrackedIterator:
        self.iterations += 1
        return self

    def __next__(self) -> Any:
        self.pulls += 1
        return next(self.values)

    def close(self) -> None:
        self.closed = True


def test_exact_prefix_has_no_extra_probe_or_ownership_transfer() -> None:
    take = reference(3)["take_exact"]
    for count in range(5):
        source = TrackedIterator(list(range(7)))
        assert take(source, count) == tuple(range(count))
        assert source.pulls == count and not source.closed
        assert next(source) == count
    for invalid in (-1, True, 2.5):
        source = TrackedIterator([1])
        with pytest.raises(ValueError):
            take(source, invalid)
        assert source.pulls == 0 and not source.closed
    source = TrackedIterator([1, 2])
    with pytest.raises(ValueError):
        take(source, 3)
    assert source.pulls == 3 and not source.closed
    assert list(source) == []


def test_chunks_and_neighbors_match_slice_oracles_without_eager_consumption() -> None:
    functions = reference(3)
    for length in range(8):
        values = list(range(length))
        for size in range(1, 5):
            source = TrackedIterator(values)
            chunks = functions["chunked"](source, size)
            assert source.pulls == source.iterations == 0
            expected = [tuple(values[start : start + size]) for start in range(0, length, size)]
            assert list(chunks) == expected
            assert not source.closed
        assert list(functions["neighbor_pairs"](values)) == list(
            zip(values, values[1:], strict=False)
        )
    source = TrackedIterator([1, 2, 3, 4, 5])
    chunks = functions["chunked"](source, 2)
    assert next(chunks) == (1, 2) and source.pulls == 2
    chunks.close()
    assert not source.closed and next(source) == 3
    source = TrackedIterator([1, 2, 3, 4, 5])
    pairs = functions["neighbor_pairs"](source)
    assert source.pulls == 0
    assert next(pairs) == (1, 2) and source.pulls == 2
    assert next(pairs) == (2, 3) and source.pulls == 3
    pairs.close()
    assert not source.closed and next(source) == 4
    for invalid in (0, -1, True):
        source = TrackedIterator([1])
        with pytest.raises(ValueError):
            functions["chunked"](source, invalid)
        assert source.pulls == source.iterations == 0


def test_owned_line_generator_closes_actual_stream_on_all_started_exits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    function = reference(3)["text_lines"]
    streams: list[StringIO] = []

    def tracked(text: str) -> StringIO:
        stream = StringIO(text)
        streams.append(stream)
        return stream

    monkeypatch.setitem(function.__globals__, "StringIO", tracked)
    events: list[str] = []
    source = function(" a \n\nb\n", events)
    assert events == [] and streams == []
    assert list(source) == [" a ", "", "b"]
    assert events == ["open", "close"] and streams[-1].closed
    events.clear()
    source = function("a\nb", events)
    assert next(source) == "a" and not streams[-1].closed
    source.close()
    source.close()
    assert events == ["open", "close"] and streams[-1].closed
    events.clear()
    source = function("a\nb", events)
    next(source)
    failure = RuntimeError("injected consumer failure")
    with pytest.raises(RuntimeError) as caught:
        source.throw(failure)
    assert caught.value is failure and streams[-1].closed and events == ["open", "close"]
    events.clear()
    previous_count = len(streams)
    source = function("not acquired", events)
    source.close()
    assert not events and len(streams) == previous_count


def test_parser_keeps_physical_positions_and_borrows_source() -> None:
    parse = reference(3)["parse_int_lines"]
    source = TrackedIterator([" ", "2", "", "-5", "bad", "8"])
    parser = parse(source)
    assert source.pulls == 0
    assert next(parser) == 2 and source.pulls == 2
    assert next(parser) == -5 and source.pulls == 4
    with pytest.raises(ValueError, match="^invalid integer on line 5$"):
        next(parser)
    assert not source.closed and next(source) == "8"
    source = TrackedIterator(["1", "2"])
    parser = parse(source)
    assert next(parser) == 1
    parser.close()
    assert not source.closed and next(source) == "2"
    assert list(parse(iter([]))) == []


def test_owned_prefix_closes_on_early_success_exhaustion_and_parse_failure() -> None:
    first = reference(3)["first_numbers"]
    cases = [("1\n\n2\nbad\n", 2, (1, 2)), ("1\n", 5, (1,)), ("\n \n", 4, ())]
    for text, count, expected in cases:
        events: list[str] = []
        assert first(text, count, events) == expected
        assert events == ["open", "close"]
    events = []
    with pytest.raises(ValueError, match="^invalid integer on line 4$"):
        first("1\n\n2\nbad\n", 3, events)
    assert events == ["open", "close"]
    events = []
    assert first("bad", 0, events) == () and not events
    for invalid in (-1, True, 1.5):
        with pytest.raises(ValueError):
            first("1", invalid, events)
        assert not events


def test_structured_results_preserve_input_order_under_reversed_completion() -> None:
    async def check() -> None:
        functions = reference(4)
        ready = {value: asyncio.Event() for value in (1, 2, 3)}
        release = {value: asyncio.Event() for value in (1, 2, 3)}
        finished = {value: asyncio.Event() for value in (1, 2, 3)}
        completion: list[int] = []

        async def work(value: int) -> int:
            ready[value].set()
            await release[value].wait()
            completion.append(value)
            finished[value].set()
            return value * 10

        result = asyncio.create_task(functions["ordered_group"]((1, 2, 3), work))
        for event in ready.values():
            await event.wait()
        for value in (3, 2, 1):
            release[value].set()
            await finished[value].wait()
        assert await result == (10, 20, 30) and completion == [3, 2, 1]
        assert await functions["ordered_group"]((), work) == ()
        assert asyncio.all_tasks() == {asyncio.current_task()}

    run_async(check)


def test_group_failure_awaits_sibling_cleanup_and_preserves_failure_leaf() -> None:
    async def check() -> None:
        functions = reference(4)
        acquired = asyncio.Event()
        events: list[str] = []
        failure = ValueError("bad input")

        async def work(value: int) -> int:
            if value == 0:
                try:
                    events.append("sibling acquired")
                    acquired.set()
                    await asyncio.Event().wait()
                finally:
                    await asyncio.sleep(0)
                    events.append("sibling closed")
            await acquired.wait()
            raise failure

        with pytest.raises(ExceptionGroup) as caught:
            await functions["ordered_group"]((0, 1), work)
        assert caught.value.exceptions == (failure,)
        assert events == ["sibling acquired", "sibling closed"]
        assert asyncio.all_tasks() == {asyncio.current_task()}

    run_async(check)


def test_limited_group_bounds_real_activity_and_balances_cancellation_events() -> None:
    async def check() -> None:
        functions = reference(4)
        active = peak = 0

        async def square(value: int) -> int:
            nonlocal active, peak
            active += 1
            peak = max(peak, active)
            try:
                await asyncio.sleep(0)
                return value * value
            finally:
                active -= 1

        events: list[tuple[str, int]] = []
        assert await functions["limited_group"](tuple(range(8)), square, 2, events) == tuple(
            value * value for value in range(8)
        )
        assert peak == 2 and active == 0
        balance = 0
        for event, _ in events:
            balance += 1 if event == "start" else -1
            assert 0 <= balance <= 2
        assert balance == 0
        assert Counter(value for event, value in events if event == "start") == Counter(range(8))
        assert Counter(value for event, value in events if event == "finish") == Counter(range(8))
        ready = asyncio.Event()
        acquired: list[int] = []

        async def blocked(value: int) -> int:
            acquired.append(value)
            if len(acquired) == 2:
                ready.set()
            await asyncio.Event().wait()
            return value

        events.clear()
        task = asyncio.create_task(functions["limited_group"](tuple(range(8)), blocked, 2, events))
        await ready.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert len(acquired) == 2
        assert Counter(value for event, value in events if event == "start") == Counter(
            value for event, value in events if event == "finish"
        )
        for invalid in (0, -1, True, 2.0):
            with pytest.raises(ValueError):
                await functions["limited_group"]((), square, invalid, [])
        assert asyncio.all_tasks() == {asyncio.current_task()}

    run_async(check)


def test_deadlines_distinguish_timeout_failure_and_external_cancellation() -> None:
    async def check() -> None:
        deadline = reference(4)["with_deadline"]
        calls: list[str] = []

        async def immediate() -> int:
            calls.append("called")
            return 7

        assert await deadline(immediate, 1) == 7
        calls.clear()
        for invalid in (0, -1, True, float("inf"), float("-inf"), float("nan"), "1"):
            with pytest.raises(ValueError):
                await deadline(immediate, invalid)
        assert not calls
        closed: list[str] = []
        ready = asyncio.Event()

        async def blocked() -> int:
            try:
                ready.set()
                await asyncio.Event().wait()
                return 0
            finally:
                await asyncio.sleep(0)
                closed.append("closed")

        with pytest.raises(TimeoutError):
            await deadline(blocked, 0.01)
        assert closed == ["closed"]
        ready.clear()
        closed.clear()
        task = asyncio.create_task(deadline(blocked, 3))
        await ready.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert closed == ["closed"]
        failure = ValueError("unchanged")

        async def broken() -> int:
            raise failure

        with pytest.raises(ValueError) as caught:
            await deadline(broken, 1)
        assert caught.value is failure
        assert asyncio.all_tasks() == {asyncio.current_task()}

    run_async(check)


def test_cancellable_wait_has_explicit_success_and_cancelled_exits() -> None:
    async def check() -> None:
        wait = reference(4)["cancellable_wait"]
        ready, release = asyncio.Event(), asyncio.Event()
        events: list[str] = []
        task = asyncio.create_task(wait(ready, release, events))
        await ready.wait()
        assert events == ["acquired"]
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert task.cancelled() and events == ["acquired", "closed"]
        events.clear()
        release.set()
        assert await wait(asyncio.Event(), release, events) == "released"
        assert events == ["acquired", "closed"]

    run_async(check)


def test_group_inspection_retains_depth_first_leaf_order_subclasses_and_duplicates() -> None:
    describe = reference(4)["describe_failures"]

    class SpecificValueError(ValueError):
        pass

    group = ExceptionGroup(
        "outer",
        [
            RuntimeError("first"),
            ExceptionGroup(
                "nested", [ValueError("same"), TypeError("middle"), SpecificValueError("same")]
            ),
            ValueError("last"),
        ],
    )
    assert describe(group) == (("same", "same", "last"), ("first", "middle"))
    assert describe(ExceptionGroup("all value", [ValueError("v")])) == (("v",), ())
    assert describe(ExceptionGroup("all other", [TypeError("t")])) == ((), ("t",))


def test_context_tokens_restore_previous_binding_on_success_failure_and_cancellation() -> None:
    async def check() -> None:
        functions = reference(4)
        scoped = functions["scoped_request"]
        label = cast(ContextVar[str], functions["REQUEST_ID"])
        token = label.set("parent")
        try:

            async def read() -> str:
                expected = label.get()

                async def child_read() -> str:
                    await asyncio.sleep(0)
                    return label.get()

                child = asyncio.create_task(child_read())
                temporary = label.set("temporary")
                try:
                    assert await child == expected
                finally:
                    label.reset(temporary)
                await asyncio.sleep(0)
                assert label.get() == expected
                return expected

            assert cast(
                list[str], await asyncio.gather(scoped("north", read), scoped("south", read))
            ) == [
                "north",
                "south",
            ]
            assert label.get() == "parent"
            assert await scoped("outer", lambda: scoped("inner", read)) == "inner"
            assert label.get() == "parent"
            failure = RuntimeError("context failure")

            async def broken() -> str:
                assert label.get() == "broken"
                raise failure

            with pytest.raises(RuntimeError) as caught:
                await scoped("broken", broken)
            assert caught.value is failure and label.get() == "parent"
            ready = asyncio.Event()
            restored: list[str] = []

            async def blocked() -> str:
                assert label.get() == "cancel"
                ready.set()
                await asyncio.Event().wait()
                return "unreachable"

            async def owner() -> None:
                try:
                    await scoped("cancel", blocked)
                finally:
                    restored.append(label.get())

            task = asyncio.create_task(owner())
            await ready.wait()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert restored == ["parent"] and label.get() == "parent"
            calls: list[str] = []

            async def observed() -> str:
                calls.append("called")
                return ""

            for invalid in ("", None, 0):
                with pytest.raises(ValueError):
                    await scoped(invalid, observed)
            assert calls == []
            assert asyncio.all_tasks() == {asyncio.current_task()}
        finally:
            label.reset(token)
        assert label.get() == "outside"

    run_async(check)


def test_limited_failure_propagates_after_every_started_operation_finishes() -> None:
    async def check() -> None:
        functions = reference(4)
        acquired = asyncio.Event()
        closed: list[int] = []
        failure = ValueError("limited child failed")

        async def work(value: int) -> int:
            try:
                if value == 0:
                    acquired.set()
                if value == 1:
                    await acquired.wait()
                    raise failure
                await asyncio.Event().wait()
                return value
            finally:
                await asyncio.sleep(0)
                closed.append(value)

        events: list[tuple[str, int]] = []
        with pytest.raises(ExceptionGroup) as caught:
            await functions["limited_group"](tuple(range(6)), work, 2, events)
        assert caught.value.exceptions == (failure,)
        starts = Counter(value for event, value in events if event == "start")
        finishes = Counter(value for event, value in events if event == "finish")
        assert starts == finishes == Counter(closed)
        assert starts[0] == starts[1] == 1
        active = 0
        for event, _ in events:
            active += 1 if event == "start" else -1
            assert 0 <= active <= 2
        assert active == 0
        assert asyncio.all_tasks() == {asyncio.current_task()}

    run_async(check)
