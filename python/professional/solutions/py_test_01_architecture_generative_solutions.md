# Test architecture and generative testing solution reasoning

Attempt `python-test-01` before reading the executable
[`py_test_01_architecture_generative_solution.py`](py_test_01_architecture_generative_solution.py).

The solution separates pure logic, stateful fakes, real-local boundaries, and
one-interaction mocks. `Clock` removes real waiting; `KeyValueStore` lets the
same contract exercise an in-memory fake and a JSON file implementation.
`patch.dict` is scoped so process environment state is restored after a test.

`merge_intervals` is the property-based target because many examples can miss
reversed endpoints, adjacency, nesting, duplicates, and empty input. Hypothesis
generates those combinations and shrinks a failure toward the smallest useful
counterexample. Its test disables the example database, uses deterministic
generation, and has no deadline, so it creates no repository cache and avoids
machine-speed failures.

A fake is valuable when behavior and state matter across several calls. A mock
is useful for one narrow interaction such as “audit once.” A real temporary
file is the right level for serialization and filesystem contract behavior.
Fixture lifetime should be the narrowest scope that preserves independence;
sharing mutable session state makes failures order-dependent.

Edge cases include expiry exactly at the deadline, malformed persisted JSON,
environment values that are blank or nonnumeric, interval endpoints in reverse
order, and a backend that passes fake-only tests but violates the real contract.

