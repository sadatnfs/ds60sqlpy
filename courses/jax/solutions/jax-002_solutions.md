# jax-002: explained reference

For \(X\in\mathbb R^{2\times3}\), row sums satisfy \(r_i=\sum_{j=0}^{2}X_{ij}\) and column sums satisfy \(c_j=\sum_{i=0}^{1}X_{ij}\). Row centering is \(X_{ij}-\frac13\sum_kX_{ik}\). Keeping the reduced axis as a singleton makes the subtraction's intended broadcast visible. The centered row sums should be zero, which is a stronger oracle than checking only the output shape.

## Solution approach

The fixture `table = jnp.arange(6.).reshape(2, 3)` holds rows [0, 1, 2] and [3, 4, 5]. Before each task, write the shape of every operand and line the shapes up from the right: (2, 3) against (3,) broadcasts along rows, while (2, 3) against (2, 1) broadcasts along columns. Updates use `.at[...]`, which returns a new array and leaves the original untouched.

**Why it is correct here:** Row means are 1 and 4, so subtracting a (2, 1) mean column gives [-1, 0, 1] in both rows and each centered row sums to zero. Offsets of shape (3,) add 10, 20 and 30 to the three columns; offsets reshaped to (2, 1) add 10 to every entry of row 0 and 20 to every entry of row 1. These sums can be read straight off the six fixture values.

## Exercise 1: Center each observation

keepdims retains shape (2,1), so each row receives its own mean.

**Expected:** Both rows [-1,0,1]; row sums zero.

```python
centered = table - table.mean(axis=1, keepdims=True)
close(centered, [[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]])
close(centered.sum(axis=1), [0.0, 0.0])
```

**Plausible wrong approach:** Dropping `keepdims=True` leaves the row means with shape (2,). Subtracting that from a (2, 3) table raises a broadcast error here, and on a (2, 2) table it would silently subtract column-wise, which is the bug a nonsquare fixture exposes.

## Exercise 2: Broadcast feature offsets

The three offsets align with the final dimension.

**Expected:** [[10,21,32],[13,24,35]].

```python
close(table + jnp.array([10.0, 20.0, 30.0]), [[10.0, 21.0, 32.0], [13.0, 24.0, 35.0]])
```

**Plausible wrong approach:** Writing the offsets as a column `[[10.], [20.], [30.]]` gives shape (3, 1), which does not broadcast against (2, 3). The feature axis is the last axis, so a flat length-3 vector is the correct alignment.

## Exercise 3: Broadcast observation offsets

A (2,1) array repeats each offset across that row's features.

**Expected:** [[10,11,12],[23,24,25]].

```python
close(table + jnp.array([10.0, 20.0])[:, None], [[10.0, 11.0, 12.0], [23.0, 24.0, 25.0]])
```

**Plausible wrong approach:** Adding `jnp.array([10., 20.])` without `[:, None]` fails because a trailing length of 2 cannot align with 3 columns. The new axis is what moves the offsets onto the row dimension.

## Exercise 4: Accumulate an update

add expresses an increment, whereas set replaces the old value.

**Expected:** New [6,2], original [1,2].

```python
old = jnp.array([1.0, 2.0])
close(old.at[0].add(5.0), [6.0, 2.0])
close(old, [1.0, 2.0])
```

**Plausible wrong approach:** Using `old.at[0].set(5.0)` replaces the 1 with 5 and returns [5, 2], not [6, 2]. The task asks for an increment, so `.add` is required; `set` silently discards the existing value.

## Exercise 5: Enforce the index boundary

The lesson refuses this request explicitly rather than relying on backend-specific bounds behavior.

**Expected:** ValueError from the declared host-side guard.

```python
try:
    replace_at(jnp.zeros(3), 3, 1.0)
except ValueError:
    pass
else:
    raise AssertionError("bad index accepted")
```

**Plausible wrong approach:** Calling `values.at[3].set(1.0)` on a length-3 vector does not raise in JAX; out-of-bounds updates are dropped by default. Relying on that would hide the bad index, which is why `replace_at` checks the bound on the host first.

## Exercise 6: Transfer the axis rule

Changing both axis lengths catches implementations that accidentally relied on a square or fixed-size example.

**Expected:** Shape (3,2), all row sums zero.

```python
other = jnp.arange(6.0).reshape(3, 2)
centered = other - other.mean(axis=1, keepdims=True)
assert centered.shape == (3, 2)
close(centered.sum(axis=1), jnp.zeros(3))
```

**Plausible wrong approach:** Reusing the (2, 3) fixture to test the axis rule cannot catch code that hard-codes three columns. The (3, 2) array changes both lengths, so a wrong axis choice produces a shape error or nonzero row sums.

## How to verify

Run the reference and confirm `jax-002: 8 asserted cases passed`. For a manual check, print `table.mean(axis=1, keepdims=True).shape` and expect (2, 1), then print `centered.sum(axis=1)` and expect zeros. After the accumulate task, print `old` again and confirm it is still [1, 2], which shows the update returned a new array instead of mutating the input.

## Scope of this evidence

A shape-correct result may still reduce the wrong population. Check a row-specific invariant and use nonsquare fixtures. Keep index validation outside transformed numerical code until the tracing rules have been taught.

Compare this value-oriented update with NumPy mutation in python-numpy-01. Explain why an implementation's possible in-place optimization does not make arbitrary Python mutation part of JAX's public array contract.
