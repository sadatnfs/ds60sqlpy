"""Pure adapter admission checks with test doubles, not Torch runtime qualification."""

from __future__ import annotations

import importlib.util
import math
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2] / "src/ds60_torch_training"
PACKAGE = "checkpoint_adapter_fixture"
pkg = types.ModuleType(PACKAGE)
pkg.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = pkg
for name in ("checkpoint", "torch_adapter"):
    spec = importlib.util.spec_from_file_location(PACKAGE + "." + name, ROOT / (name + ".py"))
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
adapter = sys.modules[PACKAGE + ".torch_adapter"]
cp = sys.modules[PACKAGE + ".checkpoint"]


class Module:
    def __init__(self):
        self.training = True
        self._parameters = {}
        self._buffers = {}
        self._modules = {}
        self._non_persistent_buffers_set = set()

    def state_dict(self):
        raise AssertionError("State hooks must not be executed")

    load_state_dict = state_dict
    _save_to_state_dict = state_dict
    _load_from_state_dict = state_dict
    get_extra_state = state_dict
    set_extra_state = state_dict


class Tensor:
    def __init__(self, shape=(2,), pointer=1, device="cpu", contiguous=True):
        self.shape = shape
        self.dtype = "torch.float64"
        self.device = types.SimpleNamespace(type=device)
        self.layout = "strided"
        self.is_quantized = False
        self.requires_grad = True
        self.pointer = pointer
        self.contiguous = contiguous
        self.grad = None

    def is_contiguous(self):
        return self.contiguous

    def storage_offset(self):
        return 0

    def numel(self):
        return math.prod(self.shape)

    def element_size(self):
        return 8

    def untyped_storage(self):
        return types.SimpleNamespace(nbytes=lambda: self.numel() * 8, data_ptr=lambda: self.pointer)


class Parameter(Tensor):
    pass


@pytest.fixture
def fake_torch(monkeypatch):
    names = [
        "Sequential",
        "ModuleList",
        "ModuleDict",
        "Linear",
        "ReLU",
        "LeakyReLU",
        "Tanh",
        "Sigmoid",
        "Identity",
        "Dropout",
        "Flatten",
    ]
    nn = types.SimpleNamespace(
        Module=Module,
        Parameter=Parameter,
        **{name: type(name, (Module,), {}) for name in names},
    )
    optim = types.SimpleNamespace(**{name: type(name, (), {}) for name in ("SGD", "Adam", "AdamW")})
    torch = types.SimpleNamespace(nn=nn, optim=optim, Tensor=Tensor, strided="strided")
    monkeypatch.setattr(adapter, "_torch", lambda: torch)
    return torch


def ordinary_model(torch):
    model = torch.nn.Linear()
    model.in_features = 2
    model.out_features = 1
    model._parameters = {"weight": Parameter(pointer=1), "bias": Parameter(pointer=2)}
    return model


def test_model_schema_binds_scalar_configuration_but_modes_are_separate(fake_torch):
    model = fake_torch.nn.Dropout()
    model.p = 0.2
    model.inplace = False
    before = adapter.module_schema_digest(model)
    model.training = False
    assert adapter.module_schema_digest(model) == before
    model.p = 0.3
    assert adapter.module_schema_digest(model) != before


def test_named_tensor_shape_and_requires_grad_are_bound(fake_torch):
    model = ordinary_model(fake_torch)
    before = adapter.module_schema_digest(model)
    assert [row["name"] for row in adapter.model_layout(model)] == ["weight", "bias"]
    model._parameters["bias"].requires_grad = False
    assert adapter.module_schema_digest(model) != before


def test_custom_state_method_refuses_without_executing_it(fake_torch):
    class Custom(Module):
        def get_extra_state(self):
            pytest.fail("Unsupported state hook executed")

    with pytest.raises(cp.CheckpointError, match="state methods"):
        adapter.module_schema_digest(Custom())


def test_custom_mutable_attribute_is_not_silently_omitted(fake_torch):
    model = ordinary_model(fake_torch)
    model.accumulator = []
    with pytest.raises(cp.CheckpointError, match="Unsupported module attributes"):
        adapter.module_schema_digest(model)


def test_hook_registration_and_shared_modules_are_rejected(fake_torch):
    model = ordinary_model(fake_torch)
    model._state_dict_hooks = {1: lambda: pytest.fail("Hook executed")}
    with pytest.raises(cp.CheckpointError, match="hooks"):
        adapter.module_schema_digest(model)
    outer = fake_torch.nn.Sequential()
    leaf = fake_torch.nn.ReLU()
    leaf.inplace = False
    outer._modules = {"first": leaf, "second": leaf}
    with pytest.raises(cp.CheckpointError, match="Shared/cyclic"):
        adapter.module_schema_digest(outer)


def test_storage_alias_views_and_non_cpu_tensors_are_rejected(fake_torch):
    model = ordinary_model(fake_torch)
    model._parameters["bias"].pointer = 1
    with pytest.raises(cp.CheckpointError, match="Aliased"):
        adapter.model_layout(model)
    model = ordinary_model(fake_torch)
    model._parameters["bias"].contiguous = False
    with pytest.raises(cp.CheckpointError, match="noncontiguous"):
        adapter.model_layout(model)
    model = ordinary_model(fake_torch)
    model._parameters["weight"].device.type = "cuda"
    with pytest.raises(cp.CheckpointError, match="CPU"):
        adapter.model_layout(model)


def test_optimizer_names_come_from_actual_parameter_objects(fake_torch):
    model = ordinary_model(fake_torch)
    optimizer = fake_torch.optim.SGD()
    options = {
        "lr": 0.1,
        "weight_decay": 0.0,
        "momentum": 0.0,
        "dampening": 0.0,
        "nesterov": False,
    }
    optimizer.param_groups = [
        {"params": [model._parameters["bias"], model._parameters["weight"]], **options}
    ]
    layout = adapter.optimizer_layout(model, optimizer)
    assert layout["groups"][0]["names"] == ["bias", "weight"]
    optimizer.param_groups[0]["param_names"] = ["weight", "bias"]
    with pytest.raises(cp.CheckpointError, match="param_names differ"):
        adapter.optimizer_layout(model, optimizer)


def test_unknown_optimizer_parameter_and_tensor_hyperparameter_refuse(fake_torch):
    model = ordinary_model(fake_torch)
    optimizer = fake_torch.optim.SGD()
    optimizer.param_groups = [{"params": [Parameter(pointer=99)], "lr": 0.1}]
    with pytest.raises(cp.CheckpointError, match="unknown parameter"):
        adapter.optimizer_layout(model, optimizer)
    optimizer.param_groups = [
        {
            "params": [model._parameters["weight"]],
            "lr": Tensor(),
            "weight_decay": 0.0,
            "momentum": 0.0,
            "dampening": 0.0,
            "nesterov": False,
        }
    ]
    with pytest.raises(cp.CheckpointError, match="finite"):
        adapter.optimizer_layout(model, optimizer)
