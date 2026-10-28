# Iterators, Generator Pipelines, and Resource Lifetime

**Stable ID:** `python-lang-03`. Plan about three hours for reading, tracing, and
independent implementation. Historical day 87 is a stable catalog
label, not a study deadline.

## How to run this lesson

Run `./classroom` from the repository root and open **Python** in the shared
`/classroom` directory. Select this lesson, read its Python capability notice,
and use the saved coding pad. Windows uses the same launcher in WSL 2.
Docker provides Python and all required standard-library modules. Paste the
complete [learner script](../lessons/py_lang_03.py) into the pad, save, and Run.
The output pane shows two worked-example observations and a completion message.
The six task functions intentionally raise `NotImplementedError` until you
implement them; the opening examples do not call those functions.

The browser saves source, notes, and results in its learning volume, while
every Run starts a fresh Python process. Include imports, fixtures, and checks
in the submitted source. In-memory closures, iterators, tasks, and event loops
do not survive the run. Save the source that reproduces your evidence. Running
the demonstrations proves only those cases, not completion of the six tasks.
Every input here is an original, bounded local fixture; no download, server,
database, credentials, or additional package is needed.

### Optional prepared contributor route

After the separate [contributor setup](../../../CONTRIBUTING.md), run
`uv run --no-sync python python/professional/lessons/py_lang_03.py` from the
repository root. This host interpreter and checkout do not read the browser's
Docker learning volume. See the [classroom guide](../../../docs/classroom-experience.md)
for source, result history, and navigation. This optional command is not a
second installation requirement for ordinary learners.

## Level and prerequisites

- **Level:** Advanced Python language practice, using Python 3.11-compatible syntax.
- **Direct prerequisite:** `python-lang-02`, [companion guide](py_lang_02.md).
- **Direct prerequisite:** `python-08`, [companion guide](../../ds-60day/companion-guides/day08_files_json_csv_context.md).
- **Artifacts:** [learner](../lessons/py_lang_03.py), [explained answers](../solutions/py_lang_03_solutions.md), [executable reference](../solutions/py_lang_03_solution.py).

You should already write functions and loops, reason about closure state, and use with for file cleanup. The new boundary is suspended iteration and explicit ownership across stages; no external streaming system is assumed.

## Learning objectives

Trace exactly how many values an operation consumes, distinguish an iterable
from its current iterator, and use lazy computation without losing ownership
of a resource. Build chunk and overlapping-neighbor generators with bounded
working memory. Parse physical lines while retaining useful error positions,
then assemble a pipeline that closes what it creates on success, exhaustion,
early return, and parse failure.

## Vocabulary and concepts

- **Iterable:** An object from which `iter(value)` obtains an iterator. A list
  can provide a new iterator each time. An existing generator normally returns
  itself, so passing it twice does not create two independent traversals.
- **Iterator:** A stateful producer advanced by `next`. It returns one item or
  raises `StopIteration` when exhausted. Exhaustion is part of this protocol,
  not a missing-data value that can be replaced arbitrarily with zero.
- **Generator:** A convenient iterator implemented with a function containing
  `yield`. Calling that function creates a generator; its body starts at the
  first advance. Each `yield` suspends the frame with its local bindings intact.
- **Laziness:** Deferring work until a consumer asks for a result. It changes
  when validation, acquisition, and failure happen. Lazy output does not
  automatically mean bounded input reading or safe resource cleanup.
- **Ownership:** Responsibility for ending a resource's lifetime. A parser can
  borrow a source from its caller while another function owns a source it
  creates. Those functions need different behavior when they stop early.
- **Finalization:** The cleanup path reached by ordinary exhaustion, an error,
  or explicit generator `close`. A `finally` block runs when a suspended
  generator is closed. Closing one that never started does not run its body,
  so no acquisition should be assumed to have happened.

`next(source)` is a state transition. If you consume two values and then fail,
a caller cannot generally undo those pulls. The exact-prefix task therefore
reports insufficient input after consuming what was available. It must avoid
probing a third value when exactly two were requested. A source may represent
a sensor or a much larger sequence, so an apparently harmless extra probe can
matter even when the returned tuple looks correct.

A generator function defers all of its body, including parameter checks. For
the chunk task, invalid size must fail at the ordinary function call. Use an
outer non-generator function for immediate validation and return an inner
generator for deferred consumption. Acquiring the iterator inside that inner
body also avoids invoking a source's `__iter__` before consumption begins.

`yield from inner` delegates iteration and parts of the generator protocol,
including forwarding `close` to an inner generator. That is useful when the
outer generator owns the inner one. It can be wrong when the source belongs to
the caller and should remain usable after the consumer closes. An ordinary
`for` loop can borrow a source without forwarding that explicit close signal.
Choose the mechanism from the ownership contract rather than its brevity.

