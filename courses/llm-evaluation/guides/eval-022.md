# eval-022: Actual CPU PPO updates on a finite contextual policy

## Starting point and outcome

Advanced; approximately 120 minutes. Direct prerequisites: `eval-018`, `eval-021`.

Train a tiny categorical policy with the PPO surrogate and critic loss while testing frozen rollout state, optimization and independent task utility.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-022`, and use its `llm-torch-cpu` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## A small real optimization experiment

This unit performs actual PyTorch forward, backward and optimizer steps. The policy has two contexts and two actions per context. Its trainable logits form a2-by -2 table, and its critic has one value per context. The environment terminates after one action, so returns equal immediate rewards and no temporal trace is needed. This isolates PPO's objective from the GAE boundary issues studied previously.

The rollout distribution is enumerated exactly. Both contexts have probability one half, and each action is weighted by the frozen old policy's probability. This computes the surrogate expectation without sampling noise. It is not a claim that a real language-model action space can be enumerated, nor a simulation of token generation. The advantage of the reduction is that every weight, reward and update can be inspected.

At the start of each outer iteration, the code copies the current policy probabilities into a detached old snapshot. It then makes three optimizer steps against that snapshot. The reference policy remains uniform throughout training and supplies a separate KL penalty. Those two distributions serve different purposes even when they happen to match at initialization.

## Worked case A: improve the declared task reward

The useful action is 0 in the first context and 1 in the second. Starting from uniform action probabilities gives expected reward one half. The reference implementation updates the actor with the clipped PPO term and the critic with a weighted squared-error loss. It recomputes final expected reward after all updates and checks improvement beyond 0.9 on this exact finite task.

```python
import torch

torch.set_num_threads(1)
DTYPE = torch.float64


def fit_policy(reward_rows, outer_steps=24):
    reward = torch.tensor(reward_rows, dtype=DTYPE)
    if reward.shape != (2, 2):
        raise ValueError("Two contexts and two actions required")
    logits = torch.nn.Parameter(torch.zeros((2, 2), dtype=DTYPE))
    values = torch.nn.Parameter(torch.zeros(2, dtype=DTYPE))
    reference = torch.full((2, 2), 0.5, dtype=DTYPE)
    optimizer = torch.optim.SGD([logits, values], lr=0.8)
    initial = float((torch.softmax(logits, dim=-1) * reward).sum(1).mean().detach())
    for _ in range(outer_steps):
        old = torch.softmax(logits.detach(), dim=-1).clone()
        frozen = old.clone()
        advantage = (reward - values.detach()[:, None]).clone()
        weights = old / 2
        assert not old.requires_grad and not advantage.requires_grad
        for _ in range(3):
            probability = torch.softmax(logits, dim=-1)
            ratio = probability / old
            surrogate = torch.minimum(ratio * advantage, torch.clamp(ratio, 0.8, 1.2) * advantage)
            kl = (probability * (torch.log(probability) - torch.log(reference))).sum(1).mean()
            critic = (weights * (values[:, None] - reward).square()).sum()
            loss = -(weights * surrogate).sum() + 0.05 * kl + 0.5 * critic
            optimizer.zero_grad()
            loss.backward()
            assert all(
                p.grad is not None and torch.isfinite(p.grad).all() for p in (logits, values)
            )
            optimizer.step()
            torch.testing.assert_close(old, frozen, rtol=0, atol=0)
    probability = torch.softmax(logits.detach(), dim=-1)
    final = float((probability * reward).sum(1).mean())
    return probability, initial, final, values.detach()


def worked_a():
    probability, initial, final, values = fit_policy([[1, 0], [0, 1]])
    assert initial == 0.5 and final > 0.9
    torch.testing.assert_close(probability.sum(1), torch.ones(2, dtype=DTYPE))
    assert torch.isfinite(values).all() and probability.device.type == "cpu"
    print("Task reward:", initial, final, "policy:", probability.tolist())


worked_a()
```

## Worked case B: correct optimization of an incorrect reward

The second fit reverses the reward table while retaining the same independent task utility. Its training reward improves, but true task utility becomes poor. The implementation is doing what its objective requests. This is a concrete connection to reward-model shortcuts: a trustworthy gradient does not guarantee a trustworthy target.

```python
import torch

torch.set_num_threads(1)
DTYPE = torch.float64


