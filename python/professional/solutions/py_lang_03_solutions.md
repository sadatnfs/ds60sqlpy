# python-lang-03: Explained solutions

The [executable reference](py_lang_03_solution.py) implements the six contracts and
contains independent expected-value, failure, and lifetime assertions. Read the
[learner guide](../companion-guides/py_lang_03.md) for the complete run workflow and
attempt each [learner function](../lessons/py_lang_03.py) before comparing. The
reference runs entirely offline in the prepared Docker Python classroom; its
assertions are behavioral evidence for these fixtures, not a claim about unseen
learner work or external system acceptance.

## Exercise 1: Consume an exact prefix

**Inputs:** A caller-owned iterator and an exact nonnegative integer count.

**Expected:** Consume exactly count items and return a tuple, without probing for an additional item or closing the caller iterator. Zero consumes nothing. Reject a malformed count with ValueError before pulling. If the source ends too early, raise ValueError after consuming the available items; consumption cannot be rolled back.

**Verify:** From iter([4, 5, 6]), requesting two returns (4, 5) and next(source) is 6. Requesting three from two items raises ValueError. A counted source confirms zero pulls for count 0 or an invalid count.

The exact-prefix implementation validates count before the first next call and then performs one next per requested position. It does not test for exhaustion beyond that prefix. This matters because iterators are stateful: a caller expects the first unrequested item to remain available. The independent check leaves six in a source after consuming four and five. A comprehension over the whole source followed by slicing would produce the correct tuple but consume too much. If the iterator ends early, the function converts StopIteration into the documented ValueError. The already consumed items cannot be restored generally; buffering them in the returned error would still not rewind the original source. Count zero creates an empty tuple without touching the source, and invalid counts fail before consumption. The function borrows the iterator and never closes it.

## Exercise 2: Yield bounded chunks lazily

**Inputs:** An iterable and an exact positive integer chunk size.

**Expected:** Validate size when chunked is called, before accessing the source. Return an iterator producing tuples of at most size items, including a final partial chunk. Do not preconsume source elements before the first next call, omit empty chunks, and do not close a caller-owned iterator.

**Verify:** The input [1, 2, 3, 4, 5] with size 2 yields (1, 2), (3, 4), (5,). Check the source pull count is 0 at construction and 2 after only the first chunk; size 0 raises immediately.

chunked is deliberately an ordinary outer function rather than a generator function. Its positive-size validator executes immediately when called, including for an empty source. The inner generate function defers iterator acquisition and all pulling until next is requested. islice consumes at most the selected size, and tuple materializes only that chunk. The loop yields nonempty chunks and stops when no values remain; a short final tuple is retained. Peak chunk storage is proportional to size, although materializing all yielded chunks in a caller would of course retain more. The spy fixture proves construction performs zero pulls and the first result performs exactly two. Closing the returned generator leaves a borrowed source available at its next item. A direct yield-from of a borrowed generator would need separate consideration because delegation can forward close.

## Exercise 3: Build overlapping neighbors

**Inputs:** A finite or unbounded iterable of integers; empty and singleton inputs are allowed.

**Expected:** Return a lazy iterator of adjacent overlapping pairs in source order, retaining only one previous value. Empty and singleton inputs yield nothing. The first result consumes two values; each later result consumes exactly one additional value. Leave a caller-owned source open on early close.

**Verify:** [4, 7, 9] yields (4, 7), (7, 9). A spy iterator confirms three pulls for two results; after closing the pair generator, the underlying source still yields its next value.

The neighbor generator first attempts to obtain one previous item. Empty input returns immediately, and singleton input ends without producing a pair. Each for-loop step supplies one current item; the yielded pair joins that current item with the previous one, then updates previous for the next step. Thus [4, 7, 9] gives overlapping pairs (4, 7) and (7, 9), rather than disjoint chunks. Only one prior value is retained besides the current iteration value. The source stays caller-owned, and an explicit close of the outer generator does not forward close through an ordinary loop. Tests use a source with another available item to prove it was not overconsumed. Raising StopIteration explicitly inside this generator would not be the right empty-input exit, because Python converts such escaping generator termination into RuntimeError.

