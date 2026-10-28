# python-lang-02: Explained solutions

The [executable reference](py_lang_02_solution.py) implements the six contracts and
contains independent expected-value, failure, and lifetime assertions. Read the
[learner guide](../companion-guides/py_lang_02.md) for the complete run workflow and
attempt each [learner function](../lessons/py_lang_02.py) before comparing. The
reference runs entirely offline in the prepared Docker Python classroom; its
assertions are behavioral evidence for these fixtures, not a claim about unseen
learner work or external system acceptance.

## Exercise 1: Bind independent offsets

**Inputs:** A tuple of exact integers such as (2, -1, 0); bool is not an integer for these contracts.

**Expected:** Return one function per offset in input order. Each function adds its own offset to an exact integer argument. Empty input returns (). Reject invalid offsets before returning functions, and invalid call arguments, with ValueError.

**Verify:** Calling all three functions with 10 returns (12, 9, 10). Call them again in reverse order to expose accidental shared late binding.

The reference first validates every offset, so a malformed later entry does not leave the caller holding a partially accepted collection of functions. It then calls a small factory once per offset. Each factory call creates a separate local binding named offset, and its inner add function reads that binding later. The closure therefore remembers the selected offset through an independent enclosing scope. Testing only the final callback would miss the loop-binding defect; calling all callbacks and then reversing the call order distinguishes independent capture from shared state. An empty tuple has no callbacks and produces an empty result tuple. A default argument could also bind the current integer, but it would appear in the function's signature and would need care to prevent callers from overriding an implementation detail.

## Exercise 2: Keep private accumulated state

**Inputs:** An exact integer start and later exact integer increments, including negative increments.

**Expected:** Return a closure with private running state. Calls add the increment and return the new total. Separate factory calls never share state. Reject a malformed start or increment with ValueError; a rejected increment must not change the stored total.

**Verify:** A total starting at 5 returns 7 then 4 for increments 2 and -3. After rejecting True, increment 0 still returns 4; a second factory starting at 5 still returns 5.

The accumulator's total lives in the factory invocation. nonlocal is necessary because the inner function reassigns that enclosing name, rather than merely reading an integer object. The increment is validated before changing total. This sequencing gives rejection a precise guarantee: a bad input leaves the next valid observation unchanged. Integer addition creates a new integer object and rebinds total; it does not mutate an integer in place. The executable fixture starts at five, adds two, subtracts three, rejects True, and then adds zero. The last observation must still be four. A separately constructed accumulator still returns five. A module-level counter or a mutable default list would create accidental sharing across factory calls and violate this contract even if one test sequence happened to pass.

## Exercise 3: Read a live configuration binding

**Inputs:** A caller-owned dictionary whose keys are nonempty strings and values exact integers, plus an existing nonempty key.

**Expected:** Validate the initial dictionary without copying or modifying it. Return a closure that reads the current value of the selected key on each call. A missing key raises KeyError, including after later deletion; a malformed current value raises ValueError. Replacing a separate caller variable with a new dictionary does not replace the captured dictionary.

**Verify:** A captured limit initially 3 becomes 8 after config["limit"] = 8. Deleting limit raises KeyError; reinserting a string raises ValueError. Record the caller dictionary before and after construction to prove no mutation.

The live lookup captures the original dictionary object and the selected key binding. It deliberately does not cache config[key] at construction. Looking up the key again on every call exposes later updates and deletion, with normal KeyError on absence. The validator checks all initial key/value entries without altering them. Later reads validate the selected current value, because a caller can mutate the shared dictionary after construction. Other later dictionary edits are outside the selected read contract. Reassigning the caller's variable config to a different dictionary leaves the closure's original reference intact. The reference keeps an old_config name solely to make that object identity visible in the test. Copying the dictionary would be a reasonable snapshot API, but it would answer a different question and would fail the required change from three to eight.

## Exercise 4: Trace a call without changing its result

**Inputs:** A list for observation and an ordinary synchronous callable to decorate. Calls may use positional and keyword arguments or raise an Exception.

