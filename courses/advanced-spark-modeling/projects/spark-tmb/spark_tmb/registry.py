"""Trusted typed model schemas and bounded numeric payload construction."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

from ds60_spark_likelihood.contracts import ObjectiveError, finite_number

IDENTIFIER = re.compile(r"[a-z][a-z0-9_]{0,47}\Z")
MAX_ROWS = 4096
MAX_PARAMETERS = 64
MAX_GROUPS = 256
R_INTEGER_MIN = -2147483647
R_INTEGER_MAX = 2147483647
VECTOR_KINDS = {"real_vector", "integer_vector"}


class ModelContractError(ValueError):
    """The prepared model or payload violates its declared contract."""


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identifier(value):
    return isinstance(value, str) and IDENTIFIER.fullmatch(value) is not None


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelContractError("Payload numbers must be finite native scalars")
    try:
        return finite_number(value, "prepared-model numeric payload")
    except ObjectiveError as exc:
        raise ModelContractError(str(exc)) from exc


def integer32(value):
    """Preserve integer identity before coercion; R reserves INT_MIN for NA."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelContractError("Integer payloads require non-boolean numeric scalars")
    if value < R_INTEGER_MIN or value > R_INTEGER_MAX:
        raise ModelContractError("Integer payload lies outside R's non-NA signed32 range")
    if isinstance(value, float) and (not math.isfinite(value) or not value.is_integer()):
        raise ModelContractError("Integer payload must be finite and integral")
    return int(value)


def numeric_value(value, kind, *, allow_empty=False):
    convert = integer32 if kind.startswith("integer") else finite
    if kind.endswith("_scalar"):
        return convert(value)
    if kind not in VECTOR_KINDS or not isinstance(value, (list, tuple)):
        raise ModelContractError("Expected a declared numeric vector")
    minimum = 0 if allow_empty else 1
    if not minimum <= len(value) <= MAX_ROWS:
        raise ModelContractError("Observation vectors must respect the bounded row count")
    return [convert(item) for item in value]


def _fields(fields, *, empty=False):
    if not isinstance(fields, dict) or not (0 if empty else 1) <= len(fields) <= 32:
        raise ModelContractError("Declare a bounded numeric data schema")
    if any(not identifier(name) or kind not in VECTOR_KINDS for name, kind in fields.items()):
        raise ModelContractError("Only declared numeric observation vectors are supported")


def _constants(constants):
    if not isinstance(constants, dict) or len(constants) > 32:
        raise ModelContractError("Trusted constants must be a bounded typed mapping")
    for name, entry in constants.items():
        if (
            not identifier(name)
            or not isinstance(entry, dict)
            or set(entry) != {"kind", "value"}
            or entry["kind"] not in VECTOR_KINDS | {"real_scalar", "integer_scalar"}
        ):
            raise ModelContractError("Each trusted constant needs an explicit numeric kind/value")
        numeric_value(entry["value"], entry["kind"], allow_empty=True)


def _layout(spec):
    names = spec["fixed_parameters"]
    if (
        not isinstance(names, list)
        or not 1 <= len(names) <= MAX_PARAMETERS
        or not all(identifier(name) for name in names)
        or len(set(names)) != len(names)
    ):
        raise ModelContractError("Declare distinct canonical fixed parameter coordinates")
    layout = spec.get("parameter_layout")
    if layout is None:
        layout = [
            {"name": name, "kind": "scalar", "size": 1, "coordinates": [name]} for name in names
        ]
    if not isinstance(layout, list) or not 1 <= len(layout) <= MAX_PARAMETERS:
        raise ModelContractError("Declare bounded fixed scalar/vector parameter blocks")
    flattened, native = [], []
    for block in layout:
        if (
            not isinstance(block, dict)
            or set(block) != {"name", "kind", "size", "coordinates"}
            or not identifier(block["name"])
            or block["kind"] not in {"scalar", "real_vector"}
            or type(block["size"]) is not int
            or not 1 <= block["size"] <= MAX_PARAMETERS
            or (block["kind"] == "scalar" and block["size"] != 1)
            or not isinstance(block["coordinates"], list)
            or len(block["coordinates"]) != block["size"]
        ):
            raise ModelContractError("Invalid fixed parameter block")
        flattened.extend(block["coordinates"])
        native.extend([block["name"]] * block["size"])
    if flattened != names or len({block["name"] for block in layout}) != len(layout):
        raise ModelContractError("Parameter blocks must match the exact canonical flat order")
    spec["parameter_layout"] = layout
    spec["native_parameter_names"] = native


