"""Compare response-free held-out scores from two committed MLP checkpoints."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from service import _prepare_python

SHARED = Path("/shared")
FEATURES = [[1.0, -0.25], [1.0, 0.75], [1.0, 1.25]]


def _load(reference: dict):
    from ds60_torch_training import checkpoint

    path = Path(reference["path"])
    manifest = json.loads((path / "manifest.json").read_text())
    return checkpoint.load_rank(
        path,
        expected_binding=manifest["binding"],
        expected_manifest_digest=reference["manifest_digest"],
        rank=0,
    )


def _predict(loaded) -> list[float]:
    import numpy as np
    import torch
    from ds60_torch_training._integration_fixture import gated_mlp_model
    from ds60_torch_training.training_examples import mlp_adam_example

    program = mlp_adam_example()
    model = gated_mlp_model(program.configuration["model"])
    state = {}
    for name, item in loaded.state["model"].items():
        if item.dtype != "float64":
            raise RuntimeError("Held-out control expects float64 model state")
        value = np.frombuffer(item.data, dtype="<f8").copy().reshape(item.shape)
        state[name] = torch.from_numpy(value)
    model.load_state_dict(state, strict=True)
    model.eval()
    with torch.no_grad():
        scores = model(torch.tensor(FEATURES, dtype=torch.float64)).reshape(-1)
        return [float(item) for item in torch.sigmoid(scores)]


def main() -> None:
    _prepare_python()
    sys.path.insert(0, "/work/python")
    reference = json.loads((SHARED / "reference-report.json").read_text())["latest_checkpoint"]
    resumed = json.loads((SHARED / "resume-report.json").read_text())["latest_checkpoint"]
    left, right = _load(reference), _load(resumed)
    if left.binding != right.binding or left.state["model"] != right.state["model"]:
        raise RuntimeError("Held-out checkpoint model/source identity differs")
    values = _predict(left)
    recovered = _predict(right)
    if values != recovered or len(values) != len(FEATURES):
        raise RuntimeError("Held-out response-free predictions differ")
    result = {
        "schema_version": 1,
        "kind": "ds60-torch-heldout-prediction-followup",
        "status": "passed",
        "scope": "local CPU inference from two committed training checkpoints",
        "conditioning": (
            "fixed response-free feature rows, binary sigmoid score, eval mode, float64"
        ),
        "feature_names": ["x0", "x1"],
        "features": FEATURES,
        "reference_manifest_digest": reference["manifest_digest"],
        "resumed_manifest_digest": resumed["manifest_digest"],
        "binding": left.binding,
        "probabilities": values,
        "exact_prediction_equality": True,
    }
    raw = json.dumps(result, sort_keys=True, allow_nan=False).encode() + b"\n"
    if len(raw) > 65536:
        raise RuntimeError("Prediction follow-up receipt exceeds bound")
    with (SHARED / "prediction-followup.json").open("xb") as stream:
        stream.write(raw)


if __name__ == "__main__":
    main()
