# jax-014: explained reference

Momentum here uses \(v_t=0.9v_{t-1}+g_t\) and \(w_t=w_{t-1}-\eta v_t\). Adam uses \(m_t=\beta_1m_{t-1}+(1-\beta_1)g_t\), \(v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2\), with corrections \(\widehat m_t=m_t/(1-\beta_1^t)\) and \(\widehat v_t=v_t/(1-\beta_2^t)\). The update is \(w_t=w_{t-1}-\eta\widehat m_t/(\sqrt{\widehat v_t}+\epsilon)\). Each denominator is a complete expression; the exponent belongs to beta with its subscript.

## Exercise 1: Trace plain SGD

Plain SGD uses no history in this defined rule.

**Expected:** 0.4.

```python
close(1.0 - 0.2 * jnp.float64(3.0), 0.4)
```

## Exercise 2: Continue momentum

The second velocity includes 90 percent of the first plus the new gradient.

**Expected:** First weight -0.2; second -0.58; final velocity 3.8.

```python
w, v = momentum_step(0.0, 0.0, 2.0)
w, v = momentum_step(w, v, 2.0)
close(w, -0.58)
close(v, 3.8)
```

## Exercise 3: Continue Adam's counter

For this constant gradient, corrected moments remain two and four on both steps.

**Expected:** Step two; weight approximately -0.2.

```python
w, s = adam_step(0.0, zero_state, 2.0)
w, s = adam_step(w, s, 2.0)
assert int(s[2]) == 2
close(w, -2 * 0.2 / (2.0 + 1e-8))
```

## Exercise 4: Preserve zero-gradient history

Zero current gradient is not equivalent to a fresh optimizer or no update.

**Expected:** The parameter still moves because the first moment retains history.

```python
w, s = adam_step(0.0, zero_state, 2.0)
next_w, next_s = adam_step(w, s, 0.0)
assert float(next_w) < float(w)
assert int(next_s[2]) == 2
```

## Exercise 5: Compile the transition

Pure state transitions compose with compilation when their structures and operations are supported.

**Expected:** Equal parameter and state leaves.

```python
a, sa = adam_step(0.0, zero_state, 2.0)
b, sb = jax.jit(adam_step)(0.0, zero_state, 2.0)
close(a, b)
for x, y in zip(sa, sb):
    close(x, y)
```

## Exercise 6: Reverse the gradient

The first moment changes sign while the squared moment does not.

**Expected:** A positive parameter update of 0.2/(2+1e-8).

```python
w, s = adam_step(0.0, zero_state, -2.0)
close(w, 0.2 / (2.0 + 1e-8))
close(s[0], -0.2)
close(s[1], 0.004)
```

## Scope of this evidence

If continued training differs, compare parameters, moments, step count, learning-rate policy and the actual next batch/key. An optimizer name is not proof that returned state was retained. Match epsilon placement and reduction before comparing frameworks.

Describe the minimum state needed to reproduce one next update under this Adam rule. Explain what changes if dropout, a scheduler or data shuffling is introduced, then connect those additions to the later continuation capstone.