def load_registry(root):
    root = Path(root).resolve(strict=True)
    config = json.loads((root / "registry.json").read_text())
    if (
        type(config.get("schema_version")) is not int
        or config["schema_version"] not in {1, 2}
        or not isinstance(config.get("models"), dict)
        or not 1 <= len(config["models"]) <= 32
    ):
        raise ModelContractError("Unsupported or unbounded prepared model registry")
    abi = config.get("abi")
    if (
        not isinstance(abi, dict)
        or set(abi) != {"R", "TMB", "Matrix"}
        or not all(isinstance(value, str) and 1 <= len(value) <= 64 for value in abi.values())
    ):
        raise ModelContractError("Declare bounded R, TMB and Matrix ABI versions")
    required = {"source", "factorization", "response", "data", "fixed_parameters", "random"}
    optional = {"parameter_layout", "training_constants", "prediction"}
    for model, spec in config["models"].items():
        if (
            not isinstance(spec, dict)
            or not required <= set(spec)
            or set(spec) - required - optional
        ):
            raise ModelContractError("Model declarations differ from the supported registry schema")
        if not identifier(model) or spec["source"] != f"models/{model}.cpp":
            raise ModelContractError("Use a fixed model ID and its owned C++ template")
        path = root / spec["source"]
        if path.is_symlink() or path.resolve().parent != root / "models" or not path.is_file():
            raise ModelContractError("Model source must be an ordinary owned template")
        if spec["factorization"] not in {"independent_rows", "complete_groups"}:
            raise ModelContractError("Only additive independent-row or complete-group models apply")
        _fields(spec["data"])
        if spec["response"] not in spec["data"]:
            raise ModelContractError("Response must be a declared observation vector")
        _layout(spec)
        random = spec["random"]
        block_names = {block["name"] for block in spec["parameter_layout"]}
        if random is not None and (
            not isinstance(random, dict)
            or set(random) != {"name", "group_field"}
            or spec["factorization"] != "complete_groups"
            or not identifier(random["name"])
            or random["name"] in block_names
            or spec["data"].get(random["group_field"]) != "integer_vector"
        ):
            raise ModelContractError(
                "Random vectors need complete groups and an integer group field"
            )
        constants = spec.setdefault("training_constants", {})
        _constants(constants)
        if set(constants) & set(spec["data"]):
            raise ModelContractError("Trusted constants cannot overwrite observation fields")
        prediction = spec.setdefault("prediction", None)
        if prediction is None:
            continue
        if (
            random is not None
            or not isinstance(prediction, dict)
            or set(prediction)
            != {"target", "inputs", "from_training", "report", "constants", "row_count_field"}
            or not identifier(prediction["target"])
            or not identifier(prediction["report"])
        ):
            raise ModelContractError("Declare an explicit fixed-effect prediction/report contract")
        _fields(prediction["inputs"], empty=True)
        _constants(prediction["constants"])
        mapping = prediction["from_training"]
        if (
            not isinstance(mapping, dict)
            or set(mapping) != set(prediction["inputs"])
            or any(
                field == spec["response"]
                or field not in spec["data"]
                or prediction["inputs"][key] != spec["data"][field]
                for key, field in mapping.items()
            )
            or spec["response"] in prediction["inputs"]
        ):
            raise ModelContractError("Prediction inputs must map to response-free training fields")
        count_field = prediction["row_count_field"]
        if count_field is not None and not identifier(count_field):
            raise ModelContractError("Prediction row count must use a declared scalar field")
        input_keys, constant_keys = set(prediction["inputs"]), set(prediction["constants"])
        if input_keys & constant_keys or count_field in input_keys | constant_keys:
            raise ModelContractError("Prediction data sources must not overlap")
        if not input_keys and count_field is None:
            raise ModelContractError("Predictor-free models need an explicit requested row count")
        constructed = input_keys | constant_keys | ({count_field} if count_field else set())
        if constructed != set(spec["data"]) | set(constants):
            raise ModelContractError(
                "Training and prediction must construct the same C++ data interface"
            )
        training_types = {
            **spec["data"],
            **{name: entry["kind"] for name, entry in constants.items()},
        }
        prediction_types = {
            **prediction["inputs"],
            **{name: entry["kind"] for name, entry in prediction["constants"].items()},
        }
        if count_field:
            prediction_types[count_field] = "integer_scalar"
        if training_types != prediction_types:
            raise ModelContractError("Prediction must preserve every native data field type")
        response_constant = prediction["constants"].get(spec["response"])
        if response_constant is None or response_constant["value"] != []:
            raise ModelContractError("Prediction cannot fabricate response observations")
    return config


