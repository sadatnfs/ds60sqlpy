# jax-018: explained reference

For positive x, \(d\log x/dx=1/x\). If the intended extension returns zero for nonpositive x, define the computational branch so that log is only applied to a valid positive surrogate there. This is an explicit piecewise extension, not a claim that log itself is defined on negative numbers. At the chosen smooth positive points, the derivative must still equal \(1/x\). At a boundary, state the selected differentiation convention rather than asserting ordinary smoothness.

## Solution approach

Reproduce each failure on the smallest input, name the invariant it breaks, and then repair it without changing the question. Host conversion breaks the rule that traced values stay inside JAX. Boolean indexing breaks the fixed-shape rule. Diagnostics must observe runtime values, and a repair for an invalid domain must leave the valid domain untouched.

**Why it is correct here:** `np.asarray` on a tracer raises `TracerArrayConversionError`. `x[x > 0]` has a data-dependent length, so JIT raises `NonConcreteBooleanIndexError`. The masked sum keeps shape (2,) and returns 2. `jax.debug.print` prints total=3 and returns 3. Disabling JIT gives [2, 5] for `x * x + 1`. On [1, 2, 4] the safe log has derivative 1 / x = [1, 0.5, 0.25].

## Exercise 1: Expose a host conversion

A traced runtime value is not a concrete host array available to NumPy during staging.

**Expected:** TracerArrayConversionError.

```python
try:
    jax.jit(lambda x: np.asarray(x) + 1)(jnp.ones(2))
except jax.errors.TracerArrayConversionError:
    pass
else:
    raise AssertionError("host conversion accepted")
```

**Plausible wrong approach:** Catching a bare `Exception` around the failing call makes the test pass for any error, including a typo. Naming `TracerArrayConversionError` proves the failure came from host conversion.

## Exercise 2: Expose a dynamic output length

The number of retained values depends on runtime data, so this expression does not specify a fixed output shape.

**Expected:** NonConcreteBooleanIndexError.

```python
try:
    jax.jit(lambda x: x[x > 0.0])(jnp.array([-1.0, 2.0]))
except jax.errors.NonConcreteBooleanIndexError:
    pass
else:
    raise AssertionError("dynamic shape accepted")
```

**Plausible wrong approach:** Replacing `x[x > 0]` with `jnp.nonzero(x)` inside JIT hits the same problem, since its length also depends on data. It only works with a fixed `size` and fill value, which is another fixed-shape repair.

## Exercise 3: Use a fixed-shape alternative

This asks for a sum, so retaining a padded vector is sufficient and does not require a variable-length selection.

**Expected:** 2 for [-1,2].

```python
function = jax.jit(lambda x: jnp.where(x > 0.0, x, 0.0).sum())
close(function(jnp.array([-1.0, 2.0])), 2.0)
```

**Plausible wrong approach:** Using Python `print(total)` inside the jitted function prints a tracer once, during tracing, and nothing on later calls. `jax.debug.print` is staged into the computation and reports the value 3.

## Exercise 4: Print a runtime diagnostic

Runtime diagnostics observe numerical values; they are excluded from later timing claims.

**Expected:** A diagnostic containing total=3 and unchanged returned total three.

```python
def observed(x):
    total = x.sum()
    jax.debug.print("total={total}", total=total)
    return total


close(jax.jit(observed)(jnp.array([1.0, 2.0])), 3.0)
```

**Plausible wrong approach:** Accepting a function because it works under `jax.disable_jit()` treats eager success as the final test. The comparison only localizes the fault; the compiled path must still be checked.

## Exercise 5: Compare with JIT disabled

The comparison localizes transformation behavior without treating eager success as the final acceptance criterion.

**Expected:** Matching values at [1,2].

```python
function = jax.jit(lambda x: x * x + 1)
with jax.disable_jit():
    eager = function(jnp.array([1.0, 2.0]))
close(function(jnp.array([1.0, 2.0])), eager)
```

**Plausible wrong approach:** Writing `jnp.where(x > 0, jnp.log(x), 0)` hides bad values in the output but not in the gradient: the unused log branch still has an infinite or NaN derivative at nonpositive entries, which leaks NaN.

## Exercise 6: Retain the positive-domain derivative

A repair for invalid inputs must not damage the intended formula on its valid domain.

**Expected:** [1,0.5,0.25].

```python
close(jax.grad(lambda x: safe_log_extension(x).sum())(jnp.array([1.0, 2.0, 4.0])), [1.0, 0.5, 0.25])
```

**Plausible wrong approach:** Testing the safe log only at zero or negative inputs proves the repair, not the formula. A mistake such as always using the safe input 1 would also pass there; positive inputs catch it.

## How to verify

Run the reference and confirm `jax-018: 8 asserted cases passed`, with the `total=3` line visible in the output. Then call `jax.grad(lambda x: jnp.where(x > 0, jnp.log(x), 0.).sum())(jnp.array([0., 1.]))` and see the NaN, and compare it with the safe extension at the same input.

## Scope of this evidence

Do not catch every exception and report success. Each negative case here names a specific violated contract, while the repaired valid path has its own assertion. Debug printing is observation, not a substitute for a numerical oracle.

Given an unfamiliar transformed program, classify its first failure as shape, host boundary, static configuration, numerical domain or state ownership. Propose one repair and a test that would reject a plausible wrong repair.
