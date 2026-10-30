# jax-026: explained reference

For \(f(x)=\sum_i x_i^3\), \(\nabla f(x)=3x^2\). At \([1,2,3]\), f=36 and the gradient is \([3,12,27]\). A checkpointed implementation should retain those results. For a donated transition \(x'=x+1\), the returned value is the next state; the old buffer's lifetime is intentionally surrendered even though the abstract numerical rule is simple.

## Exercise 1: Change the derivative input

Negative inputs change the cubic value but the squared derivative remains nonnegative.

**Expected:** [12,0,12].

```python
close(jax.grad(rematerialized)(jnp.array([-2.0, 0.0, 2.0])), [12.0, 0.0, 12.0])
```

## Exercise 2: Compose checkpointing with JIT

This checks one supported composition, not every possible custom primitive or backend.

**Expected:** The same [3,12,27] derivative.

```python
close(jax.jit(jax.grad(rematerialized))(jnp.array([1.0, 2.0, 3.0])), [3.0, 12.0, 27.0])
```

## Exercise 3: Continue from returned ownership

The second call consumes the first call's returned state, not the original donated handle.

**Expected:** [3,4] from initial [1,2].

```python
state = jnp.array([1.0, 2.0])
state = consume(state)
state = consume(state)
close(state, [3.0, 4.0])
```

## Exercise 4: Keep an ordinary baseline

Independent input arrays prevent the comparison from reusing consumed storage.

**Expected:** Matching [5,6].

```python
baseline = jnp.array([4.0, 5.0]) + 1.0
updated = consume(jnp.array([4.0, 5.0]))
close(updated, baseline)
```

## Exercise 5: Check a higher derivative

The second derivative is 6x, providing an additional transformation check.

**Expected:** [6,12].

```python
hessian = jax.hessian(rematerialized)(jnp.array([1.0, 2.0]))
close(hessian, [[6.0, 0.0], [0.0, 12.0]])
```

## Exercise 6: Separate a resource claim

Logical nbytes excludes allocator pools, compiler storage, intermediates and process/device overhead. It is not peak memory.

**Expected:** Four float64 entries, 32 bytes of logical array payload.

```python
result = consume(jnp.zeros(4, dtype=jnp.float64))
assert result.size == 4 and result.nbytes == 32
```

## Scope of this evidence

A deleted-buffer error indicates a lifetime violation, not a reason to disable correctness checks. A small nbytes value is not a peak-memory measurement. Validate the mathematical baseline before investigating checkpoint placement or donation performance.

Propose checkpoint boundaries for a multi-stage model and a donation policy for its parameter-state transition. Explain which arrays a caller must retain for evaluation and which may be consumed, then specify an actual peak-memory measurement on owned hardware.
