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

# Task 1: Sum old-policy weights across both contexts and actions.
# Task 2: Compare the old probability tensor before and after each inner update.
# Task 3: Explain why the advantage uses detached values.
# Task 4: Swap the two contexts and their useful actions.
# Task 5: Run case B and evaluate the resulting policy under the original task utility.
# Task 6: List what this actual training run omits from an LLM deployment.

# Implement your six changes below.
