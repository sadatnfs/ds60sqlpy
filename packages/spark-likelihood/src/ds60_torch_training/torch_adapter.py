# SPDX-License-Identifier: Apache-2.0
"""Narrow optional CPU Torch adapter for data-only checkpoints.

The module imports no Torch/NumPy at import time. Runtime qualification remains
separate. Artifact data never names code to import and no pickle loader exists.
"""

from __future__ import annotations

import random
import sys
from typing import Any

from . import checkpoint as cp

_BASE_ATTRIBUTES = {
    "training",
    "_parameters",
    "_buffers",
    "_non_persistent_buffers_set",
    "_backward_pre_hooks",
    "_backward_hooks",
    "_is_full_backward_hook",
    "_forward_hooks",
    "_forward_hooks_with_kwargs",
    "_forward_hooks_always_called",
    "_forward_pre_hooks",
    "_forward_pre_hooks_with_kwargs",
    "_state_dict_hooks",
    "_state_dict_pre_hooks",
    "_load_state_dict_pre_hooks",
    "_load_state_dict_post_hooks",
    "_modules",
    "_compiled_call_impl",
}
_STATE_METHODS = {
    "state_dict",
    "load_state_dict",
    "_save_to_state_dict",
    "_load_from_state_dict",
    "get_extra_state",
    "set_extra_state",
}


def _torch() -> Any:
    import torch

    cp.require(sys.byteorder == "little", "Only little-endian CPU tensor storage is qualified")
    return torch


def _modules(model: Any) -> list[tuple[str, Any, dict[str, Any]]]:
    torch = _torch()
    cp.require(isinstance(model, torch.nn.Module), "A trusted ordinary nn.Module is required")
    allowed: dict[type, set[str]] = {
        torch.nn.Sequential: set(),
        torch.nn.ModuleList: set(),
        torch.nn.ModuleDict: set(),
        torch.nn.Linear: {"in_features", "out_features"},
        torch.nn.ReLU: {"inplace"},
        torch.nn.LeakyReLU: {"inplace", "negative_slope"},
        torch.nn.Tanh: set(),
        torch.nn.Sigmoid: set(),
        torch.nn.Identity: set(),
        torch.nn.Dropout: {"p", "inplace"},
        torch.nn.Flatten: {"start_dim", "end_dim"},
    }
    result = []
    visited = set()

    def walk(module: Any, name: str) -> None:
        cp.require(id(module) not in visited, "Shared/cyclic module graphs are unsupported")
        visited.add(id(module))
        cp.require(len(visited) <= cp.MAX_TENSORS, "Module graph exceeds bound")
        cp.require(isinstance(module, torch.nn.Module), "Unexpected registered module object")
        for method in _STATE_METHODS:
            cp.require(
                getattr(type(module), method) is getattr(torch.nn.Module, method),
                "Custom module state methods are unsupported",
            )
        cp.require(
            getattr(module, "_compiled_call_impl", None) is None,
            "Compiled modules are unsupported",
        )
        for key, value in module.__dict__.items():
            if "hooks" in key:
                cp.require(
                    not value,
                    "Registered module hooks are unsupported checkpoint state",
                )
        # Custom wrappers with only registered state are allowed. Extra instance
        # values require an explicitly supported state schema instead of omission.
        expected = allowed.get(type(module), set())
        extras = set(module.__dict__) - _BASE_ATTRIBUTES
        cp.require(
            extras <= expected,
            "Unsupported module attributes: " + ",".join(sorted(extras - expected)),
        )
        attributes = {key: module.__dict__[key] for key in sorted(extras)}
        cp.require(
            all(
                value is None or type(value) in {bool, int, float, str}
                for value in attributes.values()
            ),
            "Module attributes must be immutable scalar configuration",
        )
        cp.json_bytes(attributes)
        cp.require(type(module.training) is bool, "Module training mode must be boolean")
        result.append((name, module, attributes))
        for child_name, child in module._modules.items():
            cp.require(
                cp.valid_name(child_name) and "." not in child_name,
                "Invalid registered module name",
            )
            if child is not None:
                walk(child, name + "." + child_name if name else child_name)

    walk(model, "")
    return result


def _tensor_dtype(tensor: Any) -> str:
    torch = _torch()
    cp.require(
        type(tensor) in {torch.Tensor, torch.nn.Parameter},
        "Tensor subclasses are unsupported",
    )
    cp.require(
        tensor.device.type == "cpu" and tensor.layout == torch.strided and not tensor.is_quantized,
        "Only eager dense CPU tensor state is supported",
    )
    cp.require(
        tensor.is_contiguous() and tensor.storage_offset() == 0,
        "Tensor views/noncontiguous state are unsupported",
    )
    cp.require(
        tensor.untyped_storage().nbytes() == tensor.numel() * tensor.element_size(),
        "Partial/shared tensor storage is unsupported",
    )
    dtype = str(tensor.dtype).removeprefix("torch.")
    cp.require(dtype in cp.DTYPES, "Unsupported tensor dtype")
    return dtype