## Worked example / walkthrough

### Advancing a stream changes future observations

Write the three values you expect in `pulled` after each assertion. The list
is deliberately external to the generator so it records when work happens.
`list(stream)` requests the remaining items; it does not rewind an exhausted
generator. This fixture has three bounded values and no files or remote data.

```python
pulled = []
def measured():
    for value in (3, 5, 8):
        pulled.append(value)
        yield value

stream = measured()
assert pulled == []
assert next(stream) == 3
assert pulled == [3]
assert list(stream) == [5, 8]
assert list(stream) == []
print("Pulled once:", pulled)
```

**Expected:** Construction leaves `pulled` empty. A single `next` records only
`3`. The first materialization returns `[5, 8]`; the second returns `[]`, while
`pulled` remains `[3, 5, 8]`. A fresh call to `measured()` would create a distinct
traversal. Keeping a generator object and keeping a recipe that creates one are
therefore different API choices.

### An early consumer must end the lifetime it owns

Stopping after the first item does not exhaust a generator. In the example
below, `contextlib.closing` supplies an explicit exit action: call `close` on
the object when the `with` block exits. The resource is represented by an event
log rather than a real file so the lifetime is visible and repeatable. In the
exercise you will replace that model with a real local `StringIO` stream.

```python
from contextlib import closing

events = []
def owned_letters():
    events.append("open")
    try:
        yield "a"
        yield "b"
    finally:
        events.append("close")

with closing(owned_letters()) as letters:
    assert next(letters) == "a"
    assert events == ["open"]
assert events == ["open", "close"]
print("Early-stop cleanup:", events)
```

**Expected:** Inside the block the log contains only `open`; afterward it is
`['open', 'close']`. A `break` by itself has no general promise to close a
retained generator. Do not rely on an interpreter's reference-counting timing
or garbage collection to supply the missing ownership decision. A caller can
still hold the object after leaving a loop.

`StringIO` provides a text stream in memory. Iteration yields physical lines
including their ending newline when present. `removesuffix("\n")` removes one
newline without erasing the meaningful spaces in `" a "` or the blank line
between two numbers. Later parsing can deliberately use `strip` to decide
whether a line contains a number. Keeping those two responsibilities separate
makes line preservation and numerical policy independently testable.

## Exercises

Record pull counts, output tuples, exception messages, and acquisition/close
events separately. A correct tuple with an open owned stream is incomplete.
Use small fresh sources for failure cases because consuming an iterator cannot
be rolled back. None of these tasks requires reading a learner's personal files.

### Exercise 1: Consume an exact prefix

**Inputs:** A caller-owned iterator and an exact nonnegative integer count.

**Expected:** Consume exactly count items and return a tuple, without probing for an additional item or closing the caller iterator. Zero consumes nothing. Reject a malformed count with ValueError before pulling. If the source ends too early, raise ValueError after consuming the available items; consumption cannot be rolled back.

**Verify:** From iter([4, 5, 6]), requesting two returns (4, 5) and next(source) is 6. Requesting three from two items raises ValueError. A counted source confirms zero pulls for count 0 or an invalid count.

### Exercise 2: Yield bounded chunks lazily

**Inputs:** An iterable and an exact positive integer chunk size.

**Expected:** Validate size when chunked is called, before accessing the source. Return an iterator producing tuples of at most size items, including a final partial chunk. Do not preconsume source elements before the first next call, omit empty chunks, and do not close a caller-owned iterator.

**Verify:** The input [1, 2, 3, 4, 5] with size 2 yields (1, 2), (3, 4), (5,). Check the source pull count is 0 at construction and 2 after only the first chunk; size 0 raises immediately.

### Exercise 3: Build overlapping neighbors

**Inputs:** A finite or unbounded iterable of integers; empty and singleton inputs are allowed.

**Expected:** Return a lazy iterator of adjacent overlapping pairs in source order, retaining only one previous value. Empty and singleton inputs yield nothing. The first result consumes two values; each later result consumes exactly one additional value. Leave a caller-owned source open on early close.

**Verify:** [4, 7, 9] yields (4, 7), (7, 9). A spy iterator confirms three pulls for two results; after closing the pair generator, the underlying source still yields its next value.

### Exercise 4: Give a generator explicit ownership

**Inputs:** A text string and an observation list. The implementation owns a new io.StringIO created inside its generator body.

