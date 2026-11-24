# eval-022: explained reference

`eval-022_reference.py` asserts each answer below, from *Trace the expectation weights* to *State the scale boundary*, on the authored PyTorch PPO and frozen rollout policy fixture only. Before applying a conclusion to other data, recheck the assumption that *Separate critic and actor gradients* tests.

## 1. Trace the expectation weights

An unweighted average over actions would cease to represent the old-policy expectation once the policy becomes nonuniform.

**Approach.** Compute `weights = old / 2` for two contexts with two actions each, then sum all four entries.

**Why it holds for this fixture.** Each context has probability 1 / 2 and each row of `old` sums to 1, so the weights sum to 1 / 2 + 1 / 2 = 1. At the uniform start every weight is 0.25. Weighting by `old` keeps the objective an expectation under the sampling policy as it becomes nonuniform.

**A tempting wrong approach.** Averaging the surrogate equally over the four actions matches only while the policy is uniform. Once one action has probability 0.9, equal weights would overcount the rare action.

**How to verify.** The reference asserts `float(weights.sum()) == 1` for the uniform `old`. Inside `fit_policy`, print `weights.sum()` each outer step and confirm 1.

**Expected observation:** The total is 1.

## 2. Inspect frozen state

Current-policy updates must not move the denominator of their own importance ratio.

**Approach.** Clone `old` into `frozen` at the start of each outer step and compare them after every inner update with zero tolerance.

**Why it holds for this fixture.** `old` is computed from `logits.detach()`, so optimizer steps on `logits` cannot change it. The comparison with `rtol=0, atol=0` confirms that exactly.

**A tempting wrong approach.** Writing `old = torch.softmax(logits, dim=-1)` without detach would leave it in the graph, so gradients would flow into the denominator. Exact equality catches both that and accidental in-place edits.

**How to verify.** `fit_policy` calls `torch.testing.assert_close(old, frozen, rtol=0, atol=0)` after each of the three inner steps.

**Expected observation:** It is byte-for-byte numerically unchanged.

## 3. Separate critic and actor gradients

Without this graph boundary the implemented gradient would contain an unintended optimization route.

**Approach.** Compute the advantage as `reward - values.detach()[:, None]` so the actor loss treats the baseline as a constant. Train the critic through its own squared-error term.

**Why it holds for this fixture.** If the baseline were not detached, the actor term could push `values` in whichever direction raises the surrogate, not toward predicting reward. The critic would be pulled away from its own target.

**A tempting wrong approach.** Assuming one combined loss sorts this out automatically is the mistake. Without the detach, the gradient on `values` contains an extra actor path no one intended.

**How to verify.** `fit_policy` asserts `not advantage.requires_grad`. Removing `.detach()` and comparing the learned `values` shows the difference.

**Expected observation:** The actor cannot improve its objective by changing its baseline through that path.

## 4. Check symmetry

This invariant tests the small environment and update implementation independently of a particular random seed.

**Approach.** Train with rewards `[[1, 0], [0, 1]]` for 12 outer steps and compare row 0 of the learned probabilities with row 1 reversed.

**Why it holds for this fixture.** Context 0 rewards action 0 and context 1 rewards action 1, a mirror image. Initialization, reference and updates are all symmetric, so the learned rows must be mirror images to numerical precision.

**A tempting wrong approach.** Accepting any final reward above 0.5 as correct would miss a bug that treats contexts differently, such as a wrong reduction axis. Symmetry tests the plumbing directly.

**How to verify.** The reference asserts `torch.testing.assert_close(probability[0], probability[1].flip(0), atol=1e-12, rtol=1e-12)` and that `final > initial`.

**Expected observation:** The learned probability rows mirror each other.

## 5. Optimize a bad proxy

Correct execution of PPO cannot validate a mistaken or exploitable reward definition.

**Approach.** Run `fit_policy([[0, 1], [1, 0]])` as in case B, then score the learned policy with the true utility `[[1, 0], [0, 1]]`.

**Why it holds for this fixture.** The proxy rewards the opposite action in each context. PPO maximizes it, reaching proxy reward above 0.9, and the true utility falls below 0.1 because the policy now prefers exactly the wrong actions.

**A tempting wrong approach.** Reading the rising training reward as evidence the policy improved is the mistake. The optimizer worked correctly; the reward definition was wrong, and only an independent utility shows it.

**How to verify.** Case B asserts `proxy_final > 0.9 and true_final < 0.1`. This is the same pattern as eval-019's proxy example.

**Expected observation:** Training reward exceeds 0.9 while task utility is below 0.1.

## 6. State the scale boundary

The run establishes a small CPU optimization mechanism, not a production language model or a guarantee of safe alignment.

**Approach.** List what the run lacks: a tokenizer, sampled text rollouts, multi-step credit over long outputs, pretrained weights, batching on accelerators and serving.

**Why it holds for this fixture.** The model is a 2 by 2 table of logits with two values, trained on exact expected rewards in float64 on CPU. It demonstrates the PPO update mechanics and frozen-state checks, nothing more.

**A tempting wrong approach.** Calling this an LLM alignment run is the mistake. None of the difficulties of language rollouts, such as noisy reward models or long sequences, are present.

**How to verify.** `worked_a` asserts the probabilities are on `cpu` and rows sum to 1. A write-up should state the 2 contexts, 2 actions and the step counts.

**Expected observation:** Tokenization, sampled language rollouts, long-horizon credit, pretrained weights and serving are absent.
