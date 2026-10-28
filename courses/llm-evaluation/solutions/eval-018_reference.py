import torch

torch.set_num_threads(1)
DTYPE = torch.float64


def fit_reward(differences, labels, steps=160):
    x = torch.tensor(differences, dtype=DTYPE)
    y = torch.tensor(labels, dtype=DTYPE)
    model = torch.nn.Linear(3, 1, bias=False, dtype=DTYPE)
    with torch.no_grad():
        model.weight.zero_()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.3)

    def objective():
        return (
            torch.nn.functional.binary_cross_entropy_with_logits(model(x).squeeze(-1), y)
            + 0.01 * model.weight.square().sum()
        )

    initial = float(objective().detach())
    for _ in range(steps):
        optimizer.zero_grad()
        loss = objective()
        loss.backward()
        optimizer.step()
    final = float(objective().detach())
    return model, initial, final


# === EXAMPLE A ===
def worked_a():
    x = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, -1]]
    y = [1, 1, 0.5, 0.5]
    model, initial, final = fit_reward(x, y)
    probe = torch.tensor([[1.0, 1.0, -3.0]], dtype=DTYPE)
    assert final < initial and final < 0.5
    assert abs(float(model.weight[0, 2].detach())) < 1e-12
    assert float(model(probe).detach()) > 2
    print("Balanced fit loss:", initial, final, "held-out margin:", float(model(probe).detach()))


# === EXAMPLE B ===
def worked_b():
    model, initial, final = fit_reward([[1, 0, 3], [0, 1, 3]], [1, 1])
    probe = torch.tensor([[1.0, 1.0, -3.0]], dtype=DTYPE)
    assert final < initial and float(model(probe).detach()) < 0
    assert float(model.weight[0, 2].detach()) > float(model.weight[0, 0].detach())
    print("Shortcut fit loss:", initial, final, "held-out margin:", float(model(probe).detach()))


# === EXERCISES ===
def exercise_checks():
    x = torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=DTYPE)
    y = torch.ones(2, dtype=DTYPE)
    weights = torch.zeros(3, dtype=DTYPE, requires_grad=True)
    loss = torch.nn.functional.binary_cross_entropy_with_logits(x @ weights, y)
    loss.backward()
    torch.testing.assert_close(weights.grad, x.T @ (torch.full_like(y, 0.5) - y) / len(y))
    model, initial, final = fit_reward(
        [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, -1]], [1, 1, 0.5, 0.5]
    )
    assert final < initial
    forward = model(torch.tensor([[1.0, 1.0, -3.0]], dtype=DTYPE)).detach()
    reverse = model(torch.tensor([[-1.0, -1.0, 3.0]], dtype=DTYPE)).detach()
    torch.testing.assert_close(forward, -reverse)
    assert all(parameter.device.type == "cpu" for parameter in model.parameters())


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-018: all reference checks passed")


if __name__ == "__main__":
    main()