## Exercise 4: Give a generator explicit ownership

**Inputs:** A text string and an observation list. The implementation owns a new io.StringIO created inside its generator body.

**Expected:** Acquire the StringIO only when iteration first starts and append open. Yield physical lines with exactly one final newline character removed, preserving other spaces and blank lines. Close the stream and append close in finally on exhaustion or explicit generator close. Closing an unstarted generator acquires nothing.

**Verify:** For " a \n\nb\n", list output is [" a ", "", "b"] with events ["open", "close"]. After one next call the events are ["open"]; generator.close() appends close once.

The StringIO constructor is inside the generator body, so simply calling text_lines acquires nothing. After the first advance the log records open, and iteration removes exactly one trailing newline from each physical line. It does not use strip, which would discard meaningful surrounding spaces and conceal blank-line structure. A finally block closes the owned stream and records close on exhaustion, explicit close after a yield, or an error while the frame is active. Calling close twice on the already closed generator does not execute the frame again, so the log remains balanced. Closing an unstarted generator records nothing because the acquisition was never reached. The independent checks compare both yielded strings and event sequences. Correct text alone cannot demonstrate closure; correct closure alone cannot demonstrate preservation of whitespace.

## Exercise 5: Parse without taking resource ownership

**Inputs:** A caller-owned iterator of physical text lines, including blank lines and signed decimal integers accepted by int.

**Expected:** Lazily skip whitespace-only lines and convert the rest with int. On malformed nonblank input raise ValueError with the message invalid integer on line N, where N counts all physical lines starting at one. Do not close the source, even when parsing fails or the parser is closed.

**Verify:** [" 2 ", "", "-5"] yields 2 and -5. ["", "bad"] raises ValueError("invalid integer on line 2"). A tracked source stays open until its owner explicitly closes it.

The parser enumerates source lines before filtering, starting at one. That preserves physical positions even when a blank line is skipped. For nonblank text, int supplies the standard signed-decimal conversion policy, and a conversion failure is wrapped in the exact line-number message with the original error retained as its cause. The source belongs to the caller: parsing stops at the invalid line but does not close the upstream generator or stream. The executable reference opens a text source containing bad followed by seven, catches the parser's failure, and confirms the source can still yield seven. Only the owner closes it afterward. A parser with a with-closing block around its argument would violate borrowing. Keeping whitespace removal in this conversion stage also leaves text_lines useful for nonnumerical consumers.

## Exercise 6: Close an owned early-stop pipeline

**Inputs:** Text and an exact nonnegative requested count. This function owns the text_lines and parse_int_lines generators it creates.

**Expected:** Return at most count parsed integers, preserving order and skipping blank lines. Always close owned generators on early stop, exhaustion, or parse failure. Count zero returns () without opening a stream. Invalid counts raise ValueError before acquisition. Malformed content after the requested prefix remains unconsumed.

**Verify:** For "1\n\n2\nbad\n", count 2 returns (1, 2) with ["open", "close"]. Count 3 raises the line-4 ValueError with the same balanced events. Count 0 leaves an empty event list.

first_numbers creates both pipeline generators, so it accepts ownership of them. It validates count first and returns immediately for zero, ensuring that invalid or unnecessary work never acquires a stream. For positive requests, nested closing contexts ensure the parser closes before the line generator, while the line generator's finally closes StringIO. islice asks for at most count numerical results. Blank lines may require more physical input pulls, but content after the selected numerical prefix is not parsed. In the fixture, count two returns one and two without touching bad on line four. Count three reaches that line, raises the exact ValueError, and still ends with open/close events. Asking for more numbers than exist returns the available prefix. These event checks prove normal exhaustion, early stop, and error cleanup separately without depending on garbage collection.

The following compact check runs in the executable reference namespace after its function definitions:

```python
events = []
assert first_numbers("1\n2\nbad", 2, events) == (1, 2)
assert events == ["open", "close"]
```

Run the complete reference from fresh process state when comparing results. A change to an input policy must be deliberate and reflected in its assertions; merely suppressing an exception or deleting a cleanup check does not satisfy the original contract.
