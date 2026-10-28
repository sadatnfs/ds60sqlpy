"""A bounded numerical artifact with separate integrity and schema validation."""

import hashlib
import json
import math
import os
import re
import stat
import tempfile
from pathlib import Path

import numpy as np

from ds60sqlpy.plot_artifacts import publish_report, publish_table

MAX_BYTES = 32768
INTERFACE = {
    "features": ["hours", "tickets"],
    "units": {"hours": "hours", "tickets": "count"},
    "scorer": "linear-float64-v1",
}


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate artifact field")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("Nonfinite artifact constant")


def decode(data):
    try:
        return json.loads(
            data.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=reject_constant
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ValueError("Invalid strict artifact JSON") from error


def bounded_read(path):
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or not 1 <= info.st_size <= MAX_BYTES:
                raise ValueError("Artifact must be a bounded regular file")
            data = stream.read(MAX_BYTES + 1)
    except OSError as error:
        raise ValueError("Artifact file is absent or is not an allowed regular path") from error
    if not 1 <= len(data) <= MAX_BYTES:
        raise ValueError("Artifact bytes exceed the declared budget")
    return data


def commit_file(directory, name, data):
    temporary = directory / (name + ".tmp")
    with temporary.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(directory / name)


def publish_bundle(directory, payload):
    # One trusted writer creates a new immutable version directory. The manifest
    # is committed last; this is not a distributed compare-and-swap protocol.
    directory.mkdir()
    model = encode(payload)
    manifest = {
        "schema_version": 1,
        "model_file": "model.json",
        "model_bytes": len(model),
        "model_sha256": sha256(model),
        "interface_sha256": sha256(encode(INTERFACE)),
    }
    commit_file(directory, "model.json", model)
    commit_file(directory, "manifest.json", encode(manifest))
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return manifest


def number(value):
    if type(value) not in {int, float} or abs(value) > 1_000_000 or not math.isfinite(value):
        raise ValueError("Expected a finite bounded numerical parameter")
    return float(value)


def load_bundle(directory):
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("Use the explicit owned version directory")
    manifest = decode(bounded_read(directory / "manifest.json"))
    required = {"schema_version", "model_file", "model_bytes", "model_sha256", "interface_sha256"}
    if type(manifest) is not dict or set(manifest) != required:
        raise ValueError("Unexpected manifest fields")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise ValueError("Incompatible manifest version")
    if manifest["model_file"] != "model.json":
        raise ValueError("Model path is outside the fixed filename contract")
    if type(manifest["model_bytes"]) is not int or not 1 <= manifest["model_bytes"] <= MAX_BYTES:
        raise ValueError("Invalid declared model size")
    if type(manifest["model_sha256"]) is not str or not re.fullmatch(
        r"[0-9a-f]{64}", manifest["model_sha256"]
    ):
        raise ValueError("Invalid content hash")
    if manifest["interface_sha256"] != sha256(encode(INTERFACE)):
        raise ValueError("Incompatible interface identity")
    data = bounded_read(directory / "model.json")
    if len(data) != manifest["model_bytes"] or sha256(data) != manifest["model_sha256"]:
        raise ValueError("Model byte length or hash mismatch")
    model = decode(data)
    if type(model) is not dict or set(model) != {
        "format_version",
        "feature_names",
        "feature_units",
        "intercept",
        "coefficients",
    }:
        raise ValueError("Unexpected model fields")
    if type(model["format_version"]) is not int or model["format_version"] != 1:
        raise ValueError("Incompatible numerical model format")
    if (
        model["feature_names"] != INTERFACE["features"]
        or model["feature_units"] != INTERFACE["units"]
    ):
        raise ValueError("Feature order or units mismatch")
    coefficients = model["coefficients"]
    if type(coefficients) is not list or len(coefficients) != 2:
        raise ValueError("Model coefficient shape mismatch")
    return {
        "intercept": number(model["intercept"]),
        "coefficients": [number(x) for x in coefficients],
    }


def trained_payload():
    hours = np.arange(1, 9, dtype=float)
    tickets = np.array([0, 1, 2, 1, 0, 2, 1, 2], dtype=float)
    design = np.column_stack([np.ones(8), hours, tickets])
    labels = 3 + 2 * hours - 1.5 * tickets
    weights, _, rank, _ = np.linalg.lstsq(design, labels, rcond=None)
    assert rank == 3
    return {
        "format_version": 1,
        "feature_names": INTERFACE["features"],
        "feature_units": INTERFACE["units"],
        "intercept": float(weights[0]),
        "coefficients": weights[1:].tolist(),
    }


def example_one():
    payload = trained_payload()
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "version-one"
        manifest = publish_bundle(root, payload)
        model = load_bundle(root)
        probe = np.array([[2.0, 0.0], [4.0, 1.0], [8.0, 2.0]])
        restored = probe @ np.array(model["coefficients"]) + model["intercept"]
        expected = 3 + 2 * probe[:, 0] - 1.5 * probe[:, 1]
        error = float(np.max(np.abs(restored - expected)))
        assert np.allclose(restored, expected, rtol=0, atol=1e-10)
        return {
            "model_sha256": manifest["model_sha256"],
            "model_bytes": manifest["model_bytes"],
            "predictions": restored.tolist(),
            "oracle": expected.tolist(),
            "max_absolute_error": error,
            "deserialized_executable_code": False,
        }


def example_two():
    rejected = []
    payload = trained_payload()
    with tempfile.TemporaryDirectory() as temporary:
        parent = Path(temporary)
        changed = parent / "changed-bytes"
        publish_bundle(changed, payload)
        data = bytearray((changed / "model.json").read_bytes())
        position = data.index(b'"intercept":') + len(b'"intercept":')
        data[position] = ord("9") if data[position] != ord("9") else ord("8")
        (changed / "model.json").write_bytes(data)
        wrong_shape = parent / "wrong-shape"
        publish_bundle(wrong_shape, {**payload, "coefficients": [2.0]})
        wrong_order = parent / "wrong-order"
        publish_bundle(wrong_order, {**payload, "feature_names": ["tickets", "hours"]})
        escaping = parent / "escaping-path"
        manifest = publish_bundle(escaping, payload)
        (escaping / "manifest.json").write_bytes(
            encode({**manifest, "model_file": "../model.json"})
        )
        linked = parent / "linked-model"
        publish_bundle(linked, payload)
        (linked / "model.json").unlink()
        external = parent / "external-model.json"
        external.write_bytes(encode(payload))
        # Otherwise-valid target bytes isolate the link-path rejection.
        (linked / "model.json").symlink_to(external)
        alternate = parent / "different-consistent-model"
        publish_bundle(alternate, {**payload, "coefficients": [9.0, -1.5]})
        accepted_alternate = load_bundle(alternate)
        assert accepted_alternate["coefficients"] != payload["coefficients"]
        for name, directory in [
            ("same-length changed bytes", changed),
            ("correct hash wrong shape", wrong_shape),
            ("correct hash wrong feature order", wrong_order),
            ("escaping filename", escaping),
            ("symbolic-link file", linked),
        ]:
            try:
                load_bundle(directory)
            except ValueError:
                rejected.append(name)
            else:
                raise AssertionError("An invalid artifact was accepted: " + name)
    assert len(rejected) == 5
    return {
        "rejected_conditions": rejected,
        "hash_alone_is_not_schema_or_authentication": True,
        "different_consistent_model_accepted_without_external_origin_authentication": True,
    }


def main():
    first, second = example_one(), example_two()
    publish_table(
        ["probe", "restored prediction", "independent linear oracle"],
        [
            [number, predicted, expected]
            for number, (predicted, expected) in enumerate(
                zip(first["predictions"], first["oracle"], strict=True), start=1
            )
        ],
        description="Least-squares predictions restored from strict numerical JSON",
    )
    publish_report(
        {"case_one": first, "case_two": second},
        description="Byte integrity, schema, path and model-shape checks before use",
    )
    print(json.dumps({"case_one": first, "case_two": second}, allow_nan=False))
    print("dme-040: two artifact-integrity cases passed")


if __name__ == "__main__":
    main()
