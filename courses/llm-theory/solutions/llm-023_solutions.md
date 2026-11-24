# llm-023: explanatory solutions

Read these top-p, termination and decoding failure cases answers after attempting *Retain the crossing token* through *Separate greedy mode*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Reproduce local sampling* points to one step. `llm-023_solution.py` holds the assertions; this page explains how they test nucleus. Then try *Separate greedy mode* on a fresh input you chose before looking.

## Mechanism review

Top-p decoding retains the smallest probability-ranked prefix whose cumulative mass reaches a threshold, including the token that crosses it. With probabilities 0.5, 0.3, 0.2 and p=0.6, retaining only the first token would leave mass 0.5 and fail the rule; the first two tokens provide mass 0.8. Renormalize the retained mass before sampling. Termination is a separate control: stop immediately after an end-of-sequence token and also impose a maximum generated-token count. Zero-temperature greedy selection should be a distinct branch, because dividing by zero is not a sampling algorithm. None of these policies establishes factual correctness.

**Nucleus:** The retained probability prefix under a top-p policy.

**EOS:** A designated end-of-sequence token.

**Token cap:** A hard upper limit on newly generated tokens.

## Reading the implementation

Sort probabilities descending with a stable tie policy, compute cumulative sums and retain each token whose preceding cumulative mass is below p. This formulation keeps the crossing token. torch.Generator(device='cpu') with a fixed seed makes repeated sampling locally reproducible. Generation loops check EOS after appending a chosen token and before requesting another token.

## Exercise 1: Retain the crossing token

The question is: Apply top-p 0.6 to probabilities [0.5, 0.3, 0.2].

Testing the cumulative mass before each token keeps the first token that crosses the threshold. Filtering on cumulative<=p would incorrectly drop it.

```python
p = torch.tensor([0.5, 0.3, 0.2])
sorted_p, order = torch.sort(p, descending=True, stable=True)
previous = torch.cumsum(sorted_p, 0) - sorted_p
keep = previous < 0.6
assert order[keep].tolist() == [0, 1]
np.testing.assert_allclose(sorted_p[keep].sum().item(), 0.8, atol=1e-6, rtol=0)
```

**Expected:** retained IDs 0, 1 with original mass 0.8.

**Verify:** For *Retain the crossing token*, a fresh-process check confirms `order[keep].tolist() == [0, 1]` and `sorted_p[keep].sum().item()` matches `0.8` within 1e-6.

## Exercise 2: Renormalize retained mass

The question is: Normalize the selected two probabilities before drawing.

The discarded mass is removed from the candidate set. The remaining entries must sum to one to define the sampling distribution.

```python
mass = sorted_p[keep]
normalized = mass / mass.sum()
np.testing.assert_allclose(normalized.numpy(), [0.625, 0.375], atol=1e-6, rtol=0)
```

**Expected:** probabilities 0.625, 0.375.

**Verify:** For *Renormalize retained mass*, a fresh-process check confirms `normalized.numpy()` matches `[0.625, 0.375]` within 1e-6.

## Exercise 3: Reproduce local sampling

The question is: Draw 8 tokens with two independently seeded CPU generators.

The seed establishes repeatability in the current runtime. The test does not hardcode a random sequence that might change across implementations.

```python
g1 = torch.Generator().manual_seed(7)
g2 = torch.Generator().manual_seed(7)
a = torch.multinomial(normalized, 8, replacement=True, generator=g1)
b = torch.multinomial(normalized, 8, replacement=True, generator=g2)
assert torch.equal(a, b) and set(a.tolist()) <= {0, 1}
```

**Expected:** draw sequences match and contain only 0, 1.

**Verify:** For *Reproduce local sampling*, a fresh-process check confirms `torch.equal(a, b)` and `set(a.tolist()) <= {0, 1}`.

## Exercise 4: Stop on EOS

The question is: Consume proposed tokens 2, 3, 9, 4 with EOS ID 9 and cap 5.

EOS terminates the sequence immediately. A later iteration could accidentally append content after the end marker, so the stopping location matters.

```python
generated = []
for token in [2, 3, 9, 4]:
    generated.append(token)
    if token == 9 or len(generated) >= 5:
        break
assert generated == [2, 3, 9]
```

**Expected:** generated 2, 3, 9; 4 is never consumed.

**Verify:** For *Stop on EOS*, a fresh-process check confirms `generated == [2, 3, 9]`.

## Exercise 5: Enforce a cap without EOS

The question is: Consume an endless repeated token 2 under cap 3.

A model is not guaranteed to emit EOS. A separate token cap provides a deterministic work bound even when the distribution keeps preferring continuation.

```python
generated = []
for _ in range(100):
    if len(generated) >= 3:
        break
    generated.append(2)
assert generated == [2, 2, 2]
```

**Expected:** exactly 3 generated tokens.

**Verify:** For *Enforce a cap without EOS*, a fresh-process check confirms `generated == [2, 2, 2]`.

## Exercise 6: Separate greedy mode

The question is: Handle temperature 0 with argmax rather than division.

Greedy decoding has a valid definition at zero temperature as a separate policy. Evaluating \(\frac{\mathrm{logits}}{0}\) first would create invalid values before that policy could act.

```python
logits = torch.tensor([2.0, 1.0, 0.0])
temperature = 0
choice = int(logits.argmax()) if temperature == 0 else -1
assert choice == 0 and torch.isfinite(logits).all()
```

**Expected:** token 0 and finite untouched logits.

**Verify:** For *Separate greedy mode*, a fresh-process check confirms `choice == 0` and `torch.isfinite(logits).all()`.

## Review after comparison

Change one input to *Stop on EOS* and predict the result first; keep *Enforce a cap without EOS* failing beside the repair. Log a missing PyTorch separately from a wrong nucleus value in `llm-023`.