def fit_policy(reward_rows, outer_steps=24):
    reward = torch.tensor(reward_rows, dtype=DTYPE)
    if reward.shape != (2, 2):
        raise ValueError("Two contexts and two actions required")
    logits = torch.nn.Parameter(torch.zeros((2, 2), dtype=DTYPE))
    values = torch.nn.Parameter(torch.zeros(2, dtype=DTYPE))
    reference = torch.full((2, 2), 0.5, dtype=DTYPE)
    optimizer = torch.optim.SGD([logits, values], lr=0.8)
    initial = float((torch.softmax(logits, dim=-1) * reward).sum(1).mean().detach())
    for _ in range(outer_steps):
        old = torch.softmax(logits.detach(), dim=-1).clone()
        frozen = old.clone()
        advantage = (reward - values.detach()[:, None]).clone()
        weights = old / 2
        assert not old.requires_grad and not advantage.requires_grad
        for _ in range(3):
            probability = torch.softmax(logits, dim=-1)
            ratio = probability / old
            surrogate = torch.minimum(ratio * advantage, torch.clamp(ratio, 0.8, 1.2) * advantage)
            kl = (probability * (torch.log(probability) - torch.log(reference))).sum(1).mean()
            critic = (weights * (values[:, None] - reward).square()).sum()
            loss = -(weights * surrogate).sum() + 0.05 * kl + 0.5 * critic
            optimizer.zero_grad()
            loss.backward()
            assert all(
                p.grad is not None and torch.isfinite(p.grad).all() for p in (logits, values)
            )
            optimizer.step()
            torch.testing.assert_close(old, frozen, rtol=0, atol=0)
    probability = torch.softmax(logits.detach(), dim=-1)
    final = float((probability * reward).sum(1).mean())
    return probability, initial, final, values.detach()


def worked_b():
    probability, initial, proxy_final, _ = fit_policy([[0, 1], [1, 0]])
    utility = torch.tensor([[1, 0], [0, 1]], dtype=DTYPE)
    true_final = float((probability * utility).sum(1).mean())
    assert proxy_final > 0.9 and true_final < 0.1
    print("Proxy reward:", initial, proxy_final, "independent task utility:", true_final)


worked_b()
```

## Follow the computational graph

The old probabilities are detached from the graph. The advantages also use detached value estimates. Actor gradients therefore do not secretly change the baseline or the old distribution to improve the ratio expression. The critic has its own regression term. These choices are tested directly in the reference rather than inferred from a successful loss curve.

For a one-step context, the critic's target is the immediate action reward under the old policy weighting. It estimates an expected return, not the maximum possible reward. As the actor changes, the distribution underlying that expectation changes too. An accurate value estimate for a previous policy can therefore become stale without a software defect.

The program logs state-level action probabilities and final reward. A larger training system should additionally retain rollout identity, masks, objective coefficients, clipping frequency, gradient behavior and actual KL to the old and reference policies. Objective components have different units and reductions; their coefficients are not transferable merely because another project uses the same optimizer.

## Transfer to sequence models carefully

A language-model policy uses conditional token distributions along sampled histories. Its data pipeline must distinguish prompt tokens, generated tokens, padding, truncation and true stopping. Rollout collection, advantage estimation, reference log probabilities and held-out evaluation become separate substantial components. The finite example verifies none of their model-serving or accelerator properties.

Use this exercise to understand and diagnose the optimization mechanism before adopting a larger implementation. Keep a separate evaluation corpus, task utility and critical-policy checks. A new reward or prompt can change the data-generating process, so a previous successful optimization run is not evidence that the modified assistant will behave acceptably.


## Six investigations

### 1. Trace the expectation weights

Sum old-policy weights across both contexts and actions.

**Expected:** The total is 1.

**Hint:** Each context contributes probability 0.5.

### 2. Inspect frozen state

Compare the old probability tensor before and after each inner update.

**Expected:** It is byte-for-byte numerically unchanged.

**Hint:** Detach and copy the collector snapshot.

### 3. Separate critic and actor gradients

Explain why the advantage uses detached values.

**Expected:** The actor cannot improve its objective by changing its baseline through that path.

**Hint:** The critic is trained by a separate squared-error term.

### 4. Check symmetry

Swap the two contexts and their useful actions.

**Expected:** The learned probability rows mirror each other.

**Hint:** Both start from the same logits and use symmetric rewards.

### 5. Optimize a bad proxy

Run case B and evaluate the resulting policy under the original task utility.

**Expected:** Training reward exceeds 0.9 while task utility is below 0.1.

**Hint:** Keep the evaluation utility outside the optimizer.

### 6. State the scale boundary

List what this actual training run omits from an LLM deployment.

**Expected:** Tokenization, sampled language rollouts, long-horizon credit, pretrained weights and serving are absent.

**Hint:** Name the finite state/action representation.

## Primary references

- [PyTorch optimization mechanics](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html)
- [PPO algorithm](https://arxiv.org/abs/1707.06347)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
