# jax-011: explained reference

The recurrence \(h_{t+1}=\frac12h_t+x_t\), starting at zero with inputs \([2,2,2]\), gives states \([2,3,3.5]\). The final sensitivity to the initial state is \((1/2)^3=1/8\). Sensitivities to the three inputs are \([1/4,1/2,1]\): earlier inputs pass through more attenuation steps. These independently derived coefficients test the transition and its differentiation together.

## Solution approach

Unroll `h_new = 0.5 * h + v` by hand before trusting the primitives. Three steps give `h3 = h0 / 8 + v0 / 4 + v1 / 2 + v2`, which predicts both gradient tasks at once. The remaining tasks probe the contract of each loop primitive: `scan` with zero steps, `fori_loop` with a fixed index range, `while_loop` under forward-mode differentiation, and a carry that is a vector rather than a scalar.

**Why it is correct here:** The unrolled formula has coefficient 1/8 on `h0` and coefficients [1/4, 1/2, 1] on the inputs. An empty scan returns its initial carry 5 and a history of shape (0,). Indices 0 to 3 sum to 6. Starting at one, doubling reaches 2, 4, 8 and 16, so the output is 16 and the tangent is 2 ** 4 = 16. Inputs [2, 4] then [1, 2] give [2, 4] and then `0.5 * [2, 4] + [1, 2] = [2, 4]`.

## Exercise 1: Differentiate the initial carry

Each transition multiplies the incoming initial-state sensitivity by one half.

**Expected:** 1/8 for three steps.

```python
values = jnp.array([2.0, 2.0, 2.0])
close(jax.grad(lambda h: recurrence(h, values)[0])(0.0), 0.125)
```

**Plausible wrong approach:** Counting only the transitions after the first input and answering 1/4 misreads the recurrence. Each of the three steps halves the carry, including the first, so the initial state contributes 0.5 ** 3.

## Exercise 2: Differentiate sequence inputs

The last input reaches the output directly; earlier ones pass through later transitions.

**Expected:** [1/4,1/2,1].

```python
close(
    jax.grad(lambda values: recurrence(jnp.float64(0.0), values)[0])(jnp.array([2.0, 2.0, 2.0])),
    [0.25, 0.5, 1.0],
)
```

**Plausible wrong approach:** Reporting [1, 1/2, 1/4] reverses the order. The last value is added after every halving, so it reaches the output untouched, while the first value is halved by the two later steps.

## Exercise 3: Handle an empty scan

No transition executes, so the identity of the empty computation is its initial carry.

**Expected:** Final five and a length-zero history.

```python
last, history = recurrence(jnp.float64(5.0), jnp.array([], dtype=jnp.float64))
close(last, 5.0)
assert history.shape == (0,)
```

**Plausible wrong approach:** Expecting an empty scan to raise, or to return zero, treats it like a reduction with a missing identity. `scan` simply never calls `step`, so the carry passes through as 5.

## Exercise 4: Use a fixed-index loop

The loop runs indices zero through three and retains one scalar carry.

**Expected:** 6.

```python
result = jax.lax.fori_loop(0, 4, lambda i, total: total + i, jnp.int64(0))
assert int(result) == 6
```

**Plausible wrong approach:** Treating the `fori_loop` upper bound as inclusive adds index 4 and reports 10. The bounds follow Python `range(0, 4)`, which stops before the upper value.

## Exercise 5: Inspect a dynamic stopping rule

The stopping count is stable in a neighborhood of the chosen point. This does not imply differentiability at every threshold boundary.

**Expected:** Output 16, forward sensitivity 16 under this local four-step path.

```python
def double_until(value):
    return jax.lax.while_loop(lambda z: z < 10.0, lambda z: 2.0 * z, value)


value, tangent = jax.jvp(double_until, (jnp.float64(1.0),), (jnp.float64(1.0),))
close(value, 16.0)
close(tangent, 16.0)
```

**Plausible wrong approach:** Using `jax.grad` on `double_until` fails, because reverse mode cannot differentiate a `while_loop` whose trip count is decided at run time. Forward mode through `jax.jvp` works and gives 16.

## Exercise 6: Transfer to a batched state

The carry can be an array as long as its shape remains unchanged across steps.

**Expected:** Final [2,4] from inputs [[2,4],[1,2]].

```python
last, history = recurrence(jnp.zeros(2), jnp.array([[2.0, 4.0], [1.0, 2.0]]))
close(last, [2.0, 4.0])
assert history.shape == (2, 2)
```

**Plausible wrong approach:** Starting the batched run from the scalar `0.` breaks the carry contract: after one step the carry would become shape (2,), and `scan` requires the carry returned by `step` to match the carry it received.

## How to verify

Run the reference and confirm `jax-011: 8 asserted cases passed`. Write a plain Python loop over [2, 2, 2] from zero and compare its 3.5 with `recurrence(0., values)[0]`. Then try `jax.grad(double_until)(1.)` once to see the reverse-mode error, which explains why the lesson uses `jax.jvp` for the dynamic stopping rule.

## Scope of this evidence

For a carry error, compare shape, dtype and tree structure before and after one transition. For a gradient failure, identify the primitive and the differentiation mode. A branch that changes output shape needs a different representation or explicit static configuration.

Write a fixed-step simulation transition and explain how a runtime stopping criterion changes its numerical and derivative contract. Connect the difference to solver tolerance and discretization error rather than treating all loops as interchangeable syntax.
