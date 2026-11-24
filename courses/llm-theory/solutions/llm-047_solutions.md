# llm-047: explanatory solutions

Read these sparse experts, routing capacity and load balancing answers after attempting *Calculate a top-2 expert mixture* through *Validate routing policy and ties*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Compute a load-balancing term* points to one step. `llm-047_solution.py` holds the assertions; this page explains how they test sparse expert activation. Then try *Validate routing policy and ties* on a fresh input you chose before looking.

## Mechanism review

A mixture-of-experts layer routes each token to a subset of specialized transformations. The total model can contain many expert parameters while activating only a few per token. That does not make memory or communication free: all experts must be stored somewhere, and distributed routing moves token activations to the devices owning selected experts. Uneven routing can overload one expert while others remain idle.

The router produces scores or probabilities over experts. A top-k decision selects indices, then a declared gate rule weights the selected outputs. Some designs retain selected probabilities from the full softmax; others renormalize among selected experts. Those choices change gradients and output scale. This lesson states its rule explicitly: the top-k mixture renormalizes selected mass, while the capacity demonstration uses a unit-weight top-1 expert delta inside a residual path.

Capacity bounds how many tokens an expert accepts in one batch. Overflow needs a visible policy, such as dropping the expert delta and using the residual path. A load-balancing auxiliary objective can encourage less concentrated routing, but it does not prove that a system achieves good load balance, quality or throughput. The reference uses literal linear experts and finite-difference router gradients; it does not launch expert-parallel workers or claim large-model scaling.

**Sparse expert activation:** Evaluating only selected experts for each token.

**Router:** A function producing expert-selection scores for each token.

**Capacity:** A bound on tokens admitted to an expert in one batch.

**Load-balancing loss:** An auxiliary objective encouraging a less concentrated routing distribution.

**Expert parallelism:** Placing different experts on different devices and moving activations between them.

## Reading the implementation

Inputs have shape (tokens, model_width), router logits(tokens, experts), and expert matrices(experts, model_width, output_width). Stable descending argsort declares a lowest-index tie policy. The selected gates are normalized before combining expert outputs. The capacity helper tracks assigned counts, accepted counts and dropped-token flags separately. A Switch-style auxiliary term uses hard assignment fractions f and mean router probabilities P, with the hard fractions held fixed for a local gradient calculation.

## Exercise 1: Calculate a top-2 expert mixture

The question is: Use experts I, 2I, -I and three token/router rows with selected probabilities \(\frac{3}{4}\) and \(\frac{1}{4}\).

The third token combines a negative expert with a positive expert, so routing can change the function rather than merely selecting a faster implementation of the same computation.

```python
x = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
experts = np.stack([np.eye(2), 2 * np.eye(2), -np.eye(2)])
logits = np.array([[np.log(3), 0.0, -100.0], [0.0, np.log(3), -100.0], [-100.0, 0.0, np.log(3)]])
output, indices, gates = mixture(x, logits, experts, 2)
np.testing.assert_allclose(output, [[1.25, 0], [0, 1.75], [-0.25, -0.25]], atol=1e-12, rtol=0)
np.testing.assert_allclose(gates.sum(1), 1, atol=1e-12, rtol=0)
```

**Expected:** outputs [1.25, 0], [0, 1.75], [-0.25, -0.25].

**Verify:** For *Calculate a top-2 expert mixture*, a fresh-process check confirms `output` matches `[[1.25, 0], [0, 1.75], [-0.25, -0.25]]` within 1e-12 and `gates.sum(1)` matches `1` within 1e-12.

## Exercise 2: Enforce expert capacity with residual fallback

The question is: Route four tokens to experts 0, 0, 1, 0 with capacity 2 and unit top-1 gates.

The dropped token is not deleted from the sequence or loss denominator. Its residual path is explicit, and the drop count remains available for quality and load analysis.

```python
tokens = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [2.0, 1.0]])
route_logits = np.array([[5.0, 0.0], [4.0, 0.0], [0.0, 4.0], [3.0, 0.0]])
residual, dropped, assigned, accepted = capacity_route(tokens, route_logits, experts[:2], 2)
assert (
    assigned.tolist() == [3, 1]
    and accepted.tolist() == [2, 1]
    and dropped.tolist() == [False, False, False, True]
)
np.testing.assert_allclose(residual, [[2, 0], [0, 2], [3, 3], [2, 1]], atol=1e-12, rtol=0)
```

