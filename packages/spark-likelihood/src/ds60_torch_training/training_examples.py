# SPDX-License-Identifier: Apache-2.0
"""Ordinary bounded CPU Torch examples for executor training.

Factories import Torch only when invoked on an executor. These recipes describe
finite training runs, not convergence, a fitted likelihood or a posterior.
"""

from __future__ import annotations

from .program import TrainingProgram


def linear_binary_model(config: dict):
    import torch

    if config != {"input_features": 1, "initial_weight": 0.0, "initial_bias": 0.0}:
        raise ValueError("Linear oracle requires its explicit one-feature zero initialization")
    model = torch.nn.Linear(1, 1, dtype=torch.float64)
    with torch.no_grad():
        model.weight.fill_(config["initial_weight"])
        model.bias.fill_(config["initial_bias"])
    return model


def mlp_dropout_binary_model(config: dict):
    import torch

    if config != {"input_features": 2, "hidden_features": 16, "dropout_p": 0.2}:
        raise ValueError("MLP recipe requires its explicit bounded two-feature configuration")
    return torch.nn.Sequential(
        torch.nn.Linear(2, 16, dtype=torch.float64),
        torch.nn.ReLU(),
        torch.nn.Dropout(p=config["dropout_p"]),
        torch.nn.Linear(16, 8, dtype=torch.float64),
        torch.nn.Tanh(),
        torch.nn.Linear(8, 1, dtype=torch.float64),
    )


def binary_logits_loss(config: dict):
    import torch

    if config != {"reduction": "none"}:
        raise ValueError("Binary recipe needs one loss contribution per observation")
    return torch.nn.BCEWithLogitsLoss(reduction="none")


def sgd_optimizer(parameters, config: dict):
    import torch

    if config != {"lr": 0.1, "momentum": 0.0, "weight_decay": 0.0}:
        raise ValueError("Oracle SGD options changed")
    return torch.optim.SGD(parameters, **config)


def adam_optimizer(parameters, config: dict):
    import torch

    if config != {"lr": 0.01, "weight_decay": 0.0}:
        raise ValueError("MLP Adam options changed")
    return torch.optim.Adam(parameters, **config)


def linear_sgd_oracle() -> TrainingProgram:
    return TrainingProgram(
        linear_binary_model,
        binary_logits_loss,
        sgd_optimizer,
        feature_names=("x",),
        configuration={
            "model": {"input_features": 1, "initial_weight": 0.0, "initial_bias": 0.0},
            "loss": {"reduction": "none"},
            "optimizer": {"lr": 0.1, "momentum": 0.0, "weight_decay": 0.0},
        },
        precision="float64",
        target_domain="binary",
    )


def mlp_adam_example() -> TrainingProgram:
    return TrainingProgram(
        mlp_dropout_binary_model,
        binary_logits_loss,
        adam_optimizer,
        feature_names=("x0", "x1"),
        configuration={
            "model": {"input_features": 2, "hidden_features": 16, "dropout_p": 0.2},
            "loss": {"reduction": "none"},
            "optimizer": {"lr": 0.01, "weight_decay": 0.0},
        },
        precision="float64",
        target_domain="binary",
    )
