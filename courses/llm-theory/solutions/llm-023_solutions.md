# llm-023: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Top-p decoding retains the smallest probability-ranked prefix whose cumulative mass reaches a threshold, including the token that crosses it. With probabilities.5,.3,.2 andp=.6, retaining only the first token would leave mass.5 and fail the rule; the first two tokens provide mass.8. Renormalize the retained mass before sampling. Termination is a separate control: stop immediately after an end-of-sequence token and also impose a maximum generated-token count. Zero-temperature greedy selection should be a distinct branch, because dividing by zero is not a sampling algorithm. None of these policies establishes factual correctness.

**Nucleus:** The retained probability prefix under a top-p policy.

**EOS:** A designated end-of-sequence token.

**Token cap:** A hard upper limit on newly generated tokens.

## Reading the implementation

Sort probabilities descending with a stable tie policy, compute cumulative sums and retain each token whose preceding cumulative mass is belowp. This formulation keeps the crossing token. torch.Generator(device='cpu') with a fixed seed makes repeated sampling locally reproducible. Generation loops check EOS after appending a chosen token and before requesting another token.

## Exercise 1: Retain the crossing token

The question is: Apply top-p.6 to probabilities[.5,.3,.2].

Testing the cumulative mass before each token keeps the first token that crosses the threshold. Filtering on cumulative<=p would incorrectly drop it.

```python
p=torch.tensor([.5,.3,.2]); sorted_p,order=torch.sort(p,descending=True,stable=True); previous=torch.cumsum(sorted_p,0)-sorted_p; keep=previous<.6
assert order[keep].tolist()==[0,1]; np.testing.assert_allclose(sorted_p[keep].sum().item(),.8,atol=1e-6,rtol=0)
```

**Expected:** retained IDs0,1 with original mass.8.

**Verify:** Compare the computed values or written argument with retained IDs0,1 with original mass.8.

## Exercise 2: Renormalize retained mass

The question is: Normalize the selected two probabilities before drawing.

The discarded mass is removed from the candidate set. The remaining entries must sum to one to define the sampling distribution.

```python
mass=sorted_p[keep]; normalized=mass/mass.sum()
np.testing.assert_allclose(normalized.numpy(),[.625,.375],atol=1e-6,rtol=0)
```

**Expected:** probabilities.625,.375.

**Verify:** Compare the computed values or written argument with probabilities.625,.375.

## Exercise 3: Reproduce local sampling

The question is: Draw8 tokens with two independently seeded CPU generators.

The seed establishes repeatability in the current runtime. The test does not hardcode a random sequence that might change across implementations.

```python
g1=torch.Generator().manual_seed(7); g2=torch.Generator().manual_seed(7)
a=torch.multinomial(normalized,8,replacement=True,generator=g1); b=torch.multinomial(normalized,8,replacement=True,generator=g2)
assert torch.equal(a,b) and set(a.tolist())<={0,1}
```

**Expected:** draw sequences match and contain only0,1.

**Verify:** Compare the computed values or written argument with draw sequences match and contain only0,1.

## Exercise 4: Stop on EOS

The question is: Consume proposed tokens2,3,9,4 with EOS9 and cap5.

EOS terminates the sequence immediately. A later iteration could accidentally append content after the end marker, so the stopping location matters.

```python
generated=[]
for token in [2,3,9,4]:
    generated.append(token)
    if token==9 or len(generated)>=5: break
assert generated==[2,3,9]
```

**Expected:** generated2,3,9;4 is never consumed.

**Verify:** Compare the computed values or written argument with generated2,3,9;4 is never consumed.

## Exercise 5: Enforce a cap without EOS

The question is: Consume an endless repeated token2 under cap3.

A model is not guaranteed to emit EOS. A separate token cap provides a deterministic work bound even when the distribution keeps preferring continuation.

```python
generated=[]
for _ in range(100):
    if len(generated)>=3: break
    generated.append(2)
assert generated==[2,2,2]
```

**Expected:** exactly3 generated tokens.

**Verify:** Compare the computed values or written argument with exactly3 generated tokens.

## Exercise 6: Separate greedy mode

The question is: Handle temperature0 with argmax rather than division.

Greedy decoding has a valid definition at zero temperature as a separate policy. Evaluating logits/0 first would create invalid values before that policy could act.

```python
logits=torch.tensor([2.,1.,0.]); temperature=0
choice=int(logits.argmax()) if temperature==0 else -1
assert choice==0 and torch.isfinite(logits).all()
```

**Expected:** token0 and finite untouched logits.

**Verify:** Compare the computed values or written argument with token0 and finite untouched logits.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
