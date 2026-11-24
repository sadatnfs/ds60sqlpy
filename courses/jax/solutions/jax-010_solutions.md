# jax-010: explained reference

For a fixed scalar configuration n, \(f(x,n)=\sum_{i=1}^{n}x=nx\). Python can unroll a small static n during tracing. For dynamic values, an array control-flow representation is a different implementation choice. A cache specialization is associated with more than the displayed numeric value of x: shape, dtype, static configuration and function identity can matter. The exact trace count below is a local diagnostic for a freshly created function in this pinned environment.

## Solution approach

Separate what JIT changes from what it must preserve. Values must match the eager function, but tracing happens once per abstract signature, so each task looks at one consequence: equal outputs, a new trace for a new shape, a Python branch that cannot see a traced value, a static loop count, a composition with `grad`, and the staged jaxpr.

**Why it is correct here:** The polynomial `z * z + z + 1` gives 3, 7 and 13 on [1, 2, 3] in either mode. The traced function sees shapes (2,) and (3,), so it traces twice. `n` is static, so `n = 0` unrolls to no additions and returns `0. * value`. The gradient of `sum(z * z)` is `2 * z`, giving [2, 4] at [1, 2].

## Exercise 1: Compare eager and compiled values

Compilation should preserve the declared operation within its numerical contract.

**Expected:** Both give [3,7,13].

```python
function = lambda z: z * z + z + 1
values = jnp.array([1.0, 2.0, 3.0])
close(function(values), [3.0, 7.0, 13.0])
close(jax.jit(function)(values), function(values))
```

**Plausible wrong approach:** Timing the first JIT call to compare with eager execution answers a different question. That call includes tracing and compilation, and the task only asks whether the values [3, 7, 13] agree.

## Exercise 2: Observe a shape specialization

Abstract shape information changes the specialization even when the elementwise formula is unchanged.

**Expected:** Two trace-list entries with the corresponding shapes.

```python
traces = []


def shaped(z):
    traces.append(z.shape)
    return z * 2


compiled = jax.jit(shaped)
compiled(jnp.ones(2)).block_until_ready()
compiled(jnp.ones(3)).block_until_ready()
assert traces == [(2,), (3,)]
```

**Plausible wrong approach:** Calling the compiled function twice with length-2 inputs records only one trace, because the second call reuses the cached specialization. The shapes must differ to show a new trace.

## Exercise 3: Expose a traced Boolean error

The Python branch asks for a concrete truth value during tracing. Dynamic numerical control needs an array control-flow primitive.

**Expected:** TracerBoolConversionError.

```python
def bad(z):
    if z > 0:
        return z
    return -z


try:
    jax.jit(bad)(jnp.float64(2.0))
except jax.errors.TracerBoolConversionError:
    pass
else:
    raise AssertionError("dynamic Python condition accepted")
```

**Plausible wrong approach:** Marking `z` static with `static_argnums=0` does not repair the branch. JAX arrays are not hashable, so the call fails, and static numerical values would retrace for every new number anyway.

## Exercise 4: Keep zero iterations defined

The initial carry is the result when no iterations execute.

**Expected:** Zero with the input's scalar shape.

```python
close(compiled_repeat(3.0, n=0), 0.0)
```

**Plausible wrong approach:** Starting the carry at the Python float `0.` instead of `0. * value` returns a bare scalar when `n = 0` and the input is a vector. Multiplying by `value` keeps the input's shape and dtype.

## Exercise 5: Compose differentiation with compilation

A supported transformation composition preserves the chain rule for the same scalar objective.

**Expected:** Gradient [2,4].

```python
compiled_loss = jax.jit(lambda z: jnp.sum(z * z))
close(jax.grad(compiled_loss)(jnp.array([1.0, 2.0])), [2.0, 4.0])
```

**Plausible wrong approach:** Reading the gradient as `z` itself, [1, 2], forgets the factor 2 from the square. The derivative of the sum of squares is `2 * z`, so the compiled and eager gradients are both [2, 4].

## Exercise 6: Inspect the staged operations

This is inspection of the staged computation, not proof of speed or a particular hardware instruction schedule.

**Expected:** A jaxpr with numerical equations and one output variable.

```python
closed = jax.make_jaxpr(lambda z: z * z + 1)(jnp.float64(2.0))
assert len(closed.jaxpr.eqns) >= 1
assert len(closed.jaxpr.outvars) == 1
```

**Plausible wrong approach:** Asserting an exact equation count, such as two, ties the test to one JAX version's lowering. The reference only asserts at least one equation and exactly one output variable.

## How to verify

Run the reference and confirm `jax-010: 8 asserted cases passed`. Print `jax.make_jaxpr(lambda z: z * z + 1)(2.0)` to see the multiply and add equations yourself. Add a third call to `compiled` with length 2 and confirm the trace list stays at two entries, which shows the cache, not the formula, controls retracing.

## Scope of this evidence

For repeated recompilation, inspect function identity, static values, shapes and dtypes. For a missing Python side effect, ask whether it happened only during tracing. Do not introduce mutable global state to communicate between compiled calls.

Explain why a static batch size and a dynamic threshold are different decisions. Design a small family of acceptable shapes or configurations and name the evidence needed to measure compilation overhead separately from warm execution.
