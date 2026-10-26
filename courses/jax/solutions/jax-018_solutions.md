# jax-018: explained reference

For positive x, \(d\log x/dx=1/x\). If the intended extension returns zero for nonpositive x, define the computational branch so that log is only applied to a valid positive surrogate there. This is an explicit piecewise extension, not a claim that log itself is defined on negative numbers. At the chosen smooth positive points, the derivative must still equal \(1/x\). At a boundary, state the selected differentiation convention rather than asserting ordinary smoothness.

## Exercise 1: Expose a host conversion

A traced runtime value is not a concrete host array available to NumPy during staging.

**Expected:** TracerArrayConversionError.

```python
try:
    jax.jit(lambda x: np.asarray(x) + 1)(jnp.ones(2))
except jax.errors.TracerArrayConversionError:
    pass
else:
    raise AssertionError('host conversion accepted')
```

## Exercise 2: Expose a dynamic output length

The number of retained values depends on runtime data, so this expression does not specify a fixed output shape.

**Expected:** NonConcreteBooleanIndexError.

```python
try:
    jax.jit(lambda x: x[x > 0.])(jnp.array([-1., 2.]))
except jax.errors.NonConcreteBooleanIndexError:
    pass
else:
    raise AssertionError('dynamic shape accepted')
```

## Exercise 3: Use a fixed-shape alternative

This asks for a sum, so retaining a padded vector is sufficient and does not require a variable-length selection.

**Expected:** 2 for [-1,2].

```python
function = jax.jit(lambda x: jnp.where(x > 0., x, 0.).sum())
close(function(jnp.array([-1., 2.])), 2.)
```

## Exercise 4: Print a runtime diagnostic

Runtime diagnostics observe numerical values; they are excluded from later timing claims.

**Expected:** A diagnostic containing total=3 and unchanged returned total three.

```python
def observed(x):
    total = x.sum()
    jax.debug.print('total={total}', total=total)
    return total
close(jax.jit(observed)(jnp.array([1., 2.])), 3.)
```

## Exercise 5: Compare with JIT disabled

The comparison localizes transformation behavior without treating eager success as the final acceptance criterion.

**Expected:** Matching values at [1,2].

```python
function = jax.jit(lambda x: x * x + 1)
with jax.disable_jit():
    eager = function(jnp.array([1., 2.]))
close(function(jnp.array([1., 2.])), eager)
```

## Exercise 6: Retain the positive-domain derivative

A repair for invalid inputs must not damage the intended formula on its valid domain.

**Expected:** [1,0.5,0.25].

```python
close(jax.grad(lambda x: safe_log_extension(x).sum())(jnp.array([1., 2., 4.])), [1., .5, .25])
```

## Scope of this evidence

Do not catch every exception and report success. Each negative case here names a specific violated contract, while the repaired valid path has its own assertion. Debug printing is observation, not a substitute for a numerical oracle.

Given an unfamiliar transformed program, classify its first failure as shape, host boundary, static configuration, numerical domain or state ownership. Propose one repair and a test that would reject a plausible wrong repair.
