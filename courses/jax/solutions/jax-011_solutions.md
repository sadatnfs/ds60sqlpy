# jax-011: explained reference

The recurrence \(h_{t+1}=\frac12h_t+x_t\), starting at zero with inputs \([2,2,2]\), gives states \([2,3,3.5]\). The final sensitivity to the initial state is \((1/2)^3=1/8\). Sensitivities to the three inputs are \([1/4,1/2,1]\): earlier inputs pass through more attenuation steps. These independently derived coefficients test the transition and its differentiation together.

## Exercise 1: Differentiate the initial carry

Each transition multiplies the incoming initial-state sensitivity by one half.

**Expected:** 1/8 for three steps.

```python
values = jnp.array([2., 2., 2.])
close(jax.grad(lambda h: recurrence(h, values)[0])(0.), .125)
```

## Exercise 2: Differentiate sequence inputs

The last input reaches the output directly; earlier ones pass through later transitions.

**Expected:** [1/4,1/2,1].

```python
close(jax.grad(lambda values: recurrence(jnp.float64(0.), values)[0])(jnp.array([2., 2., 2.])), [.25, .5, 1.])
```

## Exercise 3: Handle an empty scan

No transition executes, so the identity of the empty computation is its initial carry.

**Expected:** Final five and a length-zero history.

```python
last, history = recurrence(jnp.float64(5.), jnp.array([], dtype=jnp.float64))
close(last, 5.)
assert history.shape == (0,)
```

## Exercise 4: Use a fixed-index loop

The loop runs indices zero through three and retains one scalar carry.

**Expected:** 6.

```python
result = jax.lax.fori_loop(0, 4, lambda i, total: total + i, jnp.int64(0))
assert int(result) == 6
```

## Exercise 5: Inspect a dynamic stopping rule

The stopping count is stable in a neighborhood of the chosen point. This does not imply differentiability at every threshold boundary.

**Expected:** Output 16, forward sensitivity 16 under this local four-step path.

```python
def double_until(value):
    return jax.lax.while_loop(lambda z: z < 10., lambda z: 2. * z, value)
value, tangent = jax.jvp(double_until, (jnp.float64(1.),), (jnp.float64(1.),))
close(value, 16.)
close(tangent, 16.)
```

## Exercise 6: Transfer to a batched state

The carry can be an array as long as its shape remains unchanged across steps.

**Expected:** Final [2,4] from inputs [[2,4],[1,2]].

```python
last, history = recurrence(jnp.zeros(2), jnp.array([[2., 4.], [1., 2.]]))
close(last, [2., 4.])
assert history.shape == (2, 2)
```

## Scope of this evidence

For a carry error, compare shape, dtype and tree structure before and after one transition. For a gradient failure, identify the primitive and the differentiation mode. A branch that changes output shape needs a different representation or explicit static configuration.

Write a fixed-step simulation transition and explain how a runtime stopping criterion changes its numerical and derivative contract. Connect the difference to solver tolerance and discretization error rather than treating all loops as interchangeable syntax.
