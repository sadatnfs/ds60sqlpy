"""Real CPU Torch checks for ordinary factory and weighted loss math.

Run in the bounded native Torch slot. These checks alone do not qualify Spark.
"""

from __future__ import annotations

import pytest
from ds60_torch_training.runner import _batch_loss, _construct
from ds60_torch_training.training_examples import linear_sgd_oracle, mlp_adam_example

torch = pytest.importorskip("torch")
if not str(torch.__version__).startswith("2.9.1+cpu"):
    pytest.skip("requires the prepared Torch 2.9.1+cpu runtime", allow_module_level=True)


def _rows(labels, weights):
    return [
        {"id": index, "features": [1.0], "label": float(label), "weight": float(weight)}
        for index, (label, weight) in enumerate(zip(labels, weights, strict=True))
    ]


@pytest.mark.parametrize(
    ("labels", "weights", "expected_update"),
    [
        ([0, 1, 1, 0, 1, 1], [1] * 6, 1 / 60),
        ([0, 1, 1, 0, 1, 0], [1, 3, 1, 0, 2, 1], 1 / 40),
    ],
)
def test_six_row_weighted_sgd_oracle(labels, weights, expected_update):
    program = linear_sgd_oracle()
    model, loss, optimizer, dtype = _construct(program, program.descriptor(), torch)
    rows = _rows(labels, weights)
    local_sum, mass = _batch_loss(model, loss, rows, "binary", dtype, torch)
    (local_sum / mass).backward()
    optimizer.step()
    assert model.weight.item() == pytest.approx(expected_update, abs=1e-14)
    assert model.bias.item() == pytest.approx(expected_update, abs=1e-14)


def test_mlp_adam_has_more_than_64_parameters_and_dropout():
    program = mlp_adam_example()
    model, loss, optimizer, _ = _construct(program, program.descriptor(), torch)
    assert sum(value.numel() for value in model.parameters()) > 64
    assert any(type(layer) is torch.nn.Dropout for layer in model.modules())
    assert type(optimizer) is torch.optim.Adam
    assert loss.reduction == "none"