**Expected:** Return a decorator that preserves metadata with functools.wraps. Append call:NAME before invocation, then return:NAME on success or raise:NAME:TYPE on an Exception. Return the original result and re-raise the same exception object. Do not catch BaseException control signals.

**Verify:** For a function named divide, division by zero yields ["call:divide", "raise:divide:ZeroDivisionError"]. Inspect __name__, __doc__, __wrapped__, and inspect.signature; assert an injected exception is the identical object.

The decorator factory captures the caller's observation list. Decoration creates a wrapper with wraps applied, so the wrapper retains the original name, docstring, and __wrapped__ link. The wrapper accepts arbitrary positional and keyword arguments and forwards them unchanged. It records entry first, then separates ordinary success from an Exception. A bare raise inside the handler re-raises the original exception object and traceback rather than constructing a replacement with the same message. The reference checks object identity with an injected RuntimeError; comparing only its text would miss a replacement error. BaseException subclasses remain control signals and are not converted into ordinary failure log entries. Metadata preservation does not make the wrapper statically typed for every possible callable; the runtime contract here is specifically ordinary synchronous functions.

## Exercise 5: Make decorator order observable

**Inputs:** An ordinary one-integer function. The wrapper accepts one exact integer that must be at least zero.

**Expected:** Preserve function metadata. Reject negative integers, bool, and nonintegers with ValueError before calling the wrapped function. Otherwise return its result unchanged. Compare tracing outside validation with validation outside tracing; neither order may call the body for invalid input.

**Verify:** A traced outer wrapper records call and raise for -1. An outer validator records no trace for -1. On 0 both call the body once and return its actual result.

Validation is its own wrapper and happens before invocation of the function it wraps. The exact integer test distinguishes zero from False, and the nonnegative test rejects negative integers without running the body. When tracing is outermost, its call entry occurs before the validator rejects and its handler records the resulting ValueError. When validation is outermost, the rejected call never reaches the tracing wrapper. Both arrangements therefore protect the body but produce different trace evidence. The body-call list is empty after the two invalid calls, which is stronger evidence than inspecting only logs. Both zero calls then return the body's true result and each adds one entry to the body list. Reversing decorator order to obtain desired observability is a policy decision, not a general rule that either order is always superior.

## Exercise 6: Snapshot and compose a pipeline

**Inputs:** A finite caller-owned sequence of callables. Each stage accepts and returns an integer. Input stage storage may be changed after construction.

**Expected:** Snapshot the stage sequence and reject a noncallable stage with ValueError at construction. Return a function applying stages from left to right. Empty stages return their input unchanged. Forward a stage exception immediately without calling later stages; never mutate the supplied sequence.

**Verify:** For add-two then multiply-three, input 4 gives 18, while reversed stages give 14. Clearing the original list afterward does not change the first pipeline; record that a later stage was not called after a deliberate error.

The pipeline converts the stage sequence to a tuple before returning its closure. This snapshots which callable objects participate and their order, so clearing the original list has no effect. It does not deep-copy callable internals: a stage that closes over mutable configuration can still observe that configuration. The reference applies stages in supplied order, so add-two followed by multiply-three transforms four into eighteen. Reversing those stages gives fourteen and exposes an implementation that guessed conventional right-to-left composition. Empty composition is the identity operation. Stage validation happens at construction, while stage exceptions propagate during invocation. A deliberate first-stage error plus an independent later-stage observation list proves short-circuiting. Catching the error and continuing would return a plausible number while violating the pipeline's control-flow contract. No global pipeline registry or external package is needed.

The following compact check runs in the executable reference namespace after its function definitions:

```python
callbacks = bind_offsets((2, -1, 0))
assert tuple(callback(10) for callback in callbacks) == (12, 9, 10)
```

Run the complete reference from fresh process state when comparing results. A change to an input policy must be deliberate and reflected in its assertions; merely suppressing an exception or deleting a cleanup check does not satisfy the original contract.