def parameter_values(spec, theta):
    if not isinstance(theta, (list, tuple)) or len(theta) != len(spec["fixed_parameters"]):
        raise ModelContractError("Fixed parameter layout mismatch")
    values = list(map(finite, theta))
    parameters, cursor = {}, 0
    for block in spec["parameter_layout"]:
        part = values[cursor : cursor + block["size"]]
        parameters[block["name"]] = part[0] if block["kind"] == "scalar" else part
        cursor += block["size"]
    return values, parameters


def _data(fields, values, *, expected_rows=None):
    if not isinstance(values, dict) or set(values) != set(fields):
        raise ModelContractError("Payload data keys must exactly match the prepared schema")
    cleaned = {name: numeric_value(values[name], kind) for name, kind in fields.items()}
    counts = {len(value) for value in cleaned.values()}
    if expected_rows is not None:
        counts.add(expected_rows)
    if len(counts) != 1:
        raise ModelContractError("Observation vectors must have equal lengths")
    return cleaned


def _add_constants(data, definitions):
    for name, entry in definitions.items():
        data[name] = numeric_value(entry["value"], entry["kind"], allow_empty=True)


def _spec(root, model_id):
    registry = load_registry(root)
    if model_id not in registry["models"]:
        raise ModelContractError("Model ID is not prepared in the installed registry")
    return registry["models"][model_id]


def payload_for(root, model_id, data, theta):
    spec = _spec(root, model_id)
    values, parameters = parameter_values(spec, theta)
    cleaned = _data(spec["data"], data)
    random = spec["random"]
    if random is not None:
        groups = sorted(set(cleaned[random["group_field"]]))
        if len(groups) > MAX_GROUPS or groups != list(range(len(groups))):
            raise ModelContractError("Group indices must be contiguous zero-based complete groups")
        parameters[random["name"]] = [0.0] * len(groups)
    _add_constants(cleaned, spec["training_constants"])
    return {
        "schema_version": 1,
        "model_id": model_id,
        "data": cleaned,
        "parameters": parameters,
        "theta": values,
        "random": None if random is None else random["name"],
    }


def prediction_payload(root, model_id, data, theta, *, n_rows, target=None):
    spec = _spec(root, model_id)
    prediction = spec["prediction"]
    if prediction is None:
        raise ModelContractError("This prepared model does not declare prediction semantics")
    if type(n_rows) is not int or not 1 <= n_rows <= MAX_ROWS:
        raise ModelContractError("Prediction row count must be an integer within 1..4096")
    if target is not None and target != prediction["target"]:
        raise ModelContractError("Requested prediction target differs from the registered report")
    values, parameters = parameter_values(spec, theta)
    cleaned = _data(prediction["inputs"], data, expected_rows=n_rows)
    _add_constants(cleaned, prediction["constants"])
    if prediction["row_count_field"]:
        cleaned[prediction["row_count_field"]] = integer32(n_rows)
    return {
        "schema_version": 1,
        "model_id": model_id,
        "data": cleaned,
        "parameters": parameters,
        "theta": values,
        "random": None,
        "n_rows": n_rows,
        "target": prediction["target"],
    }
