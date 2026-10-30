# Scope, Closures, and Observable Decorator Contracts

**Stable ID:** `python-lang-02`. Plan about three hours for reading, tracing, and
independent implementation. Historical day 86 is a stable catalog
label, not a study deadline.

## How to run this lesson

Run `./classroom` from the repository root and open **Python** in the shared
`/classroom` directory. Select this lesson, read its Python capability notice,
and use the saved coding pad. Windows uses the same launcher in WSL 2.
Docker provides Python and all required standard-library modules. Paste the
complete [learner script](../lessons/py_lang_02.py) into the pad, save, and Run.
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
`uv run --no-sync python python/professional/lessons/py_lang_02.py` from the
repository root. This host interpreter and checkout do not read the browser's
Docker learning volume. See the [classroom guide](../../../docs/classroom-experience.md)
for source, result history, and navigation. This optional command is not a
second installation requirement for ordinary learners.

## Level and prerequisites

- **Level:** Advanced Python language practice, using Python 3.11-compatible syntax.
- **Direct prerequisite:** `python-lang-01`, [companion guide](py_lang_01_typing_data_model.md).
- **Direct prerequisite:** `python-11`, [companion guide](../../ds-60day/companion-guides/day11_debug_logging_profiling.md).
- **Artifacts:** [learner](../lessons/py_lang_02.py), [explained answers](../solutions/py_lang_02_solutions.md), [executable reference](../solutions/py_lang_02_solution.py).

You should already write functions, read exceptions and tests, and distinguish type annotations from runtime checks. This unit deepens the time and ownership of name lookup; it does not assume prior closure or decorator expertise.

## Learning objectives

Explain when a function reads a name, when it keeps a reference, and when it
stores a default value. Build independent closures and private mutable state,
then distinguish that state from a deliberately shared configuration object.
Wrap functions without losing their identity or changing their exception
behavior. Finally, predict decorator order and construct a pipeline whose
meaning survives later edits to the caller's list of stages.

## Vocabulary and concepts

- **Scope:** The region in which a name is resolved. Within a function, Python
  first considers local names, then enclosing function scopes, the module, and
  builtins. This lookup order describes names, not a permanent snapshot of all
  objects visible when the function was defined.
- **Binding:** The association between a name and an object. Assigning a new
  dictionary to `config` changes that binding; mutating `config["limit"]`
  changes the existing dictionary. Those are observably different operations.
- **Closure:** A function that retains access to bindings in an enclosing
  function after that outer call returns. Each outer call can create a new
  private binding. Several functions made within one call can share one binding.
- **Late binding:** A free name is looked up when the function runs. A loop
  usually updates one binding repeatedly, so closures made during that loop can
  all observe its final value. A new factory call supplies a separate scope;
  a default parameter can instead store the current object during definition.
- **Rebinding with nonlocal:** `nonlocal total` tells an inner function that
  assignment should change an existing enclosing binding. Reading `total`
  does not need this declaration. Assigning to it without the declaration
  makes it local and can produce `UnboundLocalError` when it is read first.
- **Decorator:** A callable that receives a function and returns its replacement.
  Writing `@decorate` above `def calculate` is equivalent to rebinding
  `calculate = decorate(calculate)` after definition. Decoration happens once;
  the replacement wrapper runs on every later call.

A function and a callable object are related but distinct. For this lesson the
decorators accept ordinary synchronous functions with names and docstrings.
`*args` collects positional arguments in a tuple, and `**kwargs` collects named
arguments in a dictionary. Passing `function(*args, **kwargs)` forwards those
arguments. It does not make a copy of the objects referenced by them.

`functools.wraps(function)` copies useful metadata and installs `__wrapped__`.
Tools such as `inspect.signature` follow that link by default. Metadata helps
inspection, but does not itself enforce a call's domain. A wrapper still needs
to reject a negative integer before the body executes if that is its contract.
Type annotations likewise describe intended types without checking them.

The integer policy here excludes `bool`, even though Python makes it an integer
subclass. Use that policy consistently when comparing the valid input zero
with the invalid input `False`. This boundary is an exercise choice appropriate
to a numerical counter; another API could choose a different policy explicitly.

