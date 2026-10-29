"""Detached prepared-model evaluation and fitting in bounded fresh R processes."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from ds60_spark_likelihood.contracts import parameter_digest

from .processes import cleanup_process_group
from .registry import (
    MAX_GROUPS,
    MAX_PARAMETERS,
    MAX_ROWS,
    ModelContractError,
    finite,
    load_registry,
    payload_for,
    prediction_payload,
    sha256,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def verify_prepared(root, build_dir, model_id):
    root, build = Path(root).resolve(strict=True), Path(build_dir).resolve(strict=True)
    registry = load_registry(root)
    if model_id not in registry["models"]:
        raise ModelContractError("Unprepared model identifier")
    receipt = json.loads((build / "receipt.json").read_text())
    if receipt.get("schema_version") != 1 or receipt.get("registry_sha256") != sha256(
        root / "registry.json"
    ):
        raise ModelContractError("Prepared registry receipt differs from installed source")
    record = receipt.get("models", {}).get(model_id, {})
    if record.get("library") != model_id + ".so":
        raise ModelContractError("Compiled library identity differs from registry")
    library = build / record["library"]
    if library.is_symlink() or library.resolve().parent != build:
        raise ModelContractError("Compiled library must remain inside prepared artifact directory")
    if record.get("source_sha256") != sha256(root / registry["models"][model_id]["source"]):
        raise ModelContractError("C++ source changed after preparation")
    if record.get("library_sha256") != sha256(library):
        raise ModelContractError("Compiled library bytes changed after preparation")
    return receipt


def _run(
    model_id,
    data,
    theta,
    *,
    action,
    root=None,
    build_dir=None,
    timeout=45,
    n_rows=None,
    target=None,
):
    if type(timeout) is not int or not 1 <= timeout <= 120:
        raise ModelContractError("Timeout must be bounded within 1..120 seconds")
    root = PROJECT_ROOT if root is None else Path(root)
    build = Path(build_dir or os.environ.get("SPARK_TMB_BUILD_DIR", "/opt/spark-tmb-models"))
    request = (
        prediction_payload(root, model_id, data, theta, n_rows=n_rows, target=target)
        if action == "predict"
        else payload_for(root, model_id, data, theta)
    )
    request["action"] = action
    receipt = verify_prepared(root, build, model_id)
    payload = json.dumps(request, separators=(",", ":"), allow_nan=False).encode()
    if len(payload) > 1_000_000:
        raise ModelContractError("Serialized payload exceeds one megabyte")
    with tempfile.TemporaryDirectory(prefix="prepared-tmb-") as directory:
        temporary = Path(directory)
        request_path = temporary / "request.json"
        request_path.write_bytes(payload)
        with (
            (temporary / "stdout").open("wb") as stdout,
            (temporary / "stderr").open("wb") as stderr,
        ):
            process = subprocess.Popen(
                [
                    "Rscript",
                    "--vanilla",
                    str(root / "R/evaluate_registered.R"),
                    str(root),
                    str(build),
                    str(request_path),
                ],
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
                env={**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"},
            )
            try:
                process.wait(timeout=timeout)
            finally:
                cleanup_process_group(process)
        if process.returncode:
            detail = (temporary / "stderr").read_bytes()[:4096].decode(errors="replace")
            raise ModelContractError(f"Prepared model failed ({process.returncode}): {detail}")
        if (temporary / "stdout").stat().st_size > 1_000_000:
            raise ModelContractError("Prepared model response exceeds one megabyte")
        try:
            response = json.loads((temporary / "stdout").read_text())
        except (ValueError, UnicodeError) as exc:
            raise ModelContractError("Prepared model returned invalid JSON") from exc
    specification = load_registry(root)["models"][model_id]
    if (
        response.get("schema_version") != 1
        or response.get("model_id") != model_id
        or response.get("parameter_names") != specification["fixed_parameters"]
        or response.get("nobs")
        != (n_rows if action == "predict" else len(request["data"][specification["response"]]))
        or response.get("abi") != receipt["abi"]
    ):
        raise ModelContractError("Prepared model response identity differs")
    response["parameter_digest_input"] = parameter_digest(theta)
    response["artifact_source_sha256"] = receipt["models"][model_id]["source_sha256"]
    response["artifact_library_sha256"] = receipt["models"][model_id]["library_sha256"]
    response["artifact_registry_sha256"] = receipt["registry_sha256"]
    if action == "predict":
        values = response.get("prediction")
        if (
            not isinstance(values, list)
            or len(values) != n_rows
            or response.get("target") != specification["prediction"]["target"]
        ):
            raise ModelContractError("Prediction shape or target differs from the declared report")
        response["prediction"] = [finite(value) for value in values]
    else:
        response["value"] = finite(response["value"])
        gradient = response.get("gradient")
        if not isinstance(gradient, list) or len(gradient) != len(theta):
            raise ModelContractError("Prepared gradient layout differs")
        response["gradient"] = [finite(value) for value in gradient]
    if action == "fit":
        fitted = response.get("fitted_parameters")
        if not isinstance(fitted, list) or len(fitted) != len(theta):
            raise ModelContractError("Fitted parameter layout differs")
        response["fitted_parameters"] = [finite(value) for value in fitted]
        if response.get("convergence") != 0 or max(map(abs, response["gradient"])) > 1e-4:
            raise ModelContractError(
                "Independent fit rejected: optimizer status="
                + str(response.get("convergence"))
                + ", gradient_max="
                + str(max(map(abs, response["gradient"])))
                + ", message="
                + str(response.get("optimizer_message", "unavailable"))
            )
    return response


def evaluate_prepared(model_id, data, theta, **options):
    """Evaluate one registered row or complete-group likelihood at fixed parameters."""
    return _run(model_id, data, theta, action="evaluate", **options)


def fit_prepared(model_id, data, initial, **options):
    """One independent fit, bounded nlminb with score checking; never pooled by averaging."""
    return _run(model_id, data, initial, action="fit", **options)


def describe_prepared(model_id, *, root=None, build_dir=None):
    """Return the one authoritative normalized schema and verified artifact identity."""
    root = PROJECT_ROOT if root is None else Path(root)
    build = Path(build_dir or os.environ.get("SPARK_TMB_BUILD_DIR", "/opt/spark-tmb-models"))
    config = load_registry(root)
    receipt = verify_prepared(root, build, model_id)
    artifact = receipt["models"][model_id]
    return {
        "spec": config["models"][model_id],
        "max_rows": MAX_ROWS,
        "max_parameters": MAX_PARAMETERS,
        "max_groups": MAX_GROUPS,
        "prepared": {
            "source_sha256": artifact["source_sha256"],
            "library_sha256": artifact["library_sha256"],
            "registry_sha256": receipt["registry_sha256"],
            "abi": receipt["abi"],
        },
    }


def predict_prepared(model_id, data, parameters, *, n_rows, target=None, **options):
    """Return only the model's declared response-free point prediction report."""
    return _run(
        model_id, data, parameters, action="predict", n_rows=n_rows, target=target, **options
    )
