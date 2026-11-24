# jax-014: explained reference

Momentum here uses \(v_t=0.9v_{t-1}+g_t\) and \(w_t=w_{t-1}-\eta v_t\). Adam uses \(m_t=\beta_1m_{t-1}+(1-\beta_1)g_t\), \(v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2\), with corrections \(\widehat m_t=m_t/(1-\beta_1^t)\) and \(\widehat v_t=v_t/(1-\beta_2^t)\). The update is \(w_t=w_{t-1}-\eta\widehat m_t/(\sqrt{\widehat v_t}+\epsilon)\). Each denominator is a complete expression; the exponent belongs to beta with its subscript.

## Solution approach

Treat every optimizer as a function from (weight, state, gradient) to (new weight, new state), and step it by hand. Momentum keeps one velocity, `v = 0.9 * v + g`, then moves by `rate * v`. Adam keeps a first moment, a second moment and a step counter, divides each moment by its bias correction, and moves by the corrected mean over the root of the corrected square.

**Why it is correct here:** SGD gives 1 - 0.2 * 3 = 0.4. Momentum gives velocity 2 and weight -0.2, then velocity 1.8 + 2 = 3.8 and weight -0.2 - 0.38 = -0.58. Adam's first step stores m = 0.2 and s = 0.004; corrected they are 2 and 4, so the step is about 0.1. On the second step m = 0.38 over 0.19 is still 2 and the corrected square is still 4.

## Exercise 1: Trace plain SGD

Plain SGD uses no history in this defined rule.

**Expected:** 0.4.

```python
close(1.0 - 0.2 * jnp.float64(3.0), 0.4)
```

**Plausible wrong approach:** Moving by the old velocity before adding the gradient makes the first momentum step zero. The reference updates the velocity first, which is why the first weight is already -0.2.

## Exercise 2: Continue momentum

The second velocity includes 90 percent of the first plus the new gradient.

**Expected:** First weight -0.2; second -0.58; final velocity 3.8.

```python
w, v = momentum_step(0.0, 0.0, 2.0)
w, v = momentum_step(w, v, 2.0)
close(w, -0.58)
close(v, 3.8)
```

**Plausible wrong approach:** Calling `adam_step` twice with a fresh `zero_state` also lands near -0.2, since a constant gradient gives the same first step each time. Only the counter, 1 instead of 2, reveals the lost state.

## Exercise 3: Continue Adam's counter

For this constant gradient, corrected moments remain two and four on both steps.

**Expected:** Step two; weight approximately -0.2.

```python
w, s = adam_step(0.0, zero_state, 2.0)
w, s = adam_step(w, s, 2.0)
assert int(s[2]) == 2
close(w, -2 * 0.2 / (2.0 + 1e-8))
```

**Plausible wrong approach:** Dropping the bias correction makes the first Adam step 0.1 * 0.2 / sqrt(0.004), about 0.32, instead of about 0.1. The early moments are biased toward their zero start.

## Exercise 4: Preserve zero-gradient history

Zero current gradient is not equivalent to a fresh optimizer or no update.

**Expected:** The parameter still moves because the first moment retains history.

```python
w, s = adam_step(0.0, zero_state, 2.0)
next_w, next_s = adam_step(w, s, 0.0)
assert float(next_w) < float(w)
assert int(next_s[2]) == 2
```

**Plausible wrong approach:** Treating a zero gradient as no update ignores the stored first moment. Here m = 0.18 and the corrected values give a further step of about 0.067, so the weight keeps decreasing.

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

**Plausible wrong approach:** Comparing only the weights after `jax.jit(adam_step)` misses a state that could differ, such as a counter that failed to increment. The reference compares all three state leaves.

## Exercise 6: Reverse the gradient

The first moment changes sign while the squared moment does not.

**Expected:** A positive parameter update of 0.2/(2+1e-8).

```python
w, s = adam_step(0.0, zero_state, -2.0)
close(w, 0.2 / (2.0 + 1e-8))
close(s[0], -0.2)
close(s[1], 0.004)
```

**Plausible wrong approach:** Expecting a negative second moment after gradient -2 forgets that it stores squares. Only the first moment flips to -0.2; the square stays 0.004, so the update is +0.1.

## How to verify

Run the reference and confirm `jax-014: 8 asserted cases passed`. Then print the three state leaves after each of two Adam steps with gradient 2 and check m = 0.2 then 0.38, s = 0.004 then 0.007996, and counter 1 then 2. Dividing each by its bias correction reproduces the corrected values 2 and 4.

## Scope of this evidence

If continued training differs, compare parameters, moments, step count, learning-rate policy and the actual next batch/key. An optimizer name is not proof that returned state was retained. Match epsilon placement and reduction before comparing frameworks.

Describe the minimum state needed to reproduce one next update under this Adam rule. Explain what changes if dropout, a scheduler or data shuffling is introduced, then connect those additions to the later continuation capstone.