**Expected:** Acquire the StringIO only when iteration first starts and append open. Yield physical lines with exactly one final newline character removed, preserving other spaces and blank lines. Close the stream and append close in finally on exhaustion or explicit generator close. Closing an unstarted generator acquires nothing.

**Verify:** For " a \n\nb\n", list output is [" a ", "", "b"] with events ["open", "close"]. After one next call the events are ["open"]; generator.close() appends close once.

### Exercise 5: Parse without taking resource ownership

**Inputs:** A caller-owned iterator of physical text lines, including blank lines and signed decimal integers accepted by int.

**Expected:** Lazily skip whitespace-only lines and convert the rest with int. On malformed nonblank input raise ValueError with the message invalid integer on line N, where N counts all physical lines starting at one. Do not close the source, even when parsing fails or the parser is closed.

**Verify:** [" 2 ", "", "-5"] yields 2 and -5. ["", "bad"] raises ValueError("invalid integer on line 2"). A tracked source stays open until its owner explicitly closes it.

### Exercise 6: Close an owned early-stop pipeline

**Inputs:** Text and an exact nonnegative requested count. This function owns the text_lines and parse_int_lines generators it creates.

**Expected:** Return at most count parsed integers, preserving order and skipping blank lines. Always close owned generators on early stop, exhaustion, or parse failure. Count zero returns () without opening a stream. Invalid counts raise ValueError before acquisition. Malformed content after the requested prefix remains unconsumed.

**Verify:** For "1\n\n2\nbad\n", count 2 returns (1, 2) with ["open", "close"]. Count 3 raises the line-4 ValueError with the same balanced events. Count 0 leaves an empty event list.

## Self-check

Explain why `list(generator)` twice differs from creating two generators.
Describe when a chunk size error should be visible and how an outer function
can make that happen. Draw the ownership chain for `first_numbers`: the top
function owns the two generators, the line generator owns its StringIO, and
the parser borrows the line source. Identify which layer is responsible for
closing each object on the line-4 parse error.

**Verify:** Retain evidence for a source still yielding `6` after a two-item
prefix, exactly two pulls after the first chunk, the overlapping pairs
`(4, 7)` and `(7, 9)`, preserved `" a "` and `""` lines, and the exact message
`invalid integer on line 4`. The event transcript must be balanced after both
early success and failure, while count zero must produce no acquisition.

## Common pitfalls

If invalid size raises only when iterating, the validator is inside a generator
body. Inspect where `yield` appears, including in branches that seem unrelated
to validation. If the first chunk drains the entire source, look for `list`
or `tuple` wrapping the input instead of a bounded prefix. If a pair generator
skips values, check whether it advances twice per result rather than retaining
one previous item.

If a parser closes a borrowed source, inspect delegation or an unexpected
context manager around caller-owned input. Conversely, if the top-level prefix
function leaves only `open` in the log, it probably assumed exhausting a short
prefix also exhausts the line source. Add explicit closure at the owning layer.
If line numbers omit blanks, count physical input lines before filtering.
If `" a "` becomes `"a"` in the line generator, whitespace normalization has
crossed into the wrong stage.

Returning from a generator uses `StopIteration` internally. Explicitly raising
`StopIteration` inside its body can surface as `RuntimeError` under Python's
generator rules. End with `return` when a singleton has no pair. These bounded
memory examples teach lifetime and pull behavior; they do not claim to process
arbitrary file encodings, network streams, or asynchronous input.

## Next step

Continue to [`python-lang-04`: Structured Asyncio, Cancellation, and Context Ownership](py_lang_04.md)
after completing the direct concurrency prerequisite there. Cancellation adds
an externally requested exit to the same ownership reasoning. Revisit
[files and context managers](../../ds-60day/companion-guides/day08_files_json_csv_context.md)
if `with` or text streams remain unfamiliar. Before proceeding, describe a
case in which every returned value was correct but the resource behavior was
wrong, and name the observation that exposed it.


## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-lang-03: Iterators, Generator Pipelines, and Resource Lifetime.
Read python/professional/companion-guides/py_lang_03.md and python/professional/lessons/py_lang_03.py. Direct prerequisites: python-lang-02, python-08.
Keep the advanced lesson self-contained for someone new to its specific mechanisms. Explain iterators, generators, laziness, ownership, closing, cleanup, ask me to predict a concrete result, then let me attempt it. Give one hint at a time and review my exact value, exception, event, and cleanup evidence. Ask retrieval questions in my own words. Do not read solutions/ until I request comparison or have made an honest attempt.
Use only prepared local offline fixtures in the Docker Python classroom; preserve saved source and notes. No SQL or external service is involved. Done when all six contracts and boundary cases have inspected evidence, and I can explain the timing and ownership decision behind each result.
```