def _state_tensors(model: Any) -> list[tuple[str, str, Any]]:
    rows = []
    used = set()
    for prefix, module, _ in _modules(model):
        for role, collection in (
            ("parameter", module._parameters),
            ("buffer", module._buffers),
        ):
            for key, tensor in collection.items():
                cp.require(
                    cp.valid_name(key) and "." not in key,
                    "Invalid registered tensor name",
                )
                if tensor is None:
                    continue
                _tensor_dtype(tensor)
                if tensor.numel():
                    pointer = tensor.untyped_storage().data_ptr()
                    cp.require(
                        pointer not in used,
                        "Aliased model tensor storage is unsupported",
                    )
                    used.add(pointer)
                rows.append((prefix + "." + key if prefix else key, role, tensor))
    cp.require(len(rows) <= cp.MAX_TENSORS, "Model tensor count exceeds bound")
    return rows


def model_layout(model: Any) -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "role": role,
            "dtype": _tensor_dtype(tensor),
            "shape": list(tensor.shape),
            "requires_grad": bool(tensor.requires_grad),
        }
        for name, role, tensor in _state_tensors(model)
    ]


def module_schema_digest(model: Any) -> str:
    graph = []
    for name, module, attributes in _modules(model):
        graph.append(
            {
                "name": name,
                "class": type(module).__module__ + "." + type(module).__qualname__,
                "attributes": attributes,
                "parameters": list(module._parameters),
                "none_parameters": [
                    key for key, value in module._parameters.items() if value is None
                ],
                "buffers": list(module._buffers),
                "none_buffers": [key for key, value in module._buffers.items() if value is None],
                "nonpersistent_buffers": sorted(module._non_persistent_buffers_set),
                "children": list(module._modules),
                "none_children": [key for key, value in module._modules.items() if value is None],
            }
        )
    return cp.digest_value(
        {
            "kind": "eager_dense_cpu_module_schema_v1",
            "graph": graph,
            "layout": model_layout(model),
        }
    )


def optimizer_layout(model: Any, optimizer: Any) -> dict[str, Any]:
    torch = _torch()
    classes = {
        torch.optim.SGD: "torch.optim.SGD",
        torch.optim.Adam: "torch.optim.Adam",
        torch.optim.AdamW: "torch.optim.AdamW",
    }
    cp.require(
        type(optimizer) in classes,
        "Only exact qualified optimizer classes are supported",
    )
    optimizer_attributes = {
        "defaults",
        "state",
        "param_groups",
        "_zero_grad_profile_name",
        "_warned_capturable_if_run_uncaptured",
        "_optimizer_step_pre_hooks",
        "_optimizer_step_post_hooks",
        "_optimizer_state_dict_pre_hooks",
        "_optimizer_state_dict_post_hooks",
        "_optimizer_load_state_dict_pre_hooks",
        "_optimizer_load_state_dict_post_hooks",
    }
    cp.require(
        set(optimizer.__dict__) <= optimizer_attributes,
        "Unsupported optimizer instance state",
    )
    for key, value in optimizer.__dict__.items():
        if "hooks" in key:
            cp.require(not value, "Optimizer state/step hooks are unsupported")
    names = {
        id(tensor): name for name, role, tensor in _state_tensors(model) if role == "parameter"
    }
    groups = []
    for group in optimizer.param_groups:
        cp.require(
            type(group) is dict and type(group.get("params")) is list,
            "Unsupported optimizer group",
        )
        cp.require(
            all(id(value) in names for value in group["params"]),
            "Optimizer uses an unknown parameter",
        )
        ordered = [names[id(value)] for value in group["params"]]
        if "param_names" in group:
            cp.require(
                list(group["param_names"]) == ordered,
                "Optimizer param_names differ from actual named parameters",
            )
        options = {
            key: list(value) if key == "betas" and type(value) is tuple else value
            for key, value in group.items()
            if key not in {"params", "param_names"}
        }
        cp.validate_optimizer_options(classes[type(optimizer)], options)
        groups.append({"names": ordered, "options": options})
    return {"class": classes[type(optimizer)], "groups": groups}


def tensor_data(tensor: Any) -> cp.TensorData:
    dtype = _tensor_dtype(tensor)
    cp.require(
        tensor.numel() * tensor.element_size() <= cp.MAX_TENSOR,
        "Tensor exceeds payload bound",
    )
    raw = tensor.detach().numpy().tobytes(order="C")
    return cp.checked_tensor(cp.TensorData(dtype, tuple(tensor.shape), raw))


