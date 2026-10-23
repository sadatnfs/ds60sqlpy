# llm-048: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Speculative decoding proposes several tokens with a cheaper draft model and verifies them against a target model. Exact speculative sampling is not simply accepting a token when the two argmaxes agree. The acceptance rule and the correction distribution are chosen so the emitted token law remains the target distribution under the declared sampling policy. This preserves a distribution, not necessarily the same individual sample produced by another random-number schedule.

For target probabilities p and draft probabilities q at the same prefix, a draft token i is accepted with probability min(1, p_i/q_i). If rejected, sample from the normalized positive part of p-q. Accepted draft mass and corrected rejection mass add back to p exactly. The distributions must already include the intended temperature or filtering policy, and both models must refer to the same token identities.

A multi-token round accepts a contiguous prefix of draft proposals. At the first rejection, discard the unaccepted suffix and emit one correction token. If all proposals are accepted, an additional token can be drawn from the target's next distribution when the budget permits. Cached keys/values for discarded draft positions must be rolled back, and the correction or bonus token must be appended at its correct position. The reference uses exact probability tables and real small NumPy K/V arrays. It does not run a fast serving kernel or claim a measured speedup.

**Draft distribution:** The proposal model's next-token probabilities at a specific prefix.

**Acceptance probability:** The correction rulemin(1,p_i/q_i) for a sampled draft token.

**Residual distribution:** Normalized positive mass from p-q used after rejection.

**Bonus token:** A target-sampled next token after an entirely accepted proposal block.

**Cache rollback:** Removing state for unaccepted speculative positions before continuing.

## Reading the implementation

Validate finite nonnegative probability vectors with unit mass. Sample using an explicit draw in[0, 1), with half-open cumulative intervals. Compute acceptance ratios only where q is positive; a zero-q token cannot be a valid draft sample. The round helper stores the draft distributions at their proposal prefixes, then verifies in order and stops at the first rejection or accepted EOS. A TinyCache stores position-dependent key vectors and value vectors so rollback can be checked against a fresh reconstruction.

Sampling builds the cumulative distribution on positive-support entries only, then maps the selected index back to the original token ID. The final cumulative boundary is assigned to the last positive entry, so floating-point rounding cannot create a tail interval for a zero-probability token. Half-open interval behavior is retained at internal boundaries.

## Exercise 1: Prove one-step distribution preservation

The question is: Use p[.5, .3, .2] and q[.2, .5, .3]; calculate accepted mass, rejection mass and residual.

The equality is an exact probability decomposition up to floating-point arithmetic. It is stronger than observing approximate frequencies in a finite simulation.

```python
p=np.array([.5,.3,.2]); q=np.array([.2,.5,.3]); acceptance,residual,rejection=correction(p,q)
accepted_mass=q*acceptance
np.testing.assert_allclose(accepted_mass,[.2,.3,.2],atol=1e-12,rtol=0)
np.testing.assert_allclose(rejection,.3,atol=1e-12,rtol=0); np.testing.assert_allclose(residual,[1,0,0],atol=1e-12,rtol=0)
np.testing.assert_allclose(accepted_mass+rejection*residual,p,atol=1e-12,rtol=0)
```

**Expected:** accepted mass[.2, .3, .2]; rejection .3; residual[1, 0, 0]; combined mass p.

**Verify:** Compare the computed values or written argument with accepted mass[.2, .3, .2]; rejection .3; residual[1, 0, 0]; combined mass p.

## Exercise 2: Exercise acceptance and correction paths

The question is: Propose token 1 with acceptance draw .8, then token 2 with draw .5.

For token 1, the acceptance threshold is.3/.5=.6. For token 2, it is.2/.3=2/3. The supplied draws make both branches deterministic and inspectable.

```python
rejected=one_step(p,q,1,.8,.9); accepted=one_step(p,q,2,.5,.1)
assert rejected=={'token':0,'accepted':False} and accepted=={'token':2,'accepted':True}
```

**Expected:** token 1 rejected and corrected to 0; token 2 accepted.

**Verify:** Compare the computed values or written argument with token 1 rejected and corrected to 0; token 2 accepted.