## Worked example / walkthrough

### A loop stores functions before their calls happen

Predict both lists before running the following example. The loop name
`label` belongs to the same enclosing call on both iterations. In the second
list, `saved=label` is evaluated when each lambda is created. Strings are
immutable, so keeping that string object gives the two expected labels.
The default technique would retain a reference to a mutable object, not clone
its contents. A factory is often clearer once the behavior needs validation
or several local names.

```python
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
```

**Expected:** The late-bound functions produce `['blue', 'blue']`; the defaults
produce `['red', 'blue']`. If both results match, inspect whether the supposed
late-bound function is actually being called within the loop, before `label`
changes. Moving a call can conceal the bug without fixing the stored callback.

### A wrapper observes both the success and failure route

The wrapper below forwards arguments and uses `finally` for an observation
that must occur on either route. `return` inside `try` does not bypass `finally`.
The division error propagates to the caller, where this small demonstration
expects it. There is no broad fallback returning zero, so an invalid operation
cannot look like a valid numerical answer. This example observes entry/exit;
the independent tracing task asks you to distinguish success from failure.

```python
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
```

**Expected:** The first call returns `0.5`; the second raises
`ZeroDivisionError`. Both produce a balanced before/after pair and the wrapper
retains the name `reciprocal`. The final print contains four strings. Remove
`wraps` experimentally and compare the name, docstring, and inspected signature;
restore it before evaluating the exercise contracts.

Two stacked decorators apply from the bottom upward during definition, while
calls enter the outer wrapper first. For `@trace` above `@validate`, tracing
receives the validated replacement and observes its rejection. Reversing the
lines means validation rejects before tracing begins. Neither arrangement
should invoke the mathematical body for rejected input. Separate body calls
from trace events when investigating this difference.

## Exercises

For each task, first write one prediction, then implement only its learner
function and call it with the stated fixture. Make observations with a fresh
local list or dictionary for each case. Retain failed assertions while debugging
so the difference between a wrong answer and an incomplete check remains clear.

### Exercise 1: Bind independent offsets

**Inputs:** A tuple of exact integers such as (2, -1, 0); bool is not an integer for these contracts.

**Expected:** Return one function per offset in input order. Each function adds its own offset to an exact integer argument. Empty input returns (). Reject invalid offsets before returning functions, and invalid call arguments, with ValueError.

**Verify:** Calling all three functions with 10 returns (12, 9, 10). Call them again in reverse order to expose accidental shared late binding.

### Exercise 2: Keep private accumulated state

**Inputs:** An exact integer start and later exact integer increments, including negative increments.

**Expected:** Return a closure with private running state. Calls add the increment and return the new total. Separate factory calls never share state. Reject a malformed start or increment with ValueError; a rejected increment must not change the stored total.

**Verify:** A total starting at 5 returns 7 then 4 for increments 2 and -3. After rejecting True, increment 0 still returns 4; a second factory starting at 5 still returns 5.

### Exercise 3: Read a live configuration binding

**Inputs:** A caller-owned dictionary whose keys are nonempty strings and values exact integers, plus an existing nonempty key.

**Expected:** Validate the initial dictionary without copying or modifying it. Return a closure that reads the current value of the selected key on each call. A missing key raises KeyError, including after later deletion; a malformed current value raises ValueError. Replacing a separate caller variable with a new dictionary does not replace the captured dictionary.

**Verify:** A captured limit initially 3 becomes 8 after config["limit"] = 8. Deleting limit raises KeyError; reinserting a string raises ValueError. Record the caller dictionary before and after construction to prove no mutation.

### Exercise 4: Trace a call without changing its result

**Inputs:** A list for observation and an ordinary synchronous callable to decorate. Calls may use positional and keyword arguments or raise an Exception.

**Expected:** Return a decorator that preserves metadata with functools.wraps. Append call:NAME before invocation, then return:NAME on success or raise:NAME:TYPE on an Exception. Return the original result and re-raise the same exception object. Do not catch BaseException control signals.