def loss_state_digest(loss: Any) -> str:
    torch = _torch()
    allowed = {
        torch.nn.MSELoss: {"reduction"},
        torch.nn.L1Loss: {"reduction"},
        torch.nn.BCEWithLogitsLoss: {"reduction"},
        torch.nn.CrossEntropyLoss: {"reduction", "ignore_index", "label_smoothing"},
        torch.nn.NLLLoss: {"reduction", "ignore_index"},
        torch.nn.SmoothL1Loss: {"reduction", "beta"},
        torch.nn.HuberLoss: {"reduction", "delta"},
    }
    cp.require(
        type(loss) in allowed,
        "Loss needs an explicitly supported immutable state schema",
    )
    for key, value in loss.__dict__.items():
        if "hooks" in key:
            cp.require(not value, "Loss hooks are unsupported")
    cp.require(
        not loss._parameters and not loss._modules,
        "Parameterized/nested mutable loss state is unsupported",
    )
    extras = set(loss.__dict__) - _BASE_ATTRIBUTES
    cp.require(extras <= allowed[type(loss)], "Unknown loss instance state")
    values = {key: loss.__dict__[key] for key in sorted(extras)}
    cp.require(
        all(type(v) in {str, bool, int, float} or v is None for v in values.values()),
        "Unsupported loss configuration value",
    )
    buffers: dict[str, Any] = {}
    for name, value in loss._buffers.items():
        if value is None:
            buffers[name] = None
        else:
            tensor = tensor_data(value)
            buffers[name] = {
                "dtype": tensor.dtype,
                "shape": list(tensor.shape),
                "sha256": cp.sha(tensor.data),
            }
    return cp.digest_value(
        {
            "kind": "immutable_loss_state_v1",
            "class": type(loss).__module__ + "." + type(loss).__qualname__,
            "configuration": values,
            "buffers": buffers,
        }
    )


def _admit_live(
    model: Any,
    optimizer: Any,
    loss: Any,
    binding: dict[str, Any],
    expected_module_schema_digest: str,
) -> None:
    cp.validate_binding(binding)
    cp.require(
        module_schema_digest(model) == expected_module_schema_digest,
        "Live module schema/configuration changed",
    )
    cp.require(
        model_layout(model) == binding["model_layout"],
        "Live model parameter/buffer layout differs",
    )
    cp.require(
        cp.json_bytes(optimizer_layout(model, optimizer))
        == cp.json_bytes(binding["optimizer_layout"]),
        "Live optimizer parameter names/order/options differ",
    )
    cp.require(
        loss_state_digest(loss) == binding["loss_state_digest"],
        "Loss state changed or differs from definition",
    )
    named = _state_tensors(model)
    tensors = [tensor for _, _, tensor in named]
    for _, role, tensor in named:
        if role == "parameter":
            cp.require(
                tensor.grad is None,
                "Checkpoint boundaries require cleared gradients; accumulation is unsupported",
            )
    for fields in optimizer.state.values():
        cp.require(type(fields) is dict, "Unsupported optimizer parameter state")
        tensors.extend(fields.values())
    pointers = set()
    for tensor in tensors:
        _tensor_dtype(tensor)
        if tensor.numel():
            pointer = tensor.untyped_storage().data_ptr()
            cp.require(
                pointer not in pointers,
                "Aliased model/optimizer state storage is unsupported",
            )
            pointers.add(pointer)


def capture_rank_state(
    model: Any,
    optimizer: Any,
    loss: Any,
    *,
    expected_binding: dict[str, Any],
    expected_module_schema_digest: str,
    progress: dict[str, Any],
    sampler: dict[str, Any],
    generators: dict[str, Any] | None = None,
) -> dict[str, Any]:
    import numpy as np

    torch = _torch()
    _admit_live(model, optimizer, loss, expected_binding, expected_module_schema_digest)
    generators = {} if generators is None else generators
    cp.require(type(generators) is dict, "Named RNG streams must be explicit")
    named = _state_tensors(model)
    parameters = {name: value for name, role, value in named if role == "parameter"}
    by_id = {id(value): name for name, value in parameters.items()}
    cp.require(
        all(id(value) in by_id for value in optimizer.state),
        "Optimizer holds state for an unknown parameter",
    )
    ordered = [
        name for group in expected_binding["optimizer_layout"]["groups"] for name in group["names"]
    ]
    optimizer_state = {}
    for name in ordered:
        parameter = parameters[name]
        if parameter in optimizer.state:
            values = optimizer.state[parameter]
            cp.require(type(values) is dict, "Optimizer parameter state is unsupported")
            optimizer_state[name] = {key: tensor_data(value) for key, value in values.items()}
    numpy_state: Any = np.random.get_state(legacy=True)
    cp.require(
        numpy_state[0] == "MT19937",
        "Only explicit global NumPy MT19937 state is qualified",
    )
    numpy_words = cp.TensorData(
        "uint32",
        tuple(numpy_state[1].shape),
        numpy_state[1].astype("<u4", copy=False).tobytes(),
    )
    streams = {}
    for name, generator in generators.items():
        cp.require(
            type(generator) is torch.Generator and generator.device.type == "cpu",
            "Only explicit CPU Torch generators are supported",
        )
        streams[name] = tensor_data(generator.get_state())
    state = {
        "model": {name: tensor_data(value) for name, _, value in named},
        "optimizer": optimizer_state,
        "module_modes": {name: bool(module.training) for name, module, _ in _modules(model)},
        "loss_state_digest": loss_state_digest(loss),
        "rng": {
            "python": random.getstate(),
            "numpy": (
                "MT19937",
                numpy_words,
                int(numpy_state[2]),
                int(numpy_state[3]),
                float(numpy_state[4]),
            ),
            "torch_cpu": tensor_data(torch.get_rng_state()),
            "generators": streams,
        },
        "sampler": sampler,
    }
    cp.validate_state(state, expected_binding, cp.validate_progress(progress))
    return state