## Exercise 3: Check an all-accepted round and bonus token

The question is: Set draft and target equal to p; propose tokens 0, 1 with draws .1, .6, and use bonus draw .7.

When draft and target distributions agree, every proposal is accepted. The extra token comes from the target distribution after the accepted prefix, not from a residual whose mass is zero.

```python
same=lambda prefix:p
all_accepted=speculative_round([],same,same,[.1,.6],[.9,.9],.7,budget=3)
assert all_accepted['tokens']==[0,1,1] and all_accepted['accepted_count']==2 and not all_accepted['rejected']
```

**Expected:** emitted[0, 1, 1]; accepted_count 2; no rejection.

**Verify:** Compare the computed values or written argument with emitted[0, 1, 1]; accepted_count 2; no rejection.

## Exercise 4: Stop at the first rejection

The question is: Use constant target p, draft q, proposal draws .1, .3 and acceptance draws .2, .9.

Theunacceptedtoken 1andsuffixcannotremainin theoutputprefix. Anyfuturetargetprobabilitymustconditionon theacceptedtoken0 and correction 0 instead.

```python
round_result=speculative_round([2],lambda prefix:p,lambda prefix:q,[.1,.3],[.2,.9],.4,budget=3)
assert round_result['proposals']==[0,1] and round_result['tokens']==[0,0] and round_result['accepted_count']==1 and round_result['rejected']
```

**Expected:** draft[0, 1]; accepted prefix[0]; correction 0; emitted[0, 0].

**Verify:** Compare the computed values or written argument with draft[0, 1]; accepted prefix[0]; correction 0; emitted[0, 0].

## Exercise 5: Rollback actual K/V arrays

The question is: Start cache prefix[2], append the two proposals, then roll back and append the correction; compare with a fresh cache[2, 0, 0].

The cache stores numerical position-dependentkeys, not only a tokenlist. Retaining a rejected suffix changes both context andposition offsets even if the next sampled token iscorrect.

```python
cache=TinyCache([2]); old_length=len(cache.tokens)
for token in round_result['proposals']: cache.append(token)
broken=TinyCache(cache.tokens)
apply_round(cache,old_length,round_result); fresh=TinyCache([2,0,0])
assert cache.tokens==fresh.tokens; np.testing.assert_allclose(cache.keys,fresh.keys,atol=0,rtol=0); np.testing.assert_allclose(cache.output(),fresh.output(),atol=1e-12,rtol=0)
broken.append(0); assert broken.tokens!=fresh.tokens and not np.allclose(broken.output(),fresh.output())
```

**Expected:** tokens, keys, values and attention output match a fresh cache; retaining a rejected token breaks parity.

**Verify:** Compare the computed values or written argument with tokens, keys, values and attention output match a fresh cache; retaining a rejected token breaks parity.

## Exercise 6: Handle equality, EOS, budgets and invalid support

The question is: Check p=q has no residual, stop on an accepted EOS 2, cap output at 2 tokens, and reject a zero-probability draft proposal.

An accepted EOS ends generation immediately, andabudget is not permission toappendanextra bonus. Equaldistributionsmustavoid dividingbyazero residualnormalizer. Invalidsupport shouldfailclearly ratherthan fabricate aprobability.

```python
alpha,none,mass=correction(p,p); assert mass==0 and none is None and np.all(alpha==1)
eos=speculative_round([],same,same,[.95,.1],[.2,.2],.1,budget=3,eos=2); assert eos['tokens']==[2]
limited=speculative_round([],same,same,[.1,.6],[.9,.9],.7,budget=2); assert len(limited['tokens'])==2
try: one_step(np.array([.5,.5]),np.array([1.,0.]),1,.2,.3)
except ValueError: pass
else: raise AssertionError('impossible draft token accepted')
```

**Expected:** rejection mass is 0 and residual is None; accepted EOS stops generation; the token cap is respected; unsupported proposals raise ValueError.

**Verify:** Compare the computed values or written argument with rejection mass is 0 and residual is None; accepted EOS stops generation; the token cap is respected; unsupported proposals raise ValueError.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
