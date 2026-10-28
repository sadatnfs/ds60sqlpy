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


def worked_a():
    x = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, -1]]
    y = [1, 1, 0.5, 0.5]
    model, initial, final = fit_reward(x, y)
    probe = torch.tensor([[1.0, 1.0, -3.0]], dtype=DTYPE)
    assert final < initial and final < 0.5
    assert abs(float(model.weight[0, 2].detach())) < 1e-12
    assert float(model(probe).detach()) > 2
    print("Balanced fit loss:", initial, final, "held-out margin:", float(model(probe).detach()))


worked_a()

# Task 1: Compare autograd at zero weights with \(D^{\mathsf T}(0.5-y)/n\).
# Task 2: Train the balanced design in case A.
# Task 3: Negate the held-out feature difference.
# Task 4: Inspect the weights from case B.
# Task 5: Evaluate the objective after the final optimizer step.
# Task 6: Describe what the three learned weights establish.

# Implement your six changes below.
