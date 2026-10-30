# jax-010: explained reference

For a fixed scalar configuration n, \(f(x,n)=\sum_{i=1}^{n}x=nx\). Python can unroll a small static n during tracing. For dynamic values, an array control-flow representation is a different implementation choice. A cache specialization is associated with more than the displayed numeric value of x: shape, dtype, static configuration and function identity can matter. The exact trace count below is a local diagnostic for a freshly created function in this pinned environment.

## Exercise 1: Compare eager and compiled values

Compilation should preserve the declared operation within its numerical contract.

**Expected:** Both give [3,7,13].

```python
function = lambda z: z * z + z + 1
values = jnp.array([1.0, 2.0, 3.0])
close(function(values), [3.0, 7.0, 13.0])
close(jax.jit(function)(values), function(values))
```

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

## Exercise 4: Keep zero iterations defined

The initial carry is the result when no iterations execute.

**Expected:** Zero with the input's scalar shape.

```python
close(compiled_repeat(3.0, n=0), 0.0)
```

## Exercise 5: Compose differentiation with compilation

A supported transformation composition preserves the chain rule for the same scalar objective.

**Expected:** Gradient [2,4].

```python
compiled_loss = jax.jit(lambda z: jnp.sum(z * z))
close(jax.grad(compiled_loss)(jnp.array([1.0, 2.0])), [2.0, 4.0])
```

## Exercise 6: Inspect the staged operations

This is inspection of the staged computation, not proof of speed or a particular hardware instruction schedule.

**Expected:** A jaxpr with numerical equations and one output variable.

```python
closed = jax.make_jaxpr(lambda z: z * z + 1)(jnp.float64(2.0))
assert len(closed.jaxpr.eqns) >= 1
assert len(closed.jaxpr.outvars) == 1
```

## Scope of this evidence

For repeated recompilation, inspect function identity, static values, shapes and dtypes. For a missing Python side effect, ask whether it happened only during tracing. Do not introduce mutable global state to communicate between compiled calls.

Explain why a static batch size and a dynamic threshold are different decisions. Design a small family of acceptable shapes or configurations and name the evidence needed to measure compilation overhead separately from warm execution.