**Expected:** assigned counts 3, 1; accepted 2, 1; last token drops its expert delta and keeps its input.

**Verify:** For *Enforce expert capacity with residual fallback*, a fresh-process check confirms `assigned.tolist() == [3, 1]`; `accepted.tolist() == [2, 1]`; `dropped.tolist() == [False, False, False, True]` and `residual` matches `[[2, 0], [0, 2], [3, 3], [2, 1]]` within 1e-12.

## Exercise 3: Compute a load-balancing term

The question is: Use hard fractions f = [0.75, 0.25], mean router probabilities P = [0.7, 0.3], expert count 2 and coefficient 0.01.

The term measures a routing-related objective under the declared formula. A lower auxiliary value is not itself evidence that task loss, capacity drops or distributed utilization improved.

```python
fractions = np.array([0.75, 0.25])
mean_probability = np.array([0.7, 0.3])
coefficient = 0.01
loss = coefficient * 2 * np.dot(fractions, mean_probability)
np.testing.assert_allclose(loss, 0.012, atol=1e-12, rtol=0)
np.testing.assert_allclose(
    coefficient * 2 * np.dot([0.5, 0.5], [0.5, 0.5]), 0.01, atol=1e-12, rtol=0
)
```

**Expected:** auxiliary loss .012; balanced fixture .01.

**Verify:** For *Compute a load-balancing term*, a fresh-process check confirms `loss` matches `0.012` within 1e-12 and `coefficient * 2 * np.dot([0.5, 0.5], [0.5, 0.5])` matches `0.01` within 1e-12.

## Exercise 4: Trace a local router gradient

The question is: Perturb the first logit of the first top-2 mixture row without changing selected experts.

Within a fixed selected set, the normalized gates vary smoothly. At a top-k membership boundary, the hard index choice is not differentiable in the same way. Do not interpret this local derivative as differentiating through every routing decision.

```python
h = 1e-6
plus = logits.copy()
minus = logits.copy()
plus[0, 0] += h
minus[0, 0] -= h
numeric = (mixture(x, plus, experts, 2)[0][0, 0] - mixture(x, minus, experts, 2)[0][0, 0]) / (2 * h)
np.testing.assert_allclose(numeric, -3 / 16, atol=1e-8, rtol=0)
```

**Expected:** derivative of first output coordinate is \(\frac{-3}{16}\) within 1e-8.

**Verify:** For *Trace a local router gradient*, a fresh-process check confirms `numeric` matches `-3 / 16` within 1e-8.

## Exercise 5: Separate total and active parameter counts

The question is: Use 8 two-layer experts with width 64, hidden width 128 and top-2 activation, excluding router and biases.

Inactive expert weights still occupy memory somewhere. Active-weight arithmetic does not measure peak memory, token dispatch cost orall-to-all communication.

```python
expert_count, width, hidden, active = 8, 64, 128, 2
assert expert_count * 2 * width * hidden == 131072
assert active * 2 * width * hidden == 32768
```

**Expected:** total 131072 expert weights; 32768 selected expert weights per token.

**Verify:** For *Separate total and active parameter counts*, a fresh-process check confirms `expert_count * 2 * width * hidden == 131072` and `active * 2 * width * hidden == 32768`.

## Exercise 6: Validate routing policy and ties

The question is: Reject top-k 0 and capacity 0; check that equal router logits choose lower indices deterministically.

Tie and overflow policies affect reproducibility and which tokens receive expert computation. They must be explicit before comparing model quality or load statistics.

```python
_, tied, _ = mixture(np.ones((1, 2)), np.zeros((1, 3)), experts, 2)
assert tied.tolist() == [[0, 1]]
for action in [
    lambda: mixture(x, logits, experts, 0),
    lambda: capacity_route(tokens, route_logits, experts[:2], 0),
]:
    try:
        action()
    except ValueError:
        pass
    else:
        raise AssertionError("invalid routing policy accepted")
```

**Expected:** invalid policies raise ValueError; top-2 tie indices 0, 1.

**Verify:** For *Validate routing policy and ties*, a fresh-process check confirms `tied.tolist() == [[0, 1]]` and for every looped case, `action()` raises `ValueError`.

## Review after comparison

Change one input to *Trace a local router gradient* and predict the result first; keep *Validate routing policy and ties* failing beside the repair. Log a missing NumPy separately from a wrong sparse expert activation value in `llm-047`.
