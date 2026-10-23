# llm-012: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Decoding converts a next-token probability distribution into a selected token. Greedy decoding chooses the maximum score with a declared tie rule. Sampling uses a random draw and cumulative probability intervals, so its result depends on the seed or supplied draw. Temperature divides logits before softmax: positive temperatures change concentration while preserving ranking. Top-k removes all but a fixed number of candidate tokens and renormalizes the remaining mass. These are inference policies, not changes to learned model weights. The tiny three-token vocabulary makes every interval visible and separates stochastic choice from a model's probability calculation.

**Greedy decoding:** Selecting a highest-scoring token under a tie policy.

**Temperature:** Positive divisor controlling score concentration before softmax.

**Top-k:** A filter retaining the k highest-scoring candidates.

## Reading the implementation

Subtract the maximum before exponentiation. Require positive temperature for stochastic sampling; handle zero-temperature greedy mode separately. np.argmax returns the first maximum, which implements the declared smallest-index tie rule. np.searchsorted(cumulative,draw,side='right') selects the interval containing a draw in[0,1). Filter candidates before the final normalization.

## Exercise 1: Calculate greedy choice

The question is: Use scores[2,1,0] and choose the maximum index.

Only ranking matters to greedy selection. A common shift or positive temperature preserves this particular decision.

```python
scores=np.array([2.,1.,0.]); assert int(np.argmax(scores))==0
```

**Expected:** token0.

**Verify:** Compare the computed values or written argument with token0.

## Exercise 2: Change temperature

The question is: Compare probabilities at temperatures1 and.5 using stable softmax.

Sharper probabilities make high-scoring tokens more likely without changing their order. They do not create new evidence that the selected token is correct.

```python
p=softmax(scores); cool=softmax(scores/.5)
assert cool[0]>p[0] and p.argmax()==cool.argmax()==0
```

**Expected:** token0 probability increases; argmax stays0.

**Verify:** Compare the computed values or written argument with token0 probability increases; argmax stays0.

## Exercise 3: Use fixed draws

The question is: Sample from probabilities[.5,.3,.2] with draws .1,.6,.9.

The intervals are[0,.5),[.5,.8),[.8,1). Supplying draws directly makes the sampling mechanism testable without relying on a platform random bit pattern.

```python
mass=np.array([.5,.3,.2]); cumulative=np.cumsum(mass)
assert [int(np.searchsorted(cumulative,d,side='right')) for d in [.1,.6,.9]]==[0,1,2]
```

**Expected:** tokens0,1,2.

**Verify:** Compare the computed values or written argument with tokens0,1,2.

## Exercise 4: Retain two candidates

The question is: Apply top-k2 to scores[2,1,0] and normalize only retained candidates.

Zeroing a probability after softmax without renormalizing would leave missing mass. Filtering is a policy that changes the final distribution.

```python
allowed=np.argsort(-scores,kind='stable')[:2]; filtered=np.zeros(3); filtered[allowed]=softmax(scores[allowed])
assert filtered[2]==0; np.testing.assert_allclose(filtered.sum(),1,atol=1e-12,rtol=0)
```

**Expected:** token 2 probability0; first two sum1.

**Verify:** Compare the computed values or written argument with token 2 probability0; first two sum1.

## Exercise 5: Declare ties

The question is: Use equal scores[1,1,0] and choose the smallest-index maximum.

A deterministic tie rule makes repeated decisions explainable. Other valid policies exist, but an undocumented implementation detail should not determine a public contract.

```python
assert int(np.argmax([1,1,0]))==0
```

**Expected:** token0 under the stated rule.

**Verify:** Compare the computed values or written argument with token0 under the stated rule.

## Exercise 6: Reject invalid draws

The question is: Validate draws0,.999,1 and-.1 before cumulative lookup.

A draw of one lies outside every half-open interval and can produce an out-of-range token. Input validation keeps a random-source contract failure distinct from vocabulary indexing.

```python
def validate_draw(draw):
    if not np.isfinite(draw) or not 0<=draw<1: raise ValueError('draw in [0,1)')
    return draw
assert validate_draw(0)==0 and validate_draw(.999)==.999
for bad in [1,-.1]:
    try: validate_draw(bad)
    except ValueError: pass
    else: raise AssertionError('invalid draw')
```

**Expected:** 0 and.999 accepted;1 and-.1 rejected.

**Verify:** Compare the computed values or written argument with 0 and.999 accepted;1 and-.1 rejected.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