def _from_data(value: cp.TensorData) -> Any:
    torch = _torch()
    cp.checked_tensor(value)
    dtype = getattr(torch, value.dtype)
    if not value.data:
        return torch.empty(value.shape, dtype=dtype, device="cpu")
    return torch.frombuffer(bytearray(value.data), dtype=dtype).clone().reshape(value.shape)


def restore_rank_state(
    model: Any,
    optimizer: Any,
    loss: Any,
    loaded: cp.LoadedRank,
    *,
    expected_binding: dict[str, Any],
    expected_module_schema_digest: str,
    generators: dict[str, Any] | None = None,
) -> None:
    """Validate completely, restore live data, then restore RNG immediately last.

    A failure is fatal to this attempt. The caller must discard partially restored
    live objects; this function never converts a failure into training success.
    """
    import numpy as np

    torch = _torch()
    cp.require(
        type(loaded) is cp.LoadedRank
        and cp.json_bytes(loaded.binding) == cp.json_bytes(expected_binding),
        "Loaded rank binding differs",
    )
    _admit_live(model, optimizer, loss, expected_binding, expected_module_schema_digest)
    state = loaded.state
    cp.validate_state(state, expected_binding, loaded.progress)
    generators = {} if generators is None else generators
    cp.require(
        type(generators) is dict and list(generators) == list(state["rng"]["generators"]),
        "Named RNG streams differ on resume",
    )
    modules = {name: module for name, module, _ in _modules(model)}
    cp.require(list(modules) == list(state["module_modes"]), "Module graph differs on resume")
    tensors = {name: value for name, _, value in _state_tensors(model)}
    prepared_model = {name: _from_data(value) for name, value in state["model"].items()}
    prepared_optimizer = {
        name: {key: _from_data(value) for key, value in fields.items()}
        for name, fields in state["optimizer"].items()
    }
    cpu_rng = _from_data(state["rng"]["torch_cpu"])
    cp.require(
        tuple(cpu_rng.shape) == tuple(torch.get_rng_state().shape),
        "Torch CPU RNG schema differs",
    )
    torch.Generator(device="cpu").set_state(cpu_rng)
    named_rng = {}
    for name, generator in generators.items():
        cp.require(
            type(generator) is torch.Generator and generator.device.type == "cpu",
            "Expected a trusted CPU generator",
        )
        value = _from_data(state["rng"]["generators"][name])
        cp.require(
            tuple(value.shape) == tuple(generator.get_state().shape),
            "Named generator RNG schema differs",
        )
        torch.Generator(device="cpu").set_state(value)
        named_rng[name] = value
    python_rng = state["rng"]["python"]
    random.Random(0).setstate(python_rng)
    np_state = state["rng"]["numpy"]
    numpy_rng = (
        np_state[0],
        np.frombuffer(np_state[1].data, dtype="<u4").copy(),
        np_state[2],
        np_state[3],
        np_state[4],
    )
    np.random.RandomState(0).set_state(numpy_rng)
    # Only trusted provided objects are mutated. No class is imported from data.
    with torch.no_grad():
        for name, value in prepared_model.items():
            tensors[name].copy_(value)
    optimizer.state.clear()
    for name, values in prepared_optimizer.items():
        optimizer.state[tensors[name]] = values
    for name, mode in state["module_modes"].items():
        modules[name].training = mode
    # Model/optimizer construction, validation and allocations precede this point.
    random.setstate(python_rng)
    np.random.set_state(numpy_rng)
    torch.set_rng_state(cpu_rng)
    for name, value in named_rng.items():
        generators[name].set_state(value)