**Verify:** For a function named divide, division by zero yields ["call:divide", "raise:divide:ZeroDivisionError"]. Inspect __name__, __doc__, __wrapped__, and inspect.signature; assert an injected exception is the identical object.

### Exercise 5: Make decorator order observable

**Inputs:** An ordinary one-integer function. The wrapper accepts one exact integer that must be at least zero.

**Expected:** Preserve function metadata. Reject negative integers, bool, and nonintegers with ValueError before calling the wrapped function. Otherwise return its result unchanged. Compare tracing outside validation with validation outside tracing; neither order may call the body for invalid input.

**Verify:** A traced outer wrapper records call and raise for -1. An outer validator records no trace for -1. On 0 both call the body once and return its actual result.

### Exercise 6: Snapshot and compose a pipeline

**Inputs:** A finite caller-owned sequence of callables. Each stage accepts and returns an integer. Input stage storage may be changed after construction.

**Expected:** Snapshot the stage sequence and reject a noncallable stage with ValueError at construction. Return a function applying stages from left to right. Empty stages return their input unchanged. Forward a stage exception immediately without calling later stages; never mutate the supplied sequence.

**Verify:** For add-two then multiply-three, input 4 gives 18, while reversed stages give 14. Clearing the original list afterward does not change the first pipeline; record that a later stage was not called after a deliberate error.

## Self-check

Explain without running code why a factory called twice can keep independent
state even when its inner functions have the same name. Explain why storing a
default dictionary does not freeze later mutations. For the live lookup,
identify which operation changes the captured dictionary and which operation
merely rebinds a caller's variable. Give the exact exception and unchanged total
expected after passing `True` to the accumulator.

**Verify:** Keep assertion evidence for `(12, 9, 10)`, the post-rejection total
`4`, a successful lookup changing from `3` to `8`, the identical injected
exception, and pipeline results `18` versus `14`. Also keep the two invalid-call
trace transcripts and the body-call list. These observations cover different
mechanisms; a correct final integer alone cannot prove metadata or nonmutation.

## Common pitfalls

If every callback adds the final offset, inspect its free names and when it is
called. Create a separate enclosing call per offset or deliberately bind a
default. If `UnboundLocalError` mentions `total`, look for an assignment in the
inner function and decide whether the intended state is enclosing or local.
Do not fix the error by introducing a module global shared by all accumulators.

If an invalid increment changes the next valid total, validation happened too
late. Move the check before the state transition. If changing a configuration
value has no effect, inspect whether you captured the value or copied the whole
dictionary instead of retaining the specified live object. If a wrapper hides
a failure, check for an unintended return in `finally` or a broad exception
handler that returns a substitute value.

If logs are missing, compare decorator order before adding another logging
layer. If a pipeline changes after the original list is cleared, identify its
ownership boundary: the stage sequence needs a snapshot, while the callable
objects themselves remain shared references. This lesson does not promise
thread-safe counters, immutable callable internals, or safe remote retry.

## Next step

Continue to [`python-lang-03`: Iterators, Generator Pipelines, and Resource Lifetime](py_lang_03.md).
It uses private state that is suspended between calls rather than hidden inside
a wrapper. Return to the [typing and data model unit](py_lang_01_typing_data_model.md)
when a callable's protocol or variance, rather than its runtime binding, is the
question. Before moving on, describe a callback bug and its smallest reproducer
in your own words, including the time at which the wrong name is read.


## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-lang-02: Scope, Closures, and Observable Decorator Contracts.
Read python/professional/companion-guides/py_lang_02.md and python/professional/lessons/py_lang_02.py. Direct prerequisites: python-lang-01, python-11.
Keep the advanced lesson self-contained for someone new to its specific mechanisms. Explain scope, closures, binding, nonlocal, decorators, metadata, ask me to predict a concrete result, then let me attempt it. Give one hint at a time and review my exact value, exception, event, and cleanup evidence. Ask retrieval questions in my own words. Do not read solutions/ until I request comparison or have made an honest attempt.
Use only prepared local offline fixtures in the Docker Python classroom; preserve saved source and notes. No SQL or external service is involved. Done when all six contracts and boundary cases have inspected evidence, and I can explain the timing and ownership decision behind each result.
```
