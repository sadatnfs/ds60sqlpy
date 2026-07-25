# Bridge Day 2 — Solution notes

Attempt the [learner file](../lessons/day02_protocols_context_decorators.py)
before reading [day02_solution.py](day02_solution.py).

## Design

The reference context manager depends on a three-method `Connection` Protocol
and a callable factory Protocol. It acquires the resource before entering its
`try`, commits only after the body returns, rolls back if the body raises, and
closes in `finally`.

The decorator uses `ParamSpec` for all parameters and `TypeVar` for the return
type. `functools.wraps()` preserves runtime metadata. Log entries include only
the qualified function name and outcome; generic wrappers cannot know which
arguments are sensitive.

## Tradeoffs

- Catching `BaseException` ensures rollback during cancellation and keyboard
  interruption. Some applications catch `Exception` and rely on a lower-level
  owner for process-level cancellation cleanup. The ownership policy must be
  explicit either way.
- If rollback fails while handling an earlier body error, Python exception
  chaining can make diagnosis complicated. Production infrastructure may use
  `ExceptionGroup` or driver-managed transaction contexts to preserve both
  failures.
- A factory returning a Protocol is easy to fake. A pool lease is also a
  resource and may need “return to pool” rather than physical `close`.
- A decorator is convenient for uniform diagnostics, but explicit logging
  inside a workflow can include safer domain context and clearer timing.

## Verification

A recording fake makes order observable:

- success: `work`, `commit`, `close`;
- body failure: `work`, `rollback`, `close`;
- the same body exception reaches the caller.

Also verify the decorated function's name, return type, and exception behavior.
Do not assert timestamps or complete log formatting; those are incidental.

